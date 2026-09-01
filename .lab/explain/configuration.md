title: Configuration, and the packets that carry it
proto: open_data:ConfigurationPacket open_data:GroupDefinition
code: producer/atlas_lab/writer.py  (start_session)
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/examples/telemetry-example/
source: https://github.com/Software-Products/MA.DataPlatforms.StreamApi
---
## What configuration is

The description of a session that has to arrive before the numbers mean
anything: the parameters, the groups they belong to, and the data formats that
map an id to a list of parameters.

Sent once, near the start, with `IsEssential = true`.

## Nobody validates it for you

This is the thing worth knowing, and it is not written down anywhere obvious.

**The Stream API never opens your configuration packet.** Search its source for
`ConfigurationPacket` or `GroupDefinition` and you get nothing — it takes a
`Packet` with a type string and an opaque `content` blob, works out which topic
it belongs on, and writes it. It has no opinion about what is inside.

So a malformed configuration is not rejected. It is delivered, perfectly, to
whatever is reading — ATLAS, your own tooling, somebody else's dashboard — and
that is where it stops making sense. There is no error to find at the producer
end because nothing at the producer end went wrong.

Worse, the write path catches its own exceptions:

    catch (Exception ex) { this.apiLogger.Error(ex.ToString()); }

Failures go to the server's log, not back down the wire. If something is being
dropped, the server knows and you do not — so when a session arrives empty,
read the Stream API container's logs before you start re-reading your producer.

## Groups are a tree, not a list

The pattern in the official example is **one root group with the rest nested
inside it**, not a flat list:

    VehicleTelemetry
      +- Engine
      +- Brakes
      +- Position

A `GroupDefinition` has its own `Groups` field holding child definitions, and
each `ParameterDefinition` names the group it belongs to by identifier. That is
how you organise a car with two hundred channels so a consumer can show them as
a tree instead of one flat list of two hundred names.

The lab sends a single group because it has eleven channels and no need for a
hierarchy. Do not read that as a limit.

## Data formats map a list, not a parameter

`GetParameterDataFormatId` takes **a list of parameters and returns one id for
that combination**:

    Parameters = { "vCar:Chassis", "NGear:Chassis", "NEngine:FIA" }  ->  id

A `PeriodicDataPacket` then carries that id and its sample columns **in the same
order as the list**. Column 0 is `vCar`, column 1 is `NGear`, column 2 is
`NEngine`. Register a different list and you get a different id.

Get the order wrong and every value lands on the wrong channel, with no error,
at plausible-looking magnitudes. That is the single most expensive mistake in
this whole protocol.

## In the wild

Send the configuration before any data, and treat "it can see my session but no
channels" as a configuration problem rather than a connection one — whether the
thing reading is ATLAS, a dashboard or a script you wrote this morning. The
connection is almost never the issue; the Stream API would have refused to
connect at all.
