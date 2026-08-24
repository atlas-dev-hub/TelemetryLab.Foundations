/**
 * Read the telemetry back out of Kafka.
 *
 * This is the second consumer on the same stream. The producer does not know
 * it exists, ATLAS does not know it exists, and neither has to change for it to
 * work - that decoupling is the point of putting a broker in the middle.
 *
 * Three packet types do all the work:
 *
 *   Configuration        what the channels are: identity, units, rate, range
 *   DataFormatDefinition which format id maps to which parameter
 *   PeriodicData         the samples themselves, one parameter per packet
 *
 * You need the first two before the third means anything. A consumer that
 * joins mid-session and only sees PeriodicData has a stream of numbers with no
 * idea what any of them are - which is what step 6 makes you experience.
 */
import kafkajs from 'kafkajs';
import ZstdCodec from '@kafkajs/zstd';
import protobuf from 'protobufjs';
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const { Kafka, logLevel, CompressionTypes, CompressionCodecs } = kafkajs;

// The Stream API publishes zstd-compressed record batches. kafkajs ships gzip
// only. Without this line it connects happily, reports topic offsets happily,
// and then delivers zero messages while throwing "ZSTD compression not
// implemented" - which reads like a subscription bug and is not one.
CompressionCodecs[CompressionTypes.ZSTD] = ZstdCodec();

const here = dirname(fileURLToPath(import.meta.url));
const proto = await protobuf.load(
  join(here, '..', 'proto', 'ma', 'streaming', 'open_data', 'v1', 'open_data.proto'),
);
const T = (n) => proto.lookupType(`ma.streaming.open_data.v1.${n}`);
const Packet = T('Packet');
const ConfigurationPacket = T('ConfigurationPacket');
const DataFormatDefinitionPacket = T('DataFormatDefinitionPacket');
const PeriodicDataPacket = T('PeriodicDataPacket');
const MarkerPacket = T('MarkerPacket');

const BOOTSTRAP = process.env.KAFKA_BOOTSTRAP ?? 'localhost:9092';
const DATA_TOPIC = 'Data.Default.Stream1';
const ESSENTIALS_TOPIC = 'Essentials.Default';
const SETTLE_MS = Number(process.env.SETTLE_MS ?? 8000);

/** parameter identifier -> { units, description, min, max, frequency } */
const parameters = new Map();
/** data format id (as string) -> parameter identifier */
const formatToParameter = new Map();
/** parameter identifier -> { count, min, max, sum, first, last } */
const stats = new Map();
const markers = [];
let sessionCount = 0;
let unresolved = 0;
/** [timestampNs, value] for whichever channel is the speed one. */
const speedSeries = [];

/** The speed channel's identifier, whatever application it came from. */
function speedChannel() {
  for (const id of parameters.keys()) if (id.startsWith('Speed:')) return id;
  return null;
}

function noteSample(identifier, value) {
  let s = stats.get(identifier);
  if (!s) {
    s = { count: 0, min: Infinity, max: -Infinity, sum: 0 };
    stats.set(identifier, s);
  }
  s.count++;
  s.sum += value;
  if (value < s.min) s.min = value;
  if (value > s.max) s.max = value;
}

function handle(packet) {
  switch (packet.type) {
    case 'Configuration': {
      const c = ConfigurationPacket.decode(packet.content);
      for (const p of c.parameterDefinitions ?? []) {
        parameters.set(p.identifier, {
          name: p.name,
          units: p.units,
          description: p.description,
          min: p.minValue,
          max: p.maxValue,
          frequency: (p.frequencies ?? [])[0],
        });
      }
      break;
    }
    case 'DataFormatDefinition': {
      const d = DataFormatDefinitionPacket.decode(packet.content);
      const ids = d.parameterIdentifiers?.parameterIdentifiers ?? [];
      // One parameter per format id - see the producer's rule 2.
      if (ids.length > 0) formatToParameter.set(String(d.identifier), ids[0]);
      break;
    }
    case 'PeriodicData': {
      const p = PeriodicDataPacket.decode(packet.content);
      const formatId = String(p.dataFormat?.dataFormatIdentifier ?? '');
      const identifier =
        formatToParameter.get(formatId) ??
        p.dataFormat?.parameterIdentifiers?.parameterIdentifiers?.[0];
      if (!identifier) {
        unresolved++; // format not yet seen - a late joiner's problem
        return;
      }
      // A periodic packet carries a start time and a fixed interval rather
      // than a timestamp per sample. That is the whole point of "periodic":
      // for evenly spaced data it is a large saving, and the timestamps are
      // reconstructable exactly rather than approximately.
      const start = Number(p.startTime ?? 0);
      const interval = Number(p.interval ?? 0);
      let i = 0;
      for (const col of p.columns ?? []) {
        for (const s of col.doubleSamples?.samples ?? []) {
          noteSample(identifier, s.value);
          if (identifier === speedChannel() && interval > 0) {
            speedSeries.push([start + i * interval, s.value]);
          }
          i++;
        }
      }
      break;
    }
    case 'Marker': {
      const m = MarkerPacket.decode(packet.content);
      markers.push({
        label: m.label,
        type: m.type,
        timestamp: m.timestamp,
        sessionKey: packet.sessionKey,
      });
      break;
    }
    case 'NewSession':
      sessionCount++;
      break;
    default:
      break;
  }
}

const kafka = new Kafka({ clientId: 'atlas-lab-consumer', brokers: [BOOTSTRAP], logLevel: logLevel.WARN });

/** Drain one topic from the beginning, then stop. */
async function drain(topic, settleMs) {
  const consumer = kafka.consumer({ groupId: `atlas-lab-consumer-${topic}-${Date.now()}` });
  await consumer.connect();
  await consumer.subscribe({ topic, fromBeginning: true });
  let decodeErrors = 0;
  await consumer.run({
    eachMessage: async ({ message }) => {
      let packet;
      try {
        packet = Packet.decode(message.value);
      } catch {
        return; // not every message on a topic is ours to understand
      }
      try {
        handle(packet);
      } catch (e) {
        // Never swallow this silently. A decode failure that looks like
        // "no data arrived" is the hardest kind of bug to find.
        if (decodeErrors++ < 3) console.warn(`  ! ${packet.type}: ${e.message}`);
      }
    },
  });
  await new Promise((r) => setTimeout(r, settleMs));
  await consumer.disconnect();
}

console.log(`Connecting to Kafka at ${BOOTSTRAP} ...`);

// Two passes, and the order is not optional.
//
// The format-id -> parameter mapping arrives on Essentials.Default; the samples
// arrive on Data.Default.Stream1. Kafka guarantees ordering *within* a
// partition, not *across topics* - so subscribing to both at once and hoping
// lets thousands of data messages arrive before the handful of definitions that
// give them meaning, and every one of them gets discarded.
//
// Reading configuration to completion first is what a real consumer must do,
// and it is the same problem a consumer that joins mid-session has. Step 6
// makes you meet it deliberately.
console.log(`Pass 1: reading configuration from ${ESSENTIALS_TOPIC} ...`);
await drain(ESSENTIALS_TOPIC, Math.min(SETTLE_MS, 5000));
console.log(`  ${parameters.size} parameters, ${formatToParameter.size} data formats resolved.`);

console.log(`Pass 2: reading telemetry from ${DATA_TOPIC} ...\n`);
await drain(DATA_TOPIC, SETTLE_MS);

// --- report -----------------------------------------------------------------

const recovered = [...stats.entries()].sort((a, b) => a[0].localeCompare(b[0]));
const totalSamples = recovered.reduce((a, [, s]) => a + s.count, 0);

console.log(`Sessions seen        : ${sessionCount}`);
console.log(`Parameters defined   : ${parameters.size}`);
console.log(`Data formats mapped  : ${formatToParameter.size}`);
console.log(`Channels with data   : ${recovered.length}`);
console.log(`Samples recovered    : ${totalSamples}`);
console.log(`Markers              : ${markers.length}`);
console.log();

if (recovered.length === 0) {
  console.log('No telemetry found. Run the producer first:');
  console.log('  cd producer && python produce.py --laps 1');
  process.exit(1);
}

const w = Math.max(...recovered.map(([id]) => id.length));
console.log('  ' + 'channel'.padEnd(w) + '  ' + 'units'.padEnd(6) + '  samples      min      max     mean');
console.log('  ' + '-'.repeat(w + 46));
for (const [id, s] of recovered) {
  const meta = parameters.get(id) ?? {};
  console.log(
    '  ' +
      id.padEnd(w) +
      '  ' +
      String(meta.units ?? '').padEnd(6) +
      '  ' +
      String(s.count).padStart(7) +
      '  ' +
      s.min.toFixed(2).padStart(7) +
      '  ' +
      s.max.toFixed(2).padStart(7) +
      '  ' +
      (s.sum / s.count).toFixed(2).padStart(7),
  );
}

// Only the most recent session. The topic accumulates every session ever
// produced, so aggregating across all of them silently mixes runs - which is
// exactly the mistake a first consumer makes, and it produces lap "times" that
// are the gap between two unrelated sessions. Every packet carries its session
// key precisely so this is avoidable.
const latestSession = markers.length ? markers[markers.length - 1].sessionKey : null;
const laps = markers.filter(
  (m) => m.type === 'Lap Trigger' && (!latestSession || m.sessionKey === latestSession),
);
if (laps.length) {
  console.log(`\n  Lap markers (latest session): ${laps.map((m) => m.label).join(', ')}`);
}

// Per-lap breakdown. The markers are what make this possible - a bare topic has
// no concept of a lap, so on a generic stack this is where you would start
// maintaining your own table of "interesting timestamps" alongside the data.
if (laps.length >= 2 && speedSeries.length > 0) {
  speedSeries.sort((a, b) => a[0] - b[0]);
  const bounds = laps.map((m) => Number(m.timestamp)).sort((a, b) => a - b);
  console.log('\n  lap        time    samples   top speed   avg speed');
  console.log('  ' + '-'.repeat(50));
  for (let i = 0; i < bounds.length - 1; i++) {
    const [from, to] = [bounds[i], bounds[i + 1]];
    const inLap = speedSeries.filter(([t]) => t >= from && t < to);
    if (inLap.length === 0) continue;
    const top = Math.max(...inLap.map(([, v]) => v));
    const avg = inLap.reduce((a, [, v]) => a + v, 0) / inLap.length;
    console.log(
      '  ' +
        String(i + 1).padEnd(5) +
        (((to - from) / 1e9).toFixed(3) + 's').padStart(9) +
        String(inLap.length).padStart(11) +
        (top * 3.6).toFixed(1).padStart(12) +
        (avg * 3.6).toFixed(1).padStart(12) +
        '  km/h',
    );
  }
}

if (unresolved > 0) {
  console.log(
    `\n  ${unresolved} packets could not be resolved to a parameter - their data\n` +
      `  format was never seen. That is what a late joiner experiences (step 6).`,
  );
}

// The units, ranges and channel names above did not come from this file. They
// arrived with the data, in the configuration packet. That is the difference
// between a telemetry platform and a topic full of numbers.
console.log(
  `\n  Every channel above arrived with its own identity and units - none of that\n` +
    `  is hardcoded in the consumer. That is what the Configuration packet buys you.`,
);

writeFileSync(
  join(here, '..', '..', '.lab', '.consumed'),
  JSON.stringify({
    channels: recovered.map(([id]) => id),
    samples: totalSamples,
    lapMarkers: laps.length,
    unresolved,
  }),
  'utf-8',
);

console.log('\nNext: lab/04-add-a-channel.md');
process.exit(0);
