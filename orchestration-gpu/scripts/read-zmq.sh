curl --location --request POST 'http://140.113.86.92:31000/api/stream/live' \
--data-raw '{
    "algorithm": "YOLOv3",
    "stream": "TCP",
    "uri": "140.113.86.92:31210",
    "scalable": true
}'
