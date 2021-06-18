import requests
import json

# https://www.speedrun.com/darkid/settings/api
headers = {'X-API-Key': input('X-API-Key: ')}
r = requests.get('https://www.speedrun.com/api/v1/profile', headers=headers)
if r.status_code != 200:
  raise ValueError('Failed to authenticate')
print('Authenticated as ' + r.json()['data']['names']['international'])

# Get game ID by name:
# https://www.speedrun.com/api/v1/games?name=The%20Witness
# Get categories for game:
# https://www.speedrun.com/api/v1/games/ldegnl13/categories
# Get variables for game:
# https://www.speedrun.com/api/v1/games/ldegnl13/variables

old_category = 'wk6v41od' # Old 20CC
new_category = 'wk60q5pk' # New 20CC
params = {'category': old_category, 'offset': 0}

# Old string: new string. Use the same dictionary for keys and values.
variable_remap = {
  'ql64y7v8': '68km513l',
  '9qj438oq': 'z194284l',
  'jq6xdeoq': '814xo7kq',
}

runs = []

def nonnull(value):
  return '' if (value is None) else value

while True:
  j = requests.get('https://www.speedrun.com/api/v1/runs', params=params).json()
  for d in j['data']:
    if d['status']['status'] != 'verified':
      raise ValueError('Run is not verified: ' + d['status'])

    run = {
      'category': new_category,
      'verified': True, # Will automatically set verifier + current date as verification time

      # User data
      'times': {
        'realtime': d['times']['realtime_t'],
        'realtime_noloads': d['times']['realtime_noloads_t'],
        'ingame': d['times']['ingame_t'],
      },
      'players': d['players'], # Runner
      'date': d['date'], # Date played
      'video': d['videos']['links'][0]['uri'], # Submission video
      'comment': nonnull(d['comment']), # Description

      'platform': d['system']['platform'],
      'emulated': d['system']['emulated'],
    }

    if d['level']: # For ILs, not in use for the witness
      run['level'] = d['level']

    if d['system']['region']:
      run['region'] = d['system']['region']

    if d['splits'] and d['splits']['rel'] == 'splits.io':
      run['splitsio'] = d['splits']['uri'].rsplit('/', 1)[1]

    run['variables'] = {}
    for var_name, var_value in d['values'].items():
      var_name = variable_remap.get(var_name, var_name)
      var_value = variable_remap.get(var_value, var_value)

      run['variables'][var_name] = {'type': 'pre-defined', 'value': var_value}

    
    runs.append(run)

  if j['pagination']['links'][0]['rel'] == 'next':
    params['offset'] += 20
  else:
    break


# Sort the runs so that the top times are entered first. This will generate a minimum of notification emails ("Your Top-3 run was beaten")
runs.sort(key=lambda run: run['times']['realtime'])

# !!! Warning !!!
# This does not deduplicate runs. If you run this twice (or run it again, after an error) it *will* happily re-upload all of the existing runs,
# and you will get duplicates. Future work should include *not* uploading a run if it matches on category && runner && time.

for run in runs:
  r = requests.post('https://www.speedrun.com/api/v1/runs', headers=headers, data=json.dumps({'run': run}))
  if r.status_code == 201:
    print(r.json())
  else:
    print('Failed to upload the run:', r.status_code)
    print('Message:', r.json()['message'])
    print('Errors:', r.json()['errors'])
    break

