# Your consumer

Module 4. Write this yourself, in whatever language you like.

## What it has to do

Read the telemetry back out of Kafka and write **`.lab/my-consumer.json`**
describing what you found:

```json
{
  "sessionIdentifier": "Sandbourne Park - yourhandle - reference - 14:02:11",
  "channels": [
    { "identifier": "Speed:SandbourneGT3", "units": "m/s", "samples": 4278 },
    { "identifier": "Throttle:SandbourneGT3", "units": "%", "samples": 4278 }
  ],
  "lapMarkers": 3
}
```

| Field | Where it comes from |
|---|---|
| `sessionIdentifier` | `System.SessionInfo` → `NewSession` → `session_info.identifier` |
| `channels[].identifier` | `ConfigurationPacket` → `parameter_definitions[].identifier` |
| `channels[].units` | the same place — **not** hardcoded in your consumer |
| `channels[].samples` | how many samples you actually decoded for that channel |
| `lapMarkers` | `MarkerPacket` where `type` is `Lap Trigger` |

Order does not matter. Extra fields are ignored.

## How it gets run

The validator runs:

```bash
bash my-consumer/run.sh
```

from the repository root, with `KAFKA_BOOTSTRAP` set in the environment
(`localhost:9092` locally). Make `run.sh` do whatever your language needs —
compile, install, execute. It must exit 0 and leave the JSON file behind.

## What you will need

**The broker.** Three topics matter, and you need all three:

| Topic | Carries |
|---|---|
| `Data.Default.Stream1` | the samples, and lap markers |
| `Essentials.Default` | configuration and data-format definitions |
| `System.SessionInfo` | session lifecycle — **and the session identifier** |

Topics follow `<Domain>.<DataSource>.<Stream>`.

Note the third one. The producer writes a bare `NewSessionPacket` to the data
stream; the *identifier* only appears in the enriched copy the Stream API
publishes to `System.SessionInfo`. Looking for it on the data stream is a
reasonable guess and it will not work.

**The schema.** [`consumer/proto/ma/streaming/open_data/v1/open_data.proto`](../consumer/proto/ma/streaming/open_data/v1/open_data.proto)
defines every packet. Every Kafka message is a `Packet` whose `type` field names
what is inside `content`.

**Four packet types do all the work:**

| Type | Carries |
|---|---|
| `Configuration` | parameter definitions — identity, units, rate, range |
| `DataFormatDefinition` | which data-format id maps to which parameter |
| `PeriodicData` | the samples: a start time, an interval, and one column |
| `Marker` | timestamped events, including laps |

## Three things that will catch you out

These are not hypothetical — every one of them cost us time building the
reference consumer in [`consumer/`](../consumer/).

**1. The stream is zstd-compressed.** Most Kafka clients ship gzip and snappy
only. If yours connects, reports topic offsets correctly, and then delivers
nothing, this is why. It rarely presents as a compression error.

**2. Configuration and data are on different topics, and Kafka does not order
across topics.** Subscribe to both at once and thousands of data messages can
arrive before the handful of definitions that give them meaning. Read
configuration to completion first, or buffer what you cannot yet resolve.

**3. `PeriodicData` has no timestamp per sample.** It has a start time and an
interval; you reconstruct the rest. In JavaScript those nanosecond values exceed
`Number.MAX_SAFE_INTEGER` and need BigInt — a double quantises them to 256 ns
steps.

## Rules

- **Do not import the reference consumer.** Reading it is fine and encouraged.
  Calling it is not — the validator is checking that *you* can decode the stream.
- **Do not hardcode.** The validator varies the stream between runs: a different
  number of laps, and an extra channel whose name and units it invents. A
  consumer that assumes eleven channels will fail.
- Any language. Any Kafka client. Any protobuf library.
