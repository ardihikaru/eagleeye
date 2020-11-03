printf "\n>>> Trying to register a new node . . . \n\n"

curl --location --request POST 'http://localhost:8080/api/nodes' \
    --header 'Content-Type: application/json' \
    --data '{
        "candidate_selection": true,
        "persistence_validation": true
    }'

printf "\n\n>>> Regestering a new node succeed\n\n"