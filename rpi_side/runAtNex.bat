@echo off
@rem Written by Zachariah Eberle zachariah.eberle@gmail.com

SETLOCAL

set parent_path=%~dp0
echo Scipt Location::%parent_path%
set HOST=Nex_3
set SRC=Flash_Firmware
set SRC_HERE=%parent_path%%SRC%

if not "%4"=="" set HOST=%4

echo %HOST%

if "%2"=="1" (
    scp -r %SRC_HERE% %HOST%:
    ssh -T %HOST% "cd ~/%SRC%; ./compile.sh; sudo ./%1 %3"
) else (
    ssh -T %HOST% "cd ~/%SRC%; sudo ./%1 %3"
)

ENDLOCAL