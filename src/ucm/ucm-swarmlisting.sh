#!/usr/bin/env bash

for stack in $(docker stack ls --format '{{.Name}}'); do
  docker stack ps ${stack} --no-trunc  --format '{{.Name}}.{{.ID}} {{.Node}} {{.Image}}' -f "desired-state=running" \
    | sed -e "s/^/${stack} /g" -e "s/\@.*$//g"
done
