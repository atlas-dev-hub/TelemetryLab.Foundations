title: Sessions
module: 1
proto: open_data:NewSessionPacket open_data:EndOfSessionPacket
code: producer/atlas_lab/writer.py  (start_session, end_session)
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/services/session-management/
---
## What a session is

A named recording with a start, an end, an identity and a configuration that
belongs to it. Not a time range you agree on out of band — a thing the platform
knows about, that you can create, look up, annotate and end.

The producer asks the Session Management service to create one and gets back a
**session key**. Every packet after that carries the key, so a consumer can tell
which recording a sample belongs to without being told separately.

## What breaks without one

On a bare topic, "a session" is a start and end timestamp that somebody writes
down. The failures are all the same shape — the range and the data drift apart:

- Two cars, or two rigs, on the same topic. Which samples were which run?
- A producer restarts mid-session. Is that one session or two?
- Somebody re-runs an export with the wrong window and quietly gets 20 minutes
  of the wrong car.
- Six months later nobody can say what configuration a recording was made under,
  because the configuration lived in a file that has since changed.

None of these error. They produce plausible, wrong answers, which is worse.

## The ordering rule that bites

The session has to exist before its configuration arrives. The Stream API
discards configuration for a session it has not registered yet, and **it does
not tell you** — you get a session with no channels and no error.

    writer.py: "Rule 1: give the Stream API a moment to register the session
    before configuration arrives. Without this the config can land first and
    be discarded."

This is the single most common way a first integration silently produces
nothing. If a consumer sees your session but no parameters, look here first.

## In the wild

Create the session at the start of the real-world event you are recording — an
outing, a test, a flight, a run — not when your process happens to boot. End it
explicitly, even on failure, so downstream tools can tell "finished" from
"still going" from "died". A session that never ends looks live forever.
