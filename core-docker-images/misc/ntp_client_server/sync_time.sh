#!/bin/bash
while :
do
        sudo ntpdate -u 192.168.1.10
        sudo hwclock --systohc --localtime
        echo "Sync'd with NTP Server"
        sleep 1
done
