#!/bin/bash

#!/bin/bash

# Script to install Ruby using rbenv

# Check if the user has root privileges
if [[ $EUID -ne 0 ]]; then
  echo "This script requires root privileges. Please run with sudo."
  exit 1
fi

# Update package lists
echo "Updating package lists"
sudo apt-get update -y

# Install rbenv dependencies
echo "Installing rbenv dependencies"
sudo apt-get install -y git curl ruby-build

# Install rbenv
echo "Installing rbenv"
curl -fsSL https://github.com/rbenv/rbenv-installer/raw/HEAD/bin/rbenv-installer | bash
export PATH="$HOME/.rbenv/bin:$PATH"
rbenv init -

# List available Ruby versions
echo "Listing available Ruby versions"
rbenv install -l

# Prompt the user to select a Ruby version
read -p "Enter the Ruby version to install: " ruby_version

# Install the selected Ruby version
echo "Installing Ruby version $ruby_version"
if rbenv install $ruby_version; then
  echo "Ruby version $ruby_version installed successfully"
else
  echo "Ruby version $ruby_version installation failed. Please check the build log."
  exit 1
fi

# Set the selected Ruby version as the global version
echo "Setting Ruby version $ruby_version as global"
rbenv global $ruby_version

echo "Ruby installation complete using rbenv"