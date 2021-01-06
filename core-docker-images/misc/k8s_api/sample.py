"""
Source: https://kubernetes.io/docs/tasks/administer-cluster/access-cluster-api/

How to use:
1. turn on k8s API: `kubectl proxy --port=8082 &`
2. Run this script
"""

import kubernetes.client

#from __future__ import print_function
import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
import json

# https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
from bson import json_util

configuration = kubernetes.client.Configuration()
# Configure API key authorization: BearerToken
configuration.api_key['authorization'] = 'YOUR_API_KEY'  # currently not being used
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['authorization'] = 'Bearer'

# Defining host is optional and default to http://localhost
configuration.host = "http://localhost:8082"

# Defining host is optional and default to http://localhost
configuration.host = "http://localhost:8082"

# Enter a context with an instance of the API kubernetes.client
with kubernetes.client.ApiClient(configuration) as api_client:
	# Create an instance of the API class
	api_instance = kubernetes.client.CoreV1Api(api_client)

	try:
		api_response = api_instance.list_endpoints_for_all_namespaces()
		# api_response = api_instance.list_service_for_all_namespaces()
		# api_response = api_instance.list_service_for_all_namespaces(allow_watch_bookmarks=allow_watch_bookmarks, _continue=_continue, field_selector=field_selector, label_selector=label_selector, limit=limit, pretty=pretty, resource_version=resource_version, timeout_seconds=timeout_seconds, watch=watch)
		# pprint(api_response)
		api_response = api_response.to_dict()
		print(type(api_response))
		print(api_response)
		with open('api_response.json', 'w') as f:
			json.dump(api_response, f, default=json_util.default)
		# json_data = json.loads(api_response)
	except ApiException as e:
		print("Exception when calling CoreV1Api->list_service_for_all_namespaces: %s\n" % e)