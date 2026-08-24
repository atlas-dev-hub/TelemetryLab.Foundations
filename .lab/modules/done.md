## Finished

Three modules down. You have run a real-time telemetry pipeline end to end,
extended it, and debugged it.

Along the way:

- A **session** is a named thing with a lifecycle, not a window of time.
- A **channel** is an identity with units and a rate, not a field name — and the
  configuration packet carries that in-band, so consumers written years later by
  people you will never meet can still interpret the data.
- **Measurement time is not arrival time**, and a pipeline that confuses them
  fails silently and convincingly.

### What comes next

| | |
|---|---|
| 4 | Write your own consumer from scratch, in any language |
| 5 | Build a bridge from an arbitrary data source |
| 6 | Survive a late joiner |
| 7 | Detect a real event, graded against ground truth |
| 8 | Instrument it to catch silent failures |
| 9 | Pass the conformance suite, hostile inputs included |

Finishing those earns a public page listing what you built, linking every
validation run and every line of code you wrote — so the evidence is the work,
not the badge.
