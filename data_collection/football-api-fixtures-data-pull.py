#may not work if you are running with my API key. Also, please keep requests to API under 100 per day otherwise I will be charged.
import json
import pandas as pd 
import requests

url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/headtohead"

querystring = {"h2h":"33-34"}

headers = {
	"x-rapidapi-key": "d08c3e16d9msh152683b9720f95ep1f9bb1jsncc3d4fdac85f",
	"x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

# print(response.json())

data = response.json()
fixtures = data['response'][1:]

df = pd.json_normalize(fixtures)

df.head()
