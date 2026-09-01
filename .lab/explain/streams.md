title: Streams, topics and what "essential" means
proto: open_data:Packet open_data:StreamStartedPacket
code: producer/atlas_lab/writer.py  (_write)
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/configuration/server-config/
source: https://github.com/Software-Products/MA.DataPlatforms.StreamApi
---
## The topics, as the router actually builds them

    <domain>.Data.<dataSource>              main stream - no suffix
    <domain>.Data.<dataSource>.<stream>     a named stream, topic-based only
    <domain>.Essentials.<dataSource>
    <domain>.System.SessionInfo
    <domain>.System.Status
    <domain>.System.DeadLetter

The domain prefix is optional; leave the domain empty and the names start at
`Data.`. Note that the **main stream has no suffix** — it is not
`Data.Default.Main`, it is `Data.Default`. An empty stream name means the main
stream, deliberately, and is not a missing value.

`System.DeadLetter` is where packets go when routing fails. If data has
disappeared and the producer reported success, look there before anywhere else.

## Two ways to split a stream

`StreamCreationStrategy` decides what a "stream" physically is:

- **PartitionBased** — every stream is a partition of the one data topic.
  Fewer topics, ordering guaranteed within a partition, and the set of valid
  streams is fixed up front by the partition mapping in the server config.
- **TopicBased** — every stream is its own topic. Add streams at runtime, and
  a consumer subscribes to exactly the ones it wants.

Under PartitionBased, a stream name that is not in the configured mapping is
silently treated as the main stream. If your named stream keeps ending up in
the main topic, that is why — check the server's partition mappings.

The official example splits by subsystem, `Stream = "engine"` and so on, so a
consumer that only cares about engine data does not pay for position data.

## Essential

`is_essential` is a flag **you set on the packet**. The server does not infer
it. When it is set, the packet is written to the Essentials topic *and* the
normal data topic — both, not one or the other.

That is the answer to consumers that start late. The data topic is a firehose
you join at the end; the Essentials topic is short and replayable from the
beginning, so a consumer connecting mid-session can recover context and then
start decoding samples.

In the official example: configuration is `IsEssential = true`; periodic data,
row data and events are all `false`. That is the line — context yes, samples no.

## In the wild

Decide by asking: **could a consumer that joined just now do its job without
this packet?** Configuration, no. A single sample, yes.

Get that wrong in the generous direction and you replay the entire session to
every consumer that reconnects, which turns a small topic into a second copy of
the big one.
