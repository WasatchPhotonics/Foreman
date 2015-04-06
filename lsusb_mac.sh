#!/bin/sh
# ssh to the specified suffix, print the status of the lsusb command along with
# the device mac address
ssh -i ./test_key_rsa parallella@192.168.1.$1 \
    "lsusb; ifconfig | grep eth"
