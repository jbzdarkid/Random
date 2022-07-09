import requests
import sys

slug = sys.argv[1]
r = requests.get(f'https://api.twitch.tv/kraken/clips/{slug}', headers={'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': 'zs377ogpzz01ogfx26pvbddx9jodg1'})
data = r.json()
print(data['created_at'])
