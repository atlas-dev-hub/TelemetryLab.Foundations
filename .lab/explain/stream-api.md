title: The Stream API, and why producers never write to Kafka
proto: api:PacketWriterService api:SessionManagementService
code: producer/atlas_lab/writer.py  (connect)
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/getting-started/overview/
source: https://github.com/Software-Products/MA.DataPlatforms.StreamApi
---
## What sits where

    your producer  --gRPC-->  Stream API  --writes-->  Kafka  --reads-->  consumers

The Stream API is a router with a memory. It registers sessions, holds the
data-format registry, decides which topic and partition each packet belongs on,
mirrors essential packets to a second topic, and emits `StreamStarted` markers
when it sees a new stream. What it does not do is inspect your payloads.

Five gRPC services, each with one job:

- **SessionManagement** — create, end, look up and annotate sessions
- **PacketWriter** — write packets, singly or in batches
- **PacketReader** — read them back, including the essentials replay
- **DataFormatManager** — the id-to-parameter-list registry
- **ConnectionManager** — connection lifecycle for readers

## Why not just produce to Kafka directly

You can. The bytes will land. Nothing will be able to read them.

A consumer needs the session to exist, the data-format id to resolve, and the
packet to be on the topic it is subscribed to. Write straight to a topic and
you have skipped all three: you have a partition full of anonymous byte arrays
that no ATLAS tool, and no consumer written against this protocol, can
interpret.

Kafka is the transport. The Stream API is the contract.

## It writes what you give it

Worth being blunt about, because it shapes how you debug: the write path takes
your packet, works out a route, writes it, and catches its own exceptions into
the server log. It does not validate your configuration, count your groups, or
check that the session key you sent is one it issued.

The only packet it will refuse is a second `StreamStarted` for a stream that
already started.

So when something is wrong, the producer is usually not the place the evidence
is. Read the Stream API container's logs, then check the consumer, then check
`System.DeadLetter`.

## The Key Generator

The third container. It hands out unique ids for sessions and data formats, so
two producers on the same broker cannot collide. `UseRemoteKeyGenerator` in the
server config switches between the in-process generator and this service, and
it is off by default — worth knowing if you are ever tracing where an id came
from.

## In the wild

Adding a new source means writing a producer against `PacketWriter`, not a
Kafka client. The compose file in this repository is a working three-service
reference; the images are public and need no licence.
