#!/bin/bash

HOST="$1"

[ -z "$HOST" ] && echo "only arg must be the test target's hostname" && exit 1


JSON="$(st2 key get "$HOST" --json -a value | jq '.value' | head -c -2 | tail -c +2 | tr -d "\\")"
echo "Got JSON $JSON"


TEST_JOB="$(./generate_job.py "$JSON")"

[ $? -gt 0 ] && echo "$TEST_JOB" && exit 1

st2 key set "job_1" "$TEST_JOB"
