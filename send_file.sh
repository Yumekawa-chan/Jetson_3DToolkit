#!/bin/bash

# 監視するカラー画像と深度画像のフォルダのパス
COLOR_FOLDER="./color/"
DEPTH_FOLDER="./depth/"

# Windowsマシンの設定
DESTINATION_USER="marik"
DESTINATION_HOST="192.168.10.117"
DESTINATION_COLOR_PATH="C:\Users\marik\033lab\tools\JetsonOperator\color"
DESTINATION_DEPTH_PATH="C:\Users\marik\033lab\tools\JetsonOperator\depth"

# カラー画像のフォルダを監視して転送
inotifywait -m -e create --format '%w%f' "${COLOR_FOLDER}" | while read NEWFILE
do
    rsync -avz -e ssh "${NEWFILE}" "${DESTINATION_USER}@${DESTINATION_HOST}:${DESTINATION_COLOR_PATH}"
done &

# 深度画像のフォルダを監視して転送
inotifywait -m -e create --format '%w%f' "${DEPTH_FOLDER}" | while read NEWFILE
do
    rsync -avz -e ssh "${NEWFILE}" "${DESTINATION_USER}@${DESTINATION_HOST}:${DESTINATION_DEPTH_PATH}"
done
