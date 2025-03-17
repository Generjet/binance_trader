#!/bin/bash

echo "Installing Elixir using default package manager"
sudo add-apt-repository ppa:rabbitmq/rabbitmq-erlang
sudo apt-get update
sudo apt install git elixir erlang

# ======== from Copilot ========
# sudo apt-get install -y esl-erlang  # Install Erlang
# sudo apt-get install -y elixir  # Install Elixir
# echo "Elixir installation complete" 