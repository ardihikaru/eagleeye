curl --location --request POST 'http://localhost:8080/api/nodes' \
    --header 'Content-Type: application/json' \
    --data '{
        "candidate_selection": true,
        "persistence_validation": true
    }'
echo "Regestering a new node succeed"