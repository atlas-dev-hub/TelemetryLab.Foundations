title: Packets, and how a consumer decodes one
module: 4
proto: open_data:Packet open_data:PeriodicDataPacket open_data:SampleColumn
code: consumer/src/consume.js
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/services/packet-reader/
---
## The envelope

Everything on the wire is a `Packet`: a type name, the session key it belongs
to, whether it is essential, and an opaque `content` blob. You read `type` to
know what the content is, then decode the content as that message.

`type` is a plain string — `"Configuration"`, `"PeriodicData"`, `"RowData"`,
`"Event"`, `"Marker"`. No enum, no registry. That is what lets one topic carry
packet kinds a given consumer has never heard of, and it is why skipping
unknown types is normal rather than defensive.

The Stream API treats `content` as bytes and never opens it. Only producers and
consumers know what is in there.

## Why samples do not name their parameters

A `PeriodicDataPacket` carries a `data_format_id` and a list of
`SampleColumn`s. It does not carry parameter names. Sending "Speed",
"Throttle", "Brake" with every batch at 100 Hz would be mostly string.

The id is registered once, against **an ordered list of parameters**:

    GetParameterDataFormatId({ "vCar:Chassis", "NGear:Chassis" }) -> 4271

and the columns in every packet using id 4271 line up with that list, by
position. Column 0 is `vCar`, column 1 is `NGear`.

So a consumer needs two things before a number means anything:

1. the id-to-parameter-list mapping, from the configuration and data format
   packets it read earlier
2. the `data_format_id` on the packet in front of it

Module 4 grades exactly this. The validator invents a channel name it has never
used before on each run, so a consumer that hardcodes its columns fails and one
that resolves the mapping passes.

## Order is the whole contract

Nothing checks that your columns are in the order you registered. Swap two and
every sample lands on the wrong channel, at a plausible magnitude, with no
error anywhere. Brake pressure showing up as throttle position looks like a
sensor fault for about a day.

## Sizing a batch

The gRPC message limit is hardcoded at 4 MiB in both directions. A batch that
exceeds it fails as a gRPC error rather than a helpful one, so size batches by
time — the lab uses 100 ms — rather than pushing for the largest that fits.

## In the wild

Treat unknown packet types as normal. A stream you did not write will grow
types you have not heard of, and a consumer that throws on the first one breaks
every time somebody upgrades the producer.
