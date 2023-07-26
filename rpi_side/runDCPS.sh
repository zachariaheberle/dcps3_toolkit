#!/bin/bash

if [ -n "$7" ]
then
HOST=$7
fi

ssh -T $HOST << EOF
cd /home/pi/rpi_dcps;
pwd;
sudo ./$1 $2 $3 $4 $5 $6 $8
EOF
