#!/bin/bash
USER_ID="$(id -u)" GID="$(id -g)" docker compose up --build -d
