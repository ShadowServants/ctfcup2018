#!/bin/bash
if [ ! -d "user_data" ]; then
  mkdir user_data
fi
if [[ ! -e user_count.txt ]]; then
  echo 1 > user_count.txt
fi
