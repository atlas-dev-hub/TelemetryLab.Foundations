title: The Stream API, and why producers never write to Kafka
proto: api:PacketWriterService api:SessionManagementService
code: producer/atlas_lab/writer.py  (connect)
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/getting-started/overview/
---
## What sits where

    your producer  --gRPC-->  Stream API  --writes-->  Kafka  --reads-->  consumers

The Stream API is not a proxy. It is the thing that turns a stream of numbers
into telemetry: it registers the session, holds the configuration describing
each channel, allocates the data-format ids that samples refer to, and decides
which topic and partition a packet belongs on.

Five gRPC services, each with one job:

- **SessionManagement** — create, end, look up and annotate sessions
- **PacketWriter** — write packets, singly or in batches
- **PacketReader** — read them back, including the essentials replay
- **DataFormatManager** — the id-to-parameter-list mapping
- **ConnectionManager** — connection lifecycle for readers

## Why not just produce to Kafka directly

You can. The bytes will land. Nothing will be able to read them.

A consumer needs the session to exist, the configuration to be registered, and
a data-format id to resolve. Write straight to the topic and you have skipped
all three: you have a topic full of anonymous byte arrays that no ATLAS tool,
and no consumer written against the protocol, can interpret.

The rule of thumb: **Kafka is the transport, the Stream API is the contract.**

## The Key Generator

The third container. It hands out unique ids for sessions and configurations,
so two producers writing to the same broker cannot collide. It exists because
"generate a unique id" is exactly the sort of thing every integrator would
otherwise re-implement slightly differently.

## In the wild

If you are adding a new source, you are writing a producer against
PacketWriter — not a Kafka client. The compose file in this repository is a
working reference for the three services; the images are public and need no
licence.
