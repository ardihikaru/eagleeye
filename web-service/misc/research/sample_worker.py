# importing os module
import os
import time
# importing the requests library
import requests
import argparse


# api-endpoint
URL = "http://localhost:8080/api/users"

# sending get request and saving the response as response object
r = requests.get(url=URL)

# extracting data in json format
data = r.json()

# Get the process ID of
# the current process
pid = os.getpid()

# Print the process ID of
# the current process
print(pid)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--node', type=int, default=1, help="Node ID")
    args = parser.parse_args()

    # time.sleep(30)
    max_data = 30
    for i in range(max_data):
        # sending get request and saving the response as response object
        r = requests.get(url=URL)
        # extracting data in json format
        data = r.json()
        print("Node: %s" % str(args.node), data, "\n")
        time.sleep(1)

    print(" --- pid closed. ..")
