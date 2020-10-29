# -*- coding: utf-8 -*-
from suds.client import Client
import json
# wcf Address
client = Client('http://10.194.188.105:36002/FlySocketWCF')
print(client)
AllDroneState = client.service.GetAllDroneState()
print(AllDroneState) # GetAllDroneState()


"""
dict = {}
dict['FlyNo'] = 'ERROR000000000'
dict['lat'] = '25.0334931'
dict['lon'] = '121.5641012'
dict['Alt'] = '12'
#print(dict)  
j = json.dumps(dict)
print(client.service.SendPeopleLocation(j))
"""

