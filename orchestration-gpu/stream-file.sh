curl --location --request POST 'http://127.0.0.1:8080/api/stream/live' \
--data-raw '{
    "algorithm": "YOLOv3",
    "stream": true,
    "uri": "/app/data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4",
    "scalable": true
}'
