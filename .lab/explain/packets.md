title: Packets, and how a consumer decodes one
module: 4
proto: open_data:Packet open_data:PeriodicDataPacket open_data:DataFormatDefinitionPacket
code: consumer/src/consume.js
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/services/packet-reader/
---
## The envelope

Everything on the wire is a `Packet`: a type name, the session key it belongs
to, whether it is essential, and an opaque `content` blob. You read the `type`
to know what the content is, then decode the content as that message.

That indirection is what lets one topic carry sessions, configuration, markers
and samples without a consumer needing to know all of them in advance. Decode
the types you understand; skip the rest without breaking.

## Why samples do not name their parameters

A `PeriodicDataPacket` carries a `data_format_id`, not a list of channel names.
Sending "Speed", "Throttle", "Brake" with every batch at 100 Hz would be mostly
string. Instead the mapping from id to parameter list is sent **once**, in a
`DataFormatDefinitionPacket`, and the samples reference it.

So a consumer has to do two things before a number means anything:

1. read the configuration and data-format packets, and remember the mapping
2. look up the `data_format_id` on each data packet to know which parameter
   each column is

Module 4 grades exactly this: the validator invents a channel name it has never
used before on each run, so a consumer that hardcodes the columns fails and one
that reads the mapping passes.

## Essential packets, and the late joiner

Configuration is sent once, at the start. A consumer that connects halfway
through has already missed it — so those packets are marked **essential** and
are also written to a separate stream a late joiner can replay.

If you have ever attached to a live feed and seen values with no names, this is
what you were missing.

## In the wild

Treat unknown packet types as normal, not as errors: a stream you did not write
will grow types you have not heard of, and a consumer that throws on the first
one is a consumer that breaks every time the producer is upgraded.
