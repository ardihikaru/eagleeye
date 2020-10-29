curl --location --request POST 'http://140.113.86.92:31000/api/stream/live' \
--data-raw '{
    "algorithm": "YOLOv3",
    "stream": true,
    "uri": "rtsp://10.194.188.106/1028",
    "scalable": true
}'
