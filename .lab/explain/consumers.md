title: Writing a consumer that survives
proto: open_data:Packet api:PacketReaderService
code: consumer/src/consume.js
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/services/packet-reader/
---
## The shape of one

A consumer is a loop over packets that does four things:

1. **Read essentials first** — configuration and data-format packets, so the
   mapping from id to parameter names exists before any sample arrives.
2. **Decode by type** — read Packet.type, decode content as that message, and
   skip the types you do not handle.
3. **Resolve the format** — use data_format_id to find which parameter each
   column of a sample list belongs to.
4. **Expand time** — one start timestamp plus an interval becomes n sample
   timestamps.

## Where consumers go wrong

- **Hardcoding the channel list.** It works until the producer adds one. Module
  4 grades against a channel invented on the run, precisely so this fails.
- **Reading data before essentials.** You get samples you cannot name.
- **Using floats for timestamps.** Nanosecond epoch values exceed the safe
  integer range of a double, so gaps quietly round away.
- **Throwing on an unknown packet type.** A stream you do not own will grow new
  types; treat them as skippable.
- **Assuming one session.** A topic can carry interleaved sessions. Filter on
  the session key, or you will average two cars together.

## Compression

Batches are zstd-compressed on the Kafka side. Node has this built in from
22.15 (node:zlib), so the reference consumer needs no native dependency — which
matters more than it sounds, because a consumer that needs a compiler is a
consumer that fails on somebody else's CI runner.

## In the wild

Write it so it can be started at any moment and still be correct. That single
constraint forces essentials-first, id resolution and session filtering — and
those are the three things that make a consumer work in production rather than
only against a file you already have.
