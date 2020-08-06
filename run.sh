#!/bin/sh

read_time_interval=$(grep 'chat_bot_read_time_interval:' information.yaml | tail -n1 | awk '{ print $2}')

while true; do
  python chat_bot_utility.py;
  sleep $read_time_interval;
done
