title: Streams, topics and what "essential" means
proto: open_data:Packet open_data:StreamStartedPacket
code: producer/atlas_lab/writer.py  (_write)
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/configuration/server-config/
---
## Topic naming

Topics are named from the data rather than chosen by hand:

    <Domain>.<DataSource>.<Stream>       Data.Default.Stream1
    <Domain>.<DataSource>                Essentials.Default
    System.SessionInfo

A **stream** is a lane within a data source. Splitting high-rate car data from
low-rate strategy data means a consumer can subscribe to one and not pay for
the other, and a slow consumer on one lane cannot hold up the other.

The empty string is the *main* stream — not a missing value. That catches
people out; it is deliberate, and the lab's writer says so where it uses it.

## Essential

Configuration, session and marker packets are marked essential and written to
the Essentials topic as well as the data topic.

That topic is the answer to "what about consumers that start late". The data
topic is a firehose you join at the end; the essentials topic is short and
replayable from the beginning, so a consumer connecting mid-session can recover
the context it missed and then start decoding samples.

Markers go to both for the same reason — a consumer reading only the data
stream still needs to know where the laps were.

## In the wild

Decide what is essential by asking: **could a consumer that joined just now do
its job without this packet?** Configuration, no. A single sample, yes.

Anything in the first category belongs in essentials. Anything in the second
must not be, or you will replay the entire session every time somebody
reconnects.
