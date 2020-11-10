curl --location --request POST 'http://140.113.86.92:31000/api/stream/live' \
--data-raw '{
    "algorithm": "YOLOv3",
    "stream": true,
    "uri": "/app/data/5g-dive/videos/mission-2_1.mp4",
    "scalable": true
}'
