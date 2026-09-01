title: Time, and why it must be contiguous
module: 3
proto: open_data:PeriodicDataPacket open_data:SampleDataFormat
code: producer/produce.py  (the timestamp_ns loop)
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/examples/telemetry-example/
source: https://github.com/Software-Products/MA.DataPlatforms.Protocol
---
## How time works here

Nanoseconds since the Unix epoch, as `int64`, everywhere. A `PeriodicDataPacket`
carries one start timestamp and an interval, and the samples after it are
implied — sample *n* is at `start + n x interval`. That is what makes a periodic
packet small: you send the clock once, not once per sample.

Which also means the start timestamp of each packet has to continue exactly
where the last one stopped.

## The failure Module 3 is built on

Read the clock again for each packet and you get this:

    timestamp_ns = time.time_ns()          # wrong: drifts every batch
    timestamp_ns += n * interval_ns        # right: continues the last batch

Nothing errors. Every value is correct. Every packet is accepted. But between
each packet there is a gap of however long your code took to get back round the
loop, so the trace is stitched together from fragments that do not quite meet.

Downstream it shows up as traces that look jittery, derived channels that spike
at packet boundaries, and lap times that are wrong by a few milliseconds in a
way that changes every run. You will look at the producer last, because the
producer is not complaining.

The official example does the same conversion explicitly, from milliseconds:

    var timestamp = (ulong)DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() * 1000000;

which is worth noticing: the resolution you send is not the resolution of the
field. That line records nanoseconds with millisecond granularity.

## Two things that will catch you out

**Nanoseconds do not fit in a double.** A nanosecond epoch timestamp is about
1.7 x 10^18; `Number.MAX_SAFE_INTEGER` is 9 x 10^15. In JavaScript, read these
as `BigInt` or your gap detection quietly rounds to the nearest 256 ns and finds
nothing. This lab hit exactly that.

**Clocks move.** Wall-clock time is not monotonic — NTP steps it, and it can go
backwards. Anchor once at session start, then advance by your own sample count.

## In the wild

Derive time from the thing generating the data, not from the machine relaying
it. If your source has its own clock or a sample counter, use it: it is the only
clock that knows when the measurement actually happened.
