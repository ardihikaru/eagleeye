#!/bin/bash
# Recommend syntax for setting an infinite while loop
while :
do
        # echo "Do something; hit [CTRL+C] to stop!"
        docker exec ntp chronyc tracking
        echo ""
        sleep 1
done
