import requests
import json


keys_json = open('config/keys.json', 'r').read()
keys = json.loads(keys_json)
cx_key = keys['cx_key']
api_key = keys['api_key']

response = requests.get(
    'https://customsearch.googleapis.com/customsearch/v1',
    params={'cx': cx_key,
            'lr': 'lang_en',
            'num': 5,
            'q': 'who%20invented%20the%20radio',
            'key': api_key}
)

json_response = response.json()

print(json_response)