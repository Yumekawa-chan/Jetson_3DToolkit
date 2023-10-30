#!/bin/bash

# Path to the configuration file
CONFIG_FILE = ./config.txt

# Check if the configuration file exists
if [[! -f $CONFIG_FILE]]
then
echo "Configuration file not found: $CONFIG_FILE"
 exit 1
fi

# Load settings from the configuration file
source $CONFIG_FILE

# Check if inotify-tools is installed
if ! command - v inotifywait & > / dev/null
then
echo "inotify-tools is required. Please install it."
 exit 1
fi

# Monitor the directory
inotifywait - m - e create - -format '%w%f' "$WATCH_DIR" | while read NEW_FILE
do
# Only transfer if the file extension is .ply
  if [["$NEW_FILE" == *.ply]]
   then
    # Use scp to transfer the file to the Windows PC
     sshpass - p "$SCP_PASS" scp "$NEW_FILE" "$SCP_DEST"
       if [$? -eq 0]
        then
        echo "Transferred $NEW_FILE to Windows PC."
        else
        echo "Failed to transfer $NEW_FILE."
        fi
    fi
done
