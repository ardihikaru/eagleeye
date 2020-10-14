curl --location --request POST 'http://127.0.0.1:31000/api/stream/live' \
--data-raw '{
    "algorithm": "YOLOv3",
    "stream": true,
    "uri": "rtsp://140.113.86.98:40000/test",
    "scalable": true
}'
