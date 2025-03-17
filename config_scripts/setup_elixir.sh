#!/bin/bash

echo "Installing Elixir and Phoenix"

# Update package list and install prerequisites
sudo apt-get update
sudo apt-get install -y curl gnupg2

# Install Erlang/OTP
echo "Adding Erlang Solutions repository"
wget https://packages.erlang-solutions.com/erlang-solutions_2.0_all.deb
sudo dpkg -i erlang-solutions_2.0_all.deb
sudo apt-get update
sudo apt-get install -y esl-erlang

# Install Elixir
echo "Installing Elixir"
sudo apt-get install -y elixir

# Install Hex and Rebar
echo "Installing Hex and Rebar"
mix local.hex --force
mix local.rebar --force

# Install Phoenix
echo "Installing Phoenix"
mix archive.install hex phx_new --force

echo "Elixir and Phoenix installation complete"
