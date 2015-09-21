#!/bin/bash
EMSS_ADDRESS=emssim@10.83.202.52
build_ver=FL00_FSM3_9999_150921_025249
USER_REPOSITORY="/home/ute/apache_script"
EMSS_REPOSITORY="/home/emssim/LOADS"
function check_version
{
is_it_available_on_our_server=$( ssh $EMSS_ADDRESS bash -c "'
cd LOADS/
if [ -d "$build_ver" ]; then
    cd "$build_ver"
    ls *_x64.bin
    ls "$build_ver"_release_BTSSM_downloadable.zip
    find * -size +100M >tmpfile.txt
     if grep -q *_x64.bin tmpfile.txt;then
        echo "First file is larger than 100M"
        if grep -q "$build_ver"_release_BTSSM_downloadable.zip tmpfile.txt;then
            echo "Second file is larger than 100M"
        elif grep -q "$build_ver"_release_BTSSM_downloadable_wo_images.zip tmpfile.txt; then
            echo "This is a symbolic link"
            echo "Second file is larger than 100M"
        fi
    fi
    rm tmpfile.txt
fi
exit
'")
echo $is_it_available_on_our_server
case $is_it_available_on_our_server in
     *'Second file is larger than 100M'*)
        echo "We download files from emss server"
        cd $USER_REPOSITORY
        mkdir $build_ver
        scp $EMSS_ADDRESS:~/LOADS/$build_ver/$build_ver"_release_BTSSM_downloadable.zip" $USER_REPOSITORY/$build_ver
        scp $EMSS_ADDRESS:~/LOADS/$build_ver/*_x64.bin $USER_REPOSITORY/$build_ver
        chmod +x $USER_REPOSITORY/$build_ver/$build_ver'_release_BTSSM_downloadable.zip'
        chmod +x $USER_REPOSITORY/$build_ver/*_x64.bin;;
     *)
     echo "Zle"

esac
}
#main
is_it_available_on_our_server=$(check_version)
echo $is_it_available_on_our_server

