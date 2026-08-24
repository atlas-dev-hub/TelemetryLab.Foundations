// Diagnostic: what is actually on the topics?
//
// Written against reality rather than against the .proto file's suggestions -
// the consumer needs to know which packet types really arrive and how a
// data-format id can be resolved back to a parameter.
import kafkajs from 'kafkajs';
import zstdCodec from './zstd.js';

const { Kafka, logLevel, CompressionTypes, CompressionCodecs } = kafkajs;
import protobuf from 'protobufjs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const root = await protobuf.load(
  join(here, '..', 'proto', 'ma', 'streaming', 'open_data', 'v1', 'open_data.proto'),
);
const Packet = root.lookupType('ma.streaming.open_data.v1.Packet');

// The Stream API publishes zstd-compressed record batches. kafkajs ships
// gzip only, and without this it fails with "ZSTD compression not
// implemented" - after successfully connecting and reporting topic offsets,
// which makes it look like a subscription problem rather than a codec one.
CompressionCodecs[CompressionTypes.ZSTD] = zstdCodec;

const brokers = [process.env.KAFKA_BOOTSTRAP ?? 'localhost:9092'];
const kafka = new Kafka({ clientId: 'lab-probe', brokers, logLevel: logLevel.WARN });

const admin = kafka.admin();
await admin.connect();
const topics = await admin.listTopics();
console.log('topics:', topics.filter((t) => !t.startsWith('__')).join(', '));
const offsets = {};
for (const t of topics.filter((t) => !t.startsWith('__'))) {
  const o = await admin.fetchTopicOffsets(t);
  offsets[t] = o.reduce((a, p) => a + Number(p.high) - Number(p.low), 0);
}
console.log('counts:', JSON.stringify(offsets));
await admin.disconnect();

const consumer = kafka.consumer({ groupId: `lab-probe-${Date.now()}` });
await consumer.connect();
for (const t of ['Essentials.Default', 'Data.Default.Stream1', 'Data.Default', 'System.SessionInfo']) {
  if (topics.includes(t)) await consumer.subscribe({ topic: t, fromBeginning: true });
}

let raw = 0;
const seen = new Map();
await consumer.run({
  eachMessage: async ({ topic, message }) => {
    raw++;
    let type = '(undecodable)';
    try {
      type = Packet.decode(message.value).type || '(empty type)';
    } catch {
      /* not a Packet wrapper */
    }
    const k = `${topic} :: ${type}`;
    seen.set(k, (seen.get(k) ?? 0) + 1);
  },
});

await new Promise((r) => setTimeout(r, 20000));
console.log(`\nraw messages received: ${raw}\n`);
for (const [k, v] of [...seen.entries()].sort()) console.log(`  ${String(v).padStart(6)}  ${k}`);
await consumer.disconnect();
process.exit(0);
