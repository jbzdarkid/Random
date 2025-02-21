# Jesus christ, python
from pathlib import Path
from pydoc import importfile
src_api_file = Path(__file__).parent.parent / 'source/src_apis.py'
src_apis = importfile(str(src_api_file))

api = src_apis.api

import requests

def login():
  # https://www.speedrun.com/darkid/settings/api
  headers = {'X-API-Key': input('X-API-Key: ')}
  r = requests.get(f'{api}/profile', headers=headers)
  if r.status_code != 200:
    raise ValueError('Failed to authenticate')
  print('Authenticated as ' + src_apis.parse_name(r.json()['data']))
  return headers

names = {}
def get_name(player_id):
  if player_id not in names:
    j = requests.get(f'{api}/users/{player_id}').json()
    names[player_id] = src_apis.parse_name(j['data'])

  return names[player_id]

def get_category_name(category_id):
  j = requests.get(f'{api}/categories/{category_id}').json()
  return j['data']['name']

def get_categories(game_id):
  j = requests.get(f'{api}/categories')

# From SpeedrunBot, copied because relative imports are apparently a mess
def get_runs(**params):
  return src_apis.get_runs(**params)
def search_src_user(username):
  return src_apis.search_src_user(username)
def get_game_id(game_name):
  return src_apis.get_game(game_name)
