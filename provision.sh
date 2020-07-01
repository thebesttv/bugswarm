#!/usr/bin/env bash
# Provision the environment for the BugSwarm reproducing pipeline.
# Tested on Ubuntu 16.04 & 18.04.

# Assumptions:
# 1. The user running this script has sudo privileges.

# Include common functions and constants.
source "${BASH_SOURCE%/*}"/common.sh

USAGE='Usage: bash provision.sh [github-credential]'

# Extract command line arguments.
# At this time, the script accepts one optional argument: a GitHub credential in the form '<username>:<token>'.
GITHUB_CREDENTIAL=$1

# Hack to make the script ask for sudo password before printing any steps.
sudo printf ''

# Cache Git credentials for convenience.
git config --global credential.helper "cache --timeout=86400"

print_green 'Provisioning the environment...'

print_green 'Update the apt package index'
sudo apt-get --assume-yes update
exit_if_failed 'Updating the apt package index failed.'

print_green 'Install git'
sudo apt-get --assume-yes install git
exit_if_failed 'Installing git failed.'

# Install pip3. This must be done before using pip3 to install the BugSwarm components.
print_green 'Install pip3'
sudo apt-get --assume-yes install python3-pip
exit_if_failed 'Installing pip3 failed.'

# Preapre to clone BugSwarm components. Perform this step as early as possible so the user waits the minimal time for
# the git credential prompt to appear.
mkdir -p ~/bugswarm
# Tell git to use the credential memory cache.
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=86400'

# Install the components.
print_green "Install BugSwarm components"
pip3 install --upgrade --force-reinstall . --user

# We need curl to install rvm and software-properties-common to install rvm
print_green 'Install curl'
sudo apt-get --assume-yes install curl
exit_if_failed 'Installing curl failed.'

print_green 'Install software-properties-common'
sudo apt-get --assume-yes install software-properties-common
exit_if_failed 'Installing software-properties-common failed.'

# Installation of RVM through their Ubuntu Doc: https://github.com/rvm/ubuntu_rvm
print_green 'Install RVM'
sudo apt-add-repository -y ppa:rael-gc/rvm
sudo apt-get --assume-yes update
sudo apt-get --assume-yes install rvm
source /etc/profile.d/rvm.sh
sudo usermod -aG rvm $(whoami)
exit_if_failed 'Updating the apt package index failed'

print_green 'Install Ruby 2.4.0'
rvm install ruby-2.4.0

print_green 'Install system packages'
sudo apt-get --assume-yes install libffi-dev gcc make
exit_if_failed 'Installing system packages failed.'

# Install Docker.
print_green 'Install Docker'
sudo apt -y install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt --assume-yes update
sudo apt -y install docker-ce
sudo usermod -aG docker $(whoami)
exit_if_failed 'Updating the apt package index failed.'

# Install Travis.
print_green 'Install Travis'
gem install travis -v 1.8.8 --no-document
exit_if_failed 'Installing Travis failed.'

# Install travis-build.
print_green 'Install travis-build'
mkdir -p ~/.travis
if [ ! -d ~/.travis/travis-build ]; then
    git clone -q https://github.com/travis-ci/travis-build.git ~/.travis/travis-build
fi

cd ~/.travis/travis-build/
yes | gem install bundler
yes | bundle install --gemfile ~/.travis/travis-build/Gemfile
bundler binstubs travis
cd ~
yes | travis
exit_if_failed 'Installing travis-build failed.'

# Done!
print_done_message 'Provisioning succeeded.'
