title: Sessions
module: 1
proto: open_data:NewSessionPacket api:CreateSessionRequest
code: producer/atlas_lab/writer.py  (start_session, end_session)
docs: https://atlas.motionapplied.com/developer-resources/secu4/stream_api/reference_docs/services/session-management/
source: https://github.com/Software-Products/MA.DataPlatforms.StreamApi
---
## What a session is

A named recording with a start, an end, an identity and a configuration that
belongs to it. Not a time range you agree on out of band — a thing the platform
knows about, that you can create, look up, annotate and end.

You call `CreateSession` on the Session Management service and it returns a
**session key**. Every packet after that carries the key, so a consumer can tell
which recording a sample belongs to without being told separately.

That is also the practical reason session creation comes first: you cannot fill
in `Packet.session_key` until you have been given one.

## What breaks without one

On a bare topic, a session is a start and end timestamp somebody wrote down. The
failures all have the same shape — the range and the data drift apart:

- Two cars, or two rigs, on the same topic. Which samples were which run?
- A producer restarts mid-session. Is that one session or two?
- Somebody re-runs an export with the wrong window and quietly gets twenty
  minutes of the wrong car.
- Six months later nobody can say what configuration a recording was made
  under, because the configuration lived in a file that has changed since.

None of these error. They produce plausible, wrong answers, which is worse.

## Details are part of the record

`CreateSession` takes a `Details` map, and it is worth using properly:

    Identifier = "silverstone-gp-2024"
    Details = { "track": "Silverstone Circuit", "weather": "dry",
                "temperature": "22" }

Anything you would otherwise write in a lab notebook belongs here, attached to
the recording rather than to a spreadsheet that will be separated from it.

## What the server does for you

The first time the Stream API sees a new data source, session and stream
combination, it writes a `StreamStarted` packet itself — you do not send one.
If you send one anyway it is rejected as a duplicate, and that is the only
packet-level rejection in the whole write path.

## In the wild

Create the session at the start of the real-world event you are recording — an
outing, a test, a flight, a run — not when your process happens to boot. End it
explicitly, including on failure, so downstream tools can tell "finished" from
"still going" from "died". A session that never ends looks live forever.
