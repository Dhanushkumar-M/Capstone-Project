from boltiot import Bolt
api_key = "6166afe7-40a2-4de6-b173-fdbfc06534fa"
device_id  = "BOLT7421210"
mybolt = Bolt(api_key, device_id)
response = mybolt.isOnline()
print (response)
