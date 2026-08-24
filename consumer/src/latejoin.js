/**
 * A consumer that joins late.
 *
 * It reads only the data topic. It never reads configuration - exactly like a
 * consumer that connects to a session already in progress, because
 * configuration is sent once, at the start, and is not resent.
 *
 * The result is the failure mode worth feeling rather than reading about:
 * thousands of samples arrive, nothing errors, and not one of them can be
 * turned into a channel name, let alone a unit.
 */
import kafkajs from 'kafkajs';
import ZstdCodec from '@kafkajs/zstd';
import protobuf from 'protobufjs';
import { writeFileSync, existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const { Kafka, logLevel, CompressionTypes, CompressionCodecs } = kafkajs;
CompressionCodecs[CompressionTypes.ZSTD] = ZstdCodec();

const here = dirname(fileURLToPath(import.meta.url));
const proto = await protobuf.load(
  join(here, '..', 'proto', 'ma', 'streaming', 'open_data', 'v1', 'open_data.proto'),
);
const Packet = proto.lookupType('ma.streaming.open_data.v1.Packet');
const PeriodicDataPacket = proto.lookupType('ma.streaming.open_data.v1.PeriodicDataPacket');

const BOOTSTRAP = process.env.KAFKA_BOOTSTRAP ?? 'localhost:9092';
const kafka = new Kafka({ clientId: 'lab-latejoin', brokers: [BOOTSTRAP], logLevel: logLevel.WARN });
const consumer = kafka.consumer({ groupId: `lab-latejoin-${Date.now()}` });

console.log('Joining the stream WITHOUT reading configuration first...\n');
await consumer.connect();
await consumer.subscribe({ topic: 'Data.Default.Stream1', fromBeginning: true });

let samples = 0;
let unresolved = 0;
const unknownFormats = new Set();

await consumer.run({
  eachMessage: async ({ message }) => {
    let packet;
    try {
      packet = Packet.decode(message.value);
    } catch {
      return;
    }
    if (packet.type !== 'PeriodicData') return;
    const p = PeriodicDataPacket.decode(packet.content);
    const formatId = String(p.dataFormat?.dataFormatIdentifier ?? '');
    // There is no map to look this up in. That is the whole point.
    unknownFormats.add(formatId);
    for (const col of p.columns ?? []) {
      const n = col.doubleSamples?.samples?.length ?? 0;
      samples += n;
      unresolved += n;
    }
  },
});

await new Promise((r) => setTimeout(r, Number(process.env.SETTLE_MS ?? 8000)));
await consumer.disconnect();

console.log(`Samples seen            : ${samples}`);
console.log(`Samples understood      : ${samples - unresolved}`);
console.log(`Distinct format ids     : ${unknownFormats.size}, none of which mean anything here`);
console.log();
console.log('  No error was raised. The data arrived perfectly and is unusable.');
console.log('  Configuration was sent once, at the start of the session, and this');
console.log('  consumer was not listening then.');
console.log();
console.log('  Now run `npm start`, which reads configuration first, and compare.');

const evidence = join(here, '..', '..', 'lab', '.broken');
let done = {};
if (existsSync(evidence)) {
  try {
    done = JSON.parse(readFileSync(evidence, 'utf-8'));
  } catch {
    done = {};
  }
}
done['late-join'] = `${samples} samples seen, ${unresolved} unresolvable`;
writeFileSync(evidence, JSON.stringify(done, null, 1), 'utf-8');
process.exit(0);
