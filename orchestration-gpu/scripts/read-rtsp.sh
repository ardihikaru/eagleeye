curl --location --request POST 'http://10.194.188.112:8080/api/stream/live' \
--data-raw '{
    "algorithm": "YOLOv3",
    "stream": "STREAM",
    "uri": "rtsp://10.194.188.106/test",
    "scalable": true
}'
