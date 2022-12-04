#!/bin/bash

gpio mode 29 out
gpio write 29 1
gpio write 29 0
gpio write 29 1
gpio mode 29 in
