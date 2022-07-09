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
  params['max'] = 100 # Undocumented parameter, gets 100 runs at once.
  if not (params.keys() & {'game', 'category', 'user'}):
    raise ValueError('You need a primary search type to get runs from Speedrun.com')

  runs = []
  j = requests.get('https://www.speedrun.com/api/v1/runs', params=params).json()
  while 1:
    runs += j['data']
    if 'limit' in params and len(runs) > params['limit']:
      break

    for link in j['pagination']['links']:
      if link['rel'] == 'next':
        j = requests.get(link['uri']).json()
        continue
    break # No more results

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

def is_video_unlisted(video_url):
  # allow_redirects=True
  r = requests.get(video_url)
  return '<meta itemprop="unlisted" content="True">' in r.text

# From SpeedrunBot
def search_src_user(username):
  j = requests.get('https://www.speedrun.com/api/v1/users', params={'name': username}).json()
  if len(j['data']) == 0:
    raise ValueError(f'Could not find user {username} on Speedrun.com')

  if len(j['data']) == 1:
    return j['data'][0]['id']

  possible_matches = []
  for user in j['data']:
    possible_match = user['names']['international']
    if possible_match == username:
      return user['id']
    possible_matches.append(possible_match)

  suggestions = ', '.join(possible_matches[:10]) # Only show a max of 10 matches, for brevity's sake
  raise ValueError(f'Found {len(possible_matches)} possible matches for user {username} on Speedrun.com -- Try one of these options:\n' + suggestions)

def get_game_id(game_name):
  j = requests.get('https://www.speedrun.com/api/v1/games', params={'name': game_name}).json()
  if len(j['data']) == 0:
    raise ValueError(f'Could not find game {game_name} on Speedrun.com')

  if len(j['data']) == 1:
    return j['data'][0]['id']

  possible_matches = []
  for game in j['data']:
    possible_match = game['names']['twitch']
    if possible_match == game_name:
      return game['id']
    possible_matches.append(possible_match)

  suggestions = ', '.join(possible_matches[:10]) # Only show a max of 10 matches, for brevity's sake
  raise ValueError(f'Found {len(possible_matches)} possible matches for game {game_name} on Speedrun.com -- Try one of these options:\n' + suggestions)

