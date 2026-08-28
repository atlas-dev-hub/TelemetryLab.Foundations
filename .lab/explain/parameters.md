title: Parameters and channels
module: 2
proto: open_data:ParameterDefinition open_data:GroupDefinition
code: producer/atlas_lab/channels.py
docs: https://atlas.motionapplied.com/developer-resources/rta/worked-guide/configuration/channels-parameters/
---
## What a parameter is

Not a field name. A parameter carries its own identity, units, valid range,
display format and the rates it may arrive at — and all of it travels in the
stream, with the session, not in a schema file somewhere else.

Look at the definition below. Seventeen fields, and only one of them is the
name. That difference is the whole argument for a telemetry data model over a
topic full of numbers.

## What breaks without it

The classic failure is silent and long-lived: **a chart that has quietly been
in the wrong units since somebody swapped a sensor eighteen months ago.**

It happens because on a generic stack the facts about a channel live in four
places that nothing keeps in step —

- the producer, which knows the sensor
- a schema registry, which knows the type
- a dashboard config, which knows the axis label and units
- a wiki page, which knows what it means

Change the sensor and you have to change four things owned by three people. Miss
one and nothing errors. Every consumer keeps reading, and every number is wrong
by a constant factor that nobody notices.

Carried in-band, there is one place, and a consumer that has never heard of your
channel still knows it is `bar`, arrives at 100 Hz, and should sit between 0 and
250 — which is exactly what Module 2 has you prove.

## The rule that bites

Exactly one `GroupDefinition` per configuration packet. Send more and the whole
packet is **silently rejected** — no error, no channels.

    writer.py: "Rule 3: exactly one group. More than one is silently rejected."

And one data format per parameter (Rule 2). These two cost people a day each,
which is why they are written down here.

## In the wild

Declare a channel once, next to the thing that produces it, and let it flow.
Resist the urge to keep a spreadsheet of units — the moment there are two
records of the same fact, one of them is wrong and you cannot tell which.
