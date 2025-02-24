from datetime import timedelta
import requests

from SpeedrunBot.source import src_apis
api = src_apis.api

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
  j = requests.get(f'{api}/games/{game_id}/categories').json()
  return j['data']

# The first half of src_apis.run_to_string
def run_to_short_string(run):
  category = run['category']['data']['name']

  if isinstance(run['level']['data'], dict):
    category = run['level']['data']['name'] + f': {category}'

  subcategories = src_apis.get_subcategories(run)
  for value in subcategories.values():
    category += f' ({value["label"]})'

  time = timedelta(seconds=run['times']['primary_t'])
  runners = ', '.join(map(src_apis.parse_name, run['players']['data']))
  return f'{time} by {runners}: {run["weblink"]}'

def get_runs(**params):
  return src_apis.get_runs(**params)

def search_src_user(username):
  return src_apis.search_src_user(username)

def get_game_id(game_name):
  return src_apis.get_game(game_name)['id']

def get_full_category(run):
  category = run['category']['data']['name']
  for subcategory in src_apis.get_subcategories(run).values():
    category += ' (' + subcategory['label'] + ')'
  return category
