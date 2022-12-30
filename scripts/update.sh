#!/usr/bin/env bash

set -eu

cd ~/notes.eatonphil.com
git reset --hard
git pull
sudo rm -rf /usr/share/caddy/*
sudo mv docs/* /usr/share/caddy/
sudo chown -R caddy:caddy /usr/share/caddy/
sudo restorecon -r /usr/share/caddy/
