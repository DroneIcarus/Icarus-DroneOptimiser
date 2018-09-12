#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e
# Print working directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

check_root()
{
    SCRIPT_USER="$(whoami)"
    if [ "$SCRIPT_USER" == "root" ]
    then
        echo "You need to run the script as root"
        echo "Example: sudo .$DIR/install.sh"
        return 1
    fi
}

check_os_disto()
{
	echo '# Checking OS and distribution'
	echo '######################################################'
	OS="$(uname -s)"
	case "${OS}" in
		"Linux")
			DISTRO="$( awk '/^ID=/' /etc/*-release | awk -F'=' '{ print tolower($2) }' | sed -e 's/^"//' -e 's/"$//' )"
			DISTRO_VER="$( awk '/^DISTRIB_RELEASE=/' /etc/*-release | awk -F'=' '{ print tolower($2) }')"
			if ! [[ "$DISTRO" =~ ^(ubuntu)$ ]]
			then
				echo "Error: Your linux distribution is not supported."
				exit 1
			fi
			;;
		"Darwin")
			DISTRO="mac"
			#TODO: Fetch macOS version for DISTRO_VER
			echo "Error: macOS is not supported."
			;;
		*)
			echo "Error: Your OS is not supported."
			exit 1
			;;
	esac
	echo "$OS" "$DISTRO" "$DISTRO_VER"
}

install_distro_packages()
{
	echo '# Installing prerequesites for icarUS mission optimizer'
	echo '######################################################'
	case "$1" in
	"ubuntu")
		sudo apt-get update
		sudo apt-get install build-essential python3-dev python3-pip tk8.6-dev -y
		;;
	*)
		echo "Error: Your linux distribution is not supported."
		exit 1
		;;
	esac
}

install_python_packages()
{
	echo '# Creating virtual environment and Installing python3 dependencies...'
	echo '#####################################################################'
	sudo -H pip3 install --upgrade pip
	sudo -H pip3 install -U pipenv
	pipenv install
}



###
# Main installer script
###
echo '
###
#    icarUS Mission Optimizer installer
###
'
#check_root
check_os_disto
install_distro_packages "$DISTRO"

install_python_packages
install_icarus_mission_optimizer "$DISTRO"

echo '# You should now be all set!'
echo ''
echo 'If you ever need to add a pip package, add it this way:'
echo '   pipenv install <package_name>'
echo ''
echo ''
echo 'Enter the virtual environment:'
echo '   pipenv shell'
