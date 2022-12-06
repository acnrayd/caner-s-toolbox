# For Kaspersky Endpoint Security for Mac installation, there are two seperate installation scripts that needs to be run on Terminal. Less tech-savvy users are struggling to follow this process.
# Following script installs Kaspersky Network Agent for Mac and Kaspersky Endpoint Security for Mac in one go without any user interaction (other than entering Admin password)

# How to use?
# 1) Create a standalone installation package for Kaspersky Network Agent for Mac from KSC Web GUI and put it in the same folder with this script.
# 2) Create a standalone installation package for Kaspersky Endpoint Security for Mac from KSC MMC and put it in the same folder with this script.
# 3) Change name of installation package, it is specified in "kes_installer" variable.
# 4) Preferably put all 3 files to a .zip file before sending to the client.
# 5) Pro-tip: If you change extension to .command, this script can be run by double-click (without asking client to run Terminal)
# Installation requires sudo privileges.

#####

#!/usr/bin/env bash
 
ExitWithError() 
{
    echo "$2" 1>&2;
	exit $1
}

# I am disabling this part as script already requires root privileges.
# if [ "$EUID" -ne 0 ]
#    then
#        echo "This script must be run as root."
#        exit 1
# fi

cd "$(dirname "$0")" ### Required to change the current working directory to the directory that contains the script file.  

nagent_installer="./klnagentmac.sh" # Specify standalone network agent installation package file name
kes_installer="./kesmac11.2.1.145.sh" # Specify standalone KES for Mac installation package file name

if [ ! -f $nagent_installer ]
    then
        echo "Path to NAgent standalone package incorrect"
        exit 1
fi

if [ ! -f $kes_installer ]
    then
        echo "Path to KES standalone package incorrect"
        exit 1
fi

echo "Run KL NAgent installer ($nagent_installer) ..."
sudo sh $nagent_installer || ExitWithError $?

echo "KL NAgent successfully installed!"

echo "Run KES installer ($kes_installer) ..."
sudo sh $kes_installer || ExitWithError $?

echo "KES successfully installed!"
ExitWithError 0 ""
