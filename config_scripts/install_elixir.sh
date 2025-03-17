#!/bin/bash

echo "Installing Elixir using Mise"
sudo apt update
sudo apt install build-essential rustc libssl-dev libyaml-dev zlib1g-dev libgmp-dev
curl https://mise.run | sh
echo 'eval "$(~/.local/bin/mise activate)"' >> ~/.bashrc
source ~/.bashrc
mise use -g elixir@1.12.3
echo "Elixir installation complete"


# ======== install guide from https://elixir-lang.org/install.html#gnulinux ========
# curl -fsSO https://elixir-lang.org/install.sh
# sh install.sh elixir@1.18.3 otp@27.2.3
# installs_dir=$HOME/.elixir-install/installs
# export PATH=$installs_dir/otp/27.2.3/bin:$PATH
# export PATH=$installs_dir/elixir/1.18.3-otp-27/bin:$PATH
# iex