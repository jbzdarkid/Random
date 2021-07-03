import requests

def login():
  # https://www.speedrun.com/darkid/settings/api
  headers = {'X-API-Key': input('X-API-Key: ')}
  r = requests.get('https://www.speedrun.com/api/v1/profile', headers=headers)
  if r.status_code != 200:
    raise ValueError('Failed to authenticate')
  print('Authenticated as ' + r.json()['data']['names']['international'])
  return headers

def get_runs(**params):
  params['offset'] = 0
  if 'game' not in params and 'category' not in params:
    raise ValueError('get_runs needs either a game or a category')

  runs = []
  while 1:
    j = requests.get('https://www.speedrun.com/api/v1/runs', params=params).json()
    runs += j['data']
    print(f'Found {len(runs)} runs')

    if any(link['rel'] == 'next' for link in j['pagination']['links']):
      params['offset'] += 20
    else:
      break

  return runs

names = {}
def get_name(player_id):
  if player_id not in names:
    j = requests.get(f'https://www.speedrun.com/api/v1/users/{player_id}').json()
    names[player_id] = j['data']['names']['international']

  return names[player_id]

def get_category_name(category_id):
  j = requests.get(f'https://www.speedrun.com/api/v1/categories/{category_id}').json()
  return j['data']['name']

