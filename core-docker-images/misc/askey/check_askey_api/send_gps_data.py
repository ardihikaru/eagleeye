from suds.client import Client
import json

client = Client("http://10.194.188.105:36002/FlySocketWCF")
dict = {}
#dict["FlyNo"]="1000000076c62168"
#dict["FlyNo"]="ERROR000000000"
dict["FlyNo"]="1"
dict["lat"]="24.951213"
dict["lon"]="121.217068"
dict["Alt"]="10"
dict["Heading"]="360"
j = json.dumps(dict)
resp = client.service.SendPeopleLocation(j)
resp = ''.join(resp)
resp = json.loads(resp)
print(type(resp))
print(resp)