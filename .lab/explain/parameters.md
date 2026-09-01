title: Parameters and channels
module: 2
proto: open_data:ParameterDefinition open_data:GroupDefinition
code: producer/atlas_lab/channels.py
docs: https://atlas.motionapplied.com/developer-resources/rta/worked-guide/configuration/channels-parameters/
---
## What a parameter is

Not a field name. A parameter carries its own identity, units, valid range,
display format, warning thresholds and the rates it may arrive at — and all of
it travels in the stream, with the session, not in a schema file somewhere.

Look at the definition below. Seventeen fields, one of which is the name.

## The fields worth knowing about

- **`frequencies`** is a list, not a number. A parameter can legitimately arrive
  at more than one rate. The official example runs engine RPM at 10 Hz, oil
  pressure at 2 Hz and coolant temperature at 1 Hz in the same session — that
  is what multi-rate means in practice, and it is why a consumer cannot assume
  one sample interval for everything.
- **`min_value` / `max_value`** are the expected range, so a display can scale
  an axis before it has seen any data.
- **`warning_min_value` / `warning_max_value`** are separate. The example sets
  a brake temperature warning at 700 with a maximum of 800 — "still valid,
  worth looking at" is a different statement from "out of range".
- **`format_string`** is a printf pattern, `"%5.1f"`. It travels with the
  channel so every tool renders it the same way.
- **`conversion`** turns numbers into text — gear 0 into "N", a state code into
  a state name — without every consumer hardcoding the same table.

## Groups are a tree

`groups` on a parameter is a list of group *identifiers*. The groups themselves
are `GroupDefinition`s in the configuration packet, and they nest:

    VehicleTelemetry
      +- Engine        Engine.Rpm, Engine.Temperature, Engine.OilPressure
      +- Brakes        Brakes.FrontLeft.Temperature, ...
      +- Position      Position.Latitude, Position.Longitude

One root, children inside it. That is how two hundred channels stay navigable
instead of arriving as a flat list of two hundred names. The lab ships one
group because it has eleven channels; that is not a limit.

## What breaks without any of this

The classic failure is silent and long-lived: **a chart that has quietly been
in the wrong units since somebody swapped a sensor eighteen months ago.**

On a generic stack the facts about a channel live in four places nothing keeps
in step — the producer, a schema registry, a dashboard config, and a wiki page.
Change the sensor and you have four things to update, owned by three people.
Miss one and nothing errors: every consumer keeps reading, and every number is
wrong by a constant factor nobody notices.

Carried in-band there is one copy, and a consumer that has never heard of your
channel still knows it is in bar, arrives at 100 Hz, and should sit between 0
and 250. Module 2 has you prove exactly that.

## In the wild

Declare a channel once, next to the thing that produces it. The moment there
are two records of the same fact, one of them is wrong and you cannot tell
which — and the one people trust is usually the spreadsheet.
