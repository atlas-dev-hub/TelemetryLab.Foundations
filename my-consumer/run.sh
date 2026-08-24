#!/usr/bin/env bash
#
# Module 4. Replace the body of this file so it runs YOUR consumer.
#
# It is executed from the repository root with KAFKA_BOOTSTRAP set. Whatever it
# does, it must exit 0 and leave .lab/my-consumer.json behind. See
# my-consumer/README.md for the shape of that file.
#
# Install whatever your language needs here too - this script owns its
# environment. For example:
#
#   pip install --quiet confluent-kafka && python my-consumer/main.py
#   npm --prefix my-consumer ci && node my-consumer/index.js
#   go run ./my-consumer
#   dotnet run --project my-consumer
#
set -euo pipefail

cat <<'MESSAGE'
my-consumer/run.sh has not been written yet.

Module 4 asks you to write a consumer of your own, in any language, that reads
the telemetry back out of Kafka and writes .lab/my-consumer.json.

Start with my-consumer/README.md - it has the output contract, the topic names,
where the protobuf schema lives, and the three things most likely to catch you
out.

The reference consumer in consumer/ is worth reading. Just do not call it.
MESSAGE

exit 1
