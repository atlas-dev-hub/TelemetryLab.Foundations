## Foundation complete

Four modules. You have run a real-time telemetry pipeline, extended it, debugged
it, and written your own consumer for it.

What you now know that you did not before:

- A **session** is a named thing with a lifecycle, not a window of time.
- A **channel** is an identity with units, a rate and a range — and the
  configuration packet carries all of that in-band, so a consumer written years
  later by someone you will never meet can still interpret the data.
- **Measurement time is not arrival time.** A pipeline that confuses them fails
  silently and convincingly.
- A consumer needs **nothing hardcoded**. Everything it needs to make sense of
  the stream is in the stream.

That last one is the whole argument. On Kafka plus a time-series database, every
one of those facts lives somewhere else — a schema registry, a wiki, a naming
convention, someone's memory — and drifts out of date.

### Practitioner

| | |
|---|---|
| 5 | Build a bridge from an arbitrary data source |
| 6 | Survive a late joiner |
| 7 | Detect a real event, graded against ground truth |
| 8 | Instrument it to catch silent failures |
| 9 | Pass the conformance suite, hostile inputs included |

Finishing those earns a public page listing what you built, linking every
validation run and every line of code you wrote — so the evidence is the work,
not the badge.
