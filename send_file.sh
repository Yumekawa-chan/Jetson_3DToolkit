#!/bin/bash

REMOTE_USER="***"
REMOTE_HOST="192.168.10.125"
REMOTE_PASS="********"
REMOTE_BASE_DIR="***/***/jetson_operator/"

DIRECTORIES=("image")

for DIR in "${DIRECTORIES[@]}"
do
    inotifywait -m "$DIR" -e create -e moved_to |
        while read path action file; do
            echo "The file '$file' appeared in directory '$path' via '$action'"
            sshpass -p "$REMOTE_PASS" scp "$path$file" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_BASE_DIR$DIR/"
        done
done
