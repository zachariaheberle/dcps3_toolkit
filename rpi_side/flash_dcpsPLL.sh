#!/usr/bin/env bash
# Written by Zachariah Eberle zachariah.eberle@gmail.com

FILE=$1
HOST=$2

ssh -T $HOST << EOF
cd ~/rpi_dcps/pll_config;
cp Si5344H_REG.h /media/pi/CIRCUITPY/Si5344H_REG.h
mpremote connect /dev/ttyACM0 run flash_pll.py;
EOF