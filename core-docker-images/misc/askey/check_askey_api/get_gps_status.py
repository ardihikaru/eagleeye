from suds.client import Client
import json
# wcf Address
client = Client('http://10.194.188.105:36002/FlySocketWCF')
print(client)
AllDroneState = client.service.GetAllDroneState()
AllDroneState = ''.join(AllDroneState)
AllDroneState = json.loads(AllDroneState)
print(AllDroneState)
print(type(AllDroneState))
print(len(AllDroneState))
print(type(AllDroneState[0]))
print(AllDroneState[0])
#AllDroneState = list(AllDroneState)
#AllDroneState = list(str(AllDroneState))
#print(type(AllDroneState))
#print(AllDroneState) # GetAllDroneState()