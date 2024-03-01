@echo off
@rem Written by Zachariah Eberle zachariah.eberle@gmail.com

SETLOCAL

if not "%7"=="" set HOST=%7

ssh -T %HOST% "cd /home/pi/rpi_dcps; pwd; sudo ./%1 %2 %3 %4 %5 %6 %8"

ENDLOCAL