curl --location --request POST 'http://140.113.86.92:31000/api/stream/live' \
--data-raw '{
    "algorithm": "YOLOv3",
    "stream": "STREAM",
    "uri": "rtsp://140.113.86.92/test",
    "scalable": true
}'
