#!/bin/sh
if [ $# -lt 1 ]; then
    echo "usage: $0 text [percent-start [percent-end]]" >&2
    exit
fi

   speed=${PLAYCW_SPEED:-25}
    text=$1
start_pc=$2
  end_pc=$3

if [ ! -r $text ]; then
    echo "$0: can't read $text" >&2
    exit 1
fi

lines=$((0+$(wc -l <$text)))

if [ -z "$start_pc" ]; then
    start_ln=1
else
    start_ln=$(($start_pc*$lines/100+1))
fi

if [ -z "$end_pc" ]; then
    end_ln=$lines
else
    end_ln=$(($end_pc*$lines/100))
fi

cat <<EOT
Playing: $text
    speed: $speed WPM
    lines: $start_ln - $end_ln (total: $lines)
EOT

sed -e "${start_ln},${end_ln}!d" $text | ./morse.py -s $speed
