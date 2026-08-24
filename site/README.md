# The site

`telemetrylab.atlas.motionapplied.com`

Static. No framework, no npm, no dependencies — two Python scripts.

```bash
python site/build/export_lap.py   # a real lap -> site/public/lap.json
python site/build/build.py        # -> site/dist/
```

| Output | For |
|---|---|
| `dist/index.html` | the deployed site |
| `dist/artifact.html` | the same content without a document wrapper, for review |

## Why the hero is real data

`export_lap.py` runs the lab's own simulator — the same code a learner executes
in Module 1 — and writes out the track geometry and speed profile. The landing
page animates that.

It would have been quicker to draw a plausible squiggle. A site about telemetry
showing invented telemetry is a bad first impression for anyone who looks
closely, and the people we want are the ones who look closely.

It also means the site cannot drift from the product: change the circuit or the
car model, and the hero changes with it on the next deploy.

## Not built yet

Module pages (also the SEO surface), `/engineers/<handle>`, and the graduates
index. Those need the completion registry, which does not exist yet.
