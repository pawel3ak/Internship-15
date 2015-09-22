#!/bin/bash
#
# SCRIPT: ivk_provisioning.sh
# AUTHOR: Radek Papke
# DATE: 22-07-2014
# REV 0.1 (draft)
#
# PLATFORM: UTE
#
# PURPOSE: This script gives the ute engineer an easy-
#          to-follow menu to handle daily tasks, such
#          as software donwload from the trunk
#
# REV LIST:
#
#
# set -n # Uncomment to check script syntax without any execution
# set -x # Uncomment to debug this script
#
###############################################
####### DEFINE FILES AND VARIABLES HERE #######
###############################################

BINDIR="/usr/local/bin"
PASSWORD_SERVER="yogi"
THIS_HOST=$(hostname)
SCRIPT_NAME=`basename $0`

msg="                        "
opt=" " # Variable for menu selection

###############################################
########## DEFINE FUNCTIONS HERE  #############
###############################################


function show_usage()
{
    # Shows the usage of the application

    echo "Usage:"
    echo "  $SCRIPT_NAME "
    echo "  $SCRIPT_NAME [-option] "
    echo "  $SCRIPT_NAME [-option] [argument]"
    echo ""
    echo "where:"
    echo "  option    - option from menu "
    echo "  argument  - provide argument if required by option"
}


function BTSSM_install
{
# Strip out all BTSSM processes
ltebtsmanager_killer=$(ps aux | grep -v grep | grep "ltebtsmanager.jar" | awk '{print $2}')
poseidonStarter_killer=$(ps aux | grep -v grep | grep "PoseidonStarter" | awk '{print $2}')

# And kill them when they exist
[[ ! -z $ltebtsmanager_killer ]] && kill -9 $ltebtsmanager_killer 2>/dev/null
[[ ! -z $poseidonStarter_killer ]] && kill -9 $poseidonStarter_killer 2>/dev/null

# Install BTSSM in silent mode

if [[ "$sw_rel" == "FL00" ||  "$sw_rel" == "FL15A" ]];then
         /bin/bash ${USER_REPOSITORY}/${build_ver}//${BTSSM_FDD}${btssm_ver}_x64.bin -i silent
elif [[ "$sw_rel" == "EMSS" ]]; then
        /bin/bash ${USER_REPOSITORY}/${build_ver}/*_x64.bin -i silent
else
        /bin/bash ${USER_REPOSITORY}/${build_ver}//${BTSSM_FDD}${1}-${btssm_ver}_x64.bin -i silent
fi


# Modify desktop shortcut with user and password needed to login into BTS
sed -i "s/btssitemanager/btssitemanager \"-pw Nemuadmin:nemuuser -ne 192.168.255.129\"/" /home/ute/Desktop/nsn-btssitemgr.desktop

# Launch BTSSM
btssitemanager "-pw Nemuadmin:nemuuser -ne 192.168.255.129" &
}


function FDD_Trunk
{
# Check whether requested software exist on server
wget    -O ${SW_CONFIG_TMP} ${FDD_TRUNK_STORAGE_URL}/job/build.fsmr3/${build_no}/artifact/build/.config \
        -q

# If software does not exist, then exit
if [ $? -ne 0 ]
then
        echo -e "\nSoftware version is not proper or doesn't exist on WFT_server\n"
        exit 1
fi

# Prepare software-specific localization
mkdir $USER_REPOSITORY/$build_ver

# BTS SiteManager Version
# Check FB for BTSSM
wget    -O ${LINKS} ${FDD_TRUNK_STORAGE_URL}/job/build.fsmr3/${build_no}/LINKS/LINKS.html \
        -q

# >> /isource/svnroot/BTS_D_SE_UI_14_05/lte/fd/installer/tags/LN7.0_BTSSM_0_087_0
#btssm_svn=$(cat ${SW_CONFIG_TMP} | grep BTSSM | head -n 1 | cut -d' ' -f4)
#btssm_svn=$(cat ${LINKS} | grep BTSSM | awk -F\" '{print $(NF-3)}' | sed 's/beisop60.china.nsn-net.net/svne1.access.nsn.com/')
btssm_svn=$(cat ${LINKS} | grep BTSSM | awk -F\" '{print $(NF-3)}' | head -n 1)
# >> 0_087_0
btssm_ver=$(cat ${SW_CONFIG_TMP} | grep BTSSM | head -n 1 | cut -d'/' -f9 | sed 's/_BTSSM_/-/')
# >> LN8.0
btssm_rel=$(cat ${SW_CONFIG_TMP} | grep BTSSM | head -n 1 | cut -d'/' -f9)

BTSSM_FDD="BTSSiteEM-"
echo "Mode: FDD"

wget    -O ${USER_REPOSITORY}/${build_ver}/${build_ver}_release_BTSSM_downloadable_wo_images.zip \
           ${FDD_TRUNK_STORAGE_URL}/job/build.fsmr3/${build_no}/artifact/build/${build_ver}_release_BTSSM_downloadable.zip

wget    -O ${USER_REPOSITORY}/${build_ver}/im_${build_no}.jar \
           ${FDD_TRUNK_STORAGE_URL}/job/build.fsmr3/${build_no}/artifact/build/im_${build_no}.jar

wget    -O ${USER_REPOSITORY}/${build_ver}/${BTSSM_FDD}${btssm_ver}_x64.bin \
        --no-check-certificate \
        --user='ca_ivk_crt' \
        --password='caivkcrt' \
        ${btssm_svn}${BTSSM_FDD}${btssm_ver}_x64.bin \

# Make BTSSM binary installable (chmod +x BTSSM*)
chmod +x ${USER_REPOSITORY}/${build_ver}//${BTSSM_FDD}${btssm_ver}_x64.bin

BTSSM_install FL00
}

function FDD_FL15A
{
# Verify whether build exists on WFT
wget --no-check-certificate --spider https://wft.inside.nsn.com/ext/build_content/$build_ver

# If software does not exist, then exit
if [ $? -ne 0 ]
then
        echo -e "\nSoftware version is not proper or doesn't exist on WFT_server\n"
        exit 1
fi

# Verify whether build passed Quick Tests
qt=$(curl -k  https://wft.inside.nsn.com/ext/build_content/$build_ver | xml_grep --text_only --cond 'result' | tr '\n' ' ')

qt1=$(echo "$qt" | cut -d' ' -f1)
qt2=$(echo "$qt" | cut -d' ' -f2)

echo "QT1: $qt1"
echo "QT2: $qt2"

if test "$qt1" != "released"
then
        echo "QuickTest1 has not been released"
        #exit 1
elif  test "$qt2" != "released"
then
        echo "QuickTest2 has not been released"
        #exit 1

fi

# Prepare software-specific localization
mkdir $USER_REPOSITORY/$build_ver

# BTS SiteManager Version
btssm_rel=$(curl -k  https://wft.inside.nsn.com/ext/build_content/$build_ver | xml_grep --text_only  --cond '*[@title="BTS Site Manager"]' | head -1)
btssm_ver=$(echo $btssm_rel | sed 's/_BTSSM_/-/g')

BTSSM_FDD="BTSSiteEM-"

wget --no-check-certificate -O ${USER_REPOSITORY}/${build_ver}/${BTSSM_FDD}${btssm_ver}_x64.bin ${FDD_WFT_STORAGE_URL}/load_file/${btssm_rel}/4?file=/C_Element/SE_UICA/Setup/${BTSSM_FDD}${btssm_ver}_x64.bin
wget --no-check-certificate -O ${USER_REPOSITORY}/${build_ver}/${build_ver}_release_BTSSM_downloadable_wo_images.zip http://wrlinb104.emea.nsn-net.net:9090/lteRel/build/FL15A/${build_ver}_release_BTSSM_downloadable_wo_images.zip&project=ALL


# Make BTSSM binary installable (chmod +x BTSSM*)
chmod +x ${USER_REPOSITORY}/${build_ver}//${BTSSM_FDD}${btssm_ver}_x64.bin

BTSSM_install FL00
}
function check_version
{
build_ver=FL00_FSM3_9999_150921_025249
USER_REPOSITORY="/home/ute/LOADS"
EMSS_REPOSITORY="/home/emssim/LOADS"
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
}
function download_from_emss_server
{
echo "We download files from emss server"
                    cd $USER_REPOSITORY
                    mkdir $build_ver
                    scp $EMSS_ADDRESS:~/LOADS/$build_ver/$build_ver"_release_BTSSM_downloadable.zip" $USER_REPOSITORY/$build_ver
                    scp $EMSS_ADDRESS:~/LOADS/$build_ver/*_x64.bin $USER_REPOSITORY/$build_ver
                    chmod +x $USER_REPOSITORY/$build_ver/$build_ver'_release_BTSSM_downloadable.zip'
                    chmod +x $USER_REPOSITORY/$build_ver/*_x64.bin
                    BTSSM_install EMSS
}
function software_download
{
# Flexi baseline
build_ver=$1


# Get Flexi build number [FDD Jenkins]
build_no=$(echo $build_ver | cut -d'_' -f5 | sed 's/^0*//')


# User-specific Variables
USER=$(whoami)
USER_REPOSITORY="/home/ute/LOADS"
EMSS_ADDRESS=emssim@10.83.202.52
# FDD Jenkins
FDD_TRUNK_STORAGE_URL="http://wrling23.emea.nsn-net.net:8080"

# TDD Jenkins
TDD_STORAGE_URL="http://hzling23.china.nsn-net.net:8080"

# WFT
FDD_WFT_STORAGE_URL="https://wft.inside.nsn.com/download"

# LOG file
NOW=$(date +"%b%d%y-%H%M")
LOG="$USER_REPOSITORY/$build_ver-$NOW.log"
SW_CONFIG_TMP="/tmp/${build_no}"
LINKS="/tmp/${build_no}_LINKS"

# Verify the type of input and number of values
[ $# -ne 1 ] && { echo "Usage: $SCRIPT_NAME $opt <SOFTWARE_VERSION>"; exit 1; }
#Check if build is on emss srever
is_it_available_on_our_server=$(check_version $build_ver)
sw_rel=$(echo $build_ver | cut -d'_' -f1)
echo $is_it_available_on_our_server
case $is_it_available_on_our_server in
     *'Second file is larger than 100M'*)
        echo "Files are correct"
        sw_rel='EMSS';;
     *)
        echo "No files on our server"
esac

case "$sw_rel" in
    EMSS)
                    download_from_emss_server
                    ;;
    FL00)
                    FDD_Trunk
    ;;
    FL15A)
                    FDD_FL15A

    ;;
    *)
                    echo -e "\n Unknown Software Release \n"
    ;;
esac
}



###############################################
############## SET A TRAP HERE ################
###############################################

trap 'echo "\nEXITING on a TRAPPED SIGNAL\n"; \
      exit 1' 1 2 3 15

###############################################
############ BEGINNING OF MAIN ################
###############################################

# Option without menu
if (( $# != 0 && $# != 2 ))
then
    show_usage
    exit 1
fi


if (( $# == 2 ))
then
    case $1 in
        1)
            software_download $2
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
else
    # Loop until option 99 is Selected

    # We use 99 as a character instead of an integer
    # in case a user enters a non-integer selection,
    # which would cause the script to fail.
    while [[ $opt != 99 ]]
    do

       # Display a reverse video image bar across the top
       # of the screen with the hostname of the machine.

       clear        # Clear the screen first
       tput smso    # Turn on reverse video
       echo -e "                                  ${THIS_HOST}\c"
       echo -e "                                       "
       tput sgr0    # Turn off reverse video
       echo -e "\n"    # Add one blank line of output

       # Show the menu options available to the user with the
       # numbered options highlighted in reverse video
       #
       # $(tput smso) Turns ON reverse video
       # $(tput sgr0) Turns OFF reverse video

       echo -e "$(tput smso)1$(tput sgr0) - Software Download"

       echo -e "\n" # echo new lines

       echo -e "$(tput smso)99$(tput sgr0) - Logout\n"

       # Draw a reverse video message bar across bottom of screen,
       # with the error message displayed, if there is a message.

       tput smso  # Turn on reverse video

       echo -e "                              ${msg}\c"
       echo -e "                          "

       tput sgr0  # Turn off reverse video

       # Prompt for menu option.

       echo -e "Selection: \c"
       read opt

       # Assume the selection was invalid. Because a message is always
       # displayed we need to blank it out when a valid option
       # is selected.

       msg="Invalid option selected."

       # Process the Menu Selection

       case $opt in
       1)
            # option 1 - Software Download
            echo -e "Provide the software version to be downloaded:"
            echo -en "> "
            read soft
            software_download $soft
            sleep 1
            msg="                        "
            ;;
       esac

       # End of Loop until 99 is selected

    done

    # Erase menu from screen upon exiting with the "clear" command

    clear
    # End of Script
fi

