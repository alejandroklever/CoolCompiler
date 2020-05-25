#!/usr/bin/env bash

echo "Hello World"

for i in {1..5} ; do
  if [ $i ]; then
    echo $i
  fi
done