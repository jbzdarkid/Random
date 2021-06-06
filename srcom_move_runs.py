import requests

# https://www.speedrun.com/darkid/settings/api
headers = {'X-API-Key': input('X-API-Key: ')}
r = requests.get('https://www.speedrun.com/api/v1/profile', headers=headers)
if r.status_code != 200:
  raise ValueError('Failed to authenticate')
print('Authenticated as ' + r.json()['data']['names']['international'])

# Get game ID by name:
# https://www.speedrun.com/api/v1/games?name=The%20Witness
# Get categorys for game:
# https://www.speedrun.com/api/v1/games/ldegnl13/categories

# Old 20CC
r = requests.get('https://www.speedrun.com/api/v1/runs?category=wk6v41od')

new_category = '' # New 20CC

runs = r.json()['data']
for d in r.json()['data']:
  run = {
    # Constant data
    'category': new_category,
    'level': d['level'],

    # System data
    'verified': false, # TODO

    # User data
    'times': d['times'],
    'players': d['players'],
    'date': d['date'],
    'video': d['videos']['links'][0]['uri'],
    'comment': d['comment'],
    'variables': {},

    'region': d['system']['region'],
    'platform': d['system']['platform'],
    'emulated': d['system']['emulated'],

    'status': d['status'], # Auto verification comes in here
    'submitted': d['submitted'],

    'date_played': d['date'],
    'date_submitted': d['submitted'],
  }
  if d['splits'] and d['splits']['rel'] == 'splits.io':
    run['splitsio'] = d['splits']['uri'].rsplit('/', 1)[1]
  for var_name, var_value in d['values'].iter():
    run['variables'][var_name] = {'type': 'pre-defined', 'value': var_value}

  
  runs.append(run)

# Then post to /runs, and pray it works.
