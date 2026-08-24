/**
 * A zstd codec for kafkajs, built on Node's own zlib.
 *
 * The ATLAS Stream API publishes zstd-compressed record batches. kafkajs ships
 * gzip and snappy only, so without a codec it connects, reports topic offsets
 * correctly, and then delivers nothing while throwing "ZSTD compression not
 * implemented" — which reads like a subscription bug and is not one.
 *
 * The obvious fix is `@kafkajs/zstd`, and it is the wrong one for a lab: it
 * pulls in `cppzst`, a native module that needs node-gyp and a working C++
 * toolchain. It builds on some machines and not others, which turns
 * `npm install` into a coin flip for a learner whose actual goal is telemetry.
 *
 * Node has had zstd in `node:zlib` since 22.15, so there is no reason to
 * compile anything. No native dependency, no build tools, works anywhere Node
 * runs.
 */
import { zstdCompressSync, zstdDecompressSync } from 'node:zlib';

if (typeof zstdDecompressSync !== 'function') {
  throw new Error(
    'This Node build has no zstd support in node:zlib. Node 22.15 or later is required — ' +
      `this is ${process.version}.`,
  );
}

/**
 * Register this **uncalled**:
 *
 *     CompressionCodecs[CompressionTypes.ZSTD] = zstdCodec
 *
 * kafkajs stores a factory and calls it each time it needs a codec, so the
 * value in the table has to be a function. Assigning the codec object itself
 * fails at decode time with "codec is not a function" — long after connecting
 * and reporting offsets successfully, which makes it look like a broker problem
 * rather than a one-line registration mistake.
 */
export default function zstdCodec() {
  return {
    async compress(encoder) {
      return zstdCompressSync(encoder.buffer);
    },
    async decompress(buffer) {
      return zstdDecompressSync(buffer);
    },
  };
}
