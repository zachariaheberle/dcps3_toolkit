#!/usr/bin/env bash
# Written by Rohith Saradhy
# Email -> rohithsaradhy@gmail.com





parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
echo "Scipt Location::"$parent_path
HOST="Nex_3"
SRC=Flash_Firmware
SRC_HERE=$parent_path"/"$SRC

if [ -n "$4" ]
then
HOST=$4
fi


if [ "$2" = "1" ]
then
rsync -r $SRC_HERE $HOST:
ssh -T $HOST << EOF
cd ~/$SRC;
# pwd;
./compile.sh
sudo ./$1 $3    
EOF
else

ssh -T $HOST << EOF
cd ~/$SRC;
# pwd;
sudo ./$1 $3
EOF

fi




