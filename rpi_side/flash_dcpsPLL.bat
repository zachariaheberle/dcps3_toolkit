@echo off
@rem Written by Zachariah Eberle zachariah.eberle@gmail.com

SETLOCAL

set FILE=%1
set HOST=%2

ssh -T %HOST% "cd ~/rpi_dcps/pll_config; cp Si5344H_REG.h /media/pi/CIRCUITPY/Si5344H_REG.h; mpremote connect /dev/ttyACM0 run flash_pll.py"

ENDLOCAL