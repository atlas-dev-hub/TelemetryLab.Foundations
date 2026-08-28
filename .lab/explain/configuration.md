title: Configuration, and the packets that carry it
proto: open_data:ConfigurationPacket open_data:DataFormatDefinitionPacket
code: producer/atlas_lab/writer.py  (start_session)
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/services/data-format-management/
---
## What configuration is

The description of a session that has to arrive before the numbers mean
anything: the parameters, the group they belong to, and the data formats that
map an id to a list of parameters.

It is sent once, at the start, marked essential, on both streams.

## The order that actually works

This sequence is not arbitrary, and each step has a failure mode if you skip it:

1. **Create the session** and get a key.
2. **Wait** for the Stream API to register it — configuration for a session it
   does not know about is discarded, silently.
3. **Send the configuration packet** — with exactly one group definition in it.
4. **Send one data-format definition per parameter.**
5. Only now, send data.

Three of those five are things the platform will not tell you that you got
wrong. It will accept the packets and give you a session that looks fine and
carries nothing.

## The four rules, written down

The lab's writer carries these as comments because each one cost somebody a day:

- **Rule 1** — the session must be registered before configuration arrives
- **Rule 2** — one data format per parameter
- **Rule 3** — exactly one GroupDefinition per packet; more is silently rejected
- **Rule 4** — configuration goes to both streams, marked essential

Rule 5 lives in the producer rather than the writer: timestamps must be
contiguous. That is what Module 3 is about.

## In the wild

If a consumer can see your session but no channels, you have hit Rule 1 or
Rule 3. Check those two before anything else — between them they account for
most first integrations that connect fine and produce nothing.
