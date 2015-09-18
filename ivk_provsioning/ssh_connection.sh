#!/bin/bash
EMSS_ADDRESS=emssim@10.83.202.52
build_ver=FL15A_ENB_0107_001192_000000
USER_REPOSITORY="/home/ute/LOADS"
EMSS_REPOSITORY="/home/emssim/LOADS"
LAB_STORAGE="10.83.202.52"
SCP="/usr/bin/scp"
EMSS_ADDRESS2="10.83.202.52"
function check_version
{
ssh $EMSS_ADDRESS bash -c "'
cd LOADS/
if [ -d "$build_ver" ]; then
    cd "$build_ver"
    ls *_x64.bin
    ls "$build_ver"_release_BTSSM_downloadable.zip
    find * -type f >tmpfile.txt
     if grep -q FL15A_ENB_0107_001192_000000_release_BTSSM_downloadable.zip tmpfile.txt;then
        echo "First file is larger than 100M"
        if grep -q *_x64.bin tmpfile.txt;then
            echo "Second file is larger than 100M"
            echo "zmienna=1"
        fi
    fi
    rm tmpfile.txt
fi
exit
'"
echo $zmienna
}
#main
check_version
$SCP emssim@$EMSS_ADDRESS2:./LOADS/$build_ver/*_x64.bin USER_REPOSITORY

