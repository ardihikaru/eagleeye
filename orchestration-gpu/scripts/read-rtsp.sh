curl --location --request POST 'http://127.0.0.1:31000/api/stream/live' \
--data-raw '{
    "algorithm": "YOLOv3",
    "stream": true,
    "uri": "rtsp://192.168.1.250/0137",
    "scalable": true
}'
