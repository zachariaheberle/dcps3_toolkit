


DST="./Flash_Firmware/HEX_Files/"
SRC="Flash_Firmware/"
HOST=$2

#Extract the file name from dst
FileName=$(echo $1 | rev | cut -d '/' -f1 | rev)
ssh -T $HOST << EOF
  mkdir -p $DST
EOF

scp $1 $HOST:$DST
ssh -T $HOST << EOF
  cd ~/$SRC;
  echo "We are in dir::\$PWD"
  gcc -O ./src/program_fpga_Nex.c  -l bcm2835 -o ./bin/NexFlash.exe
  sudo ./bin/NexFlash.exe < HEX_Files/$FileName
  sleep 1;
EOF
