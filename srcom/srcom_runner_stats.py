import requests

# Get game ID by name:
# https://www.speedrun.com/api/v1/games?name=The%20Witness

params = {'game': 'ldegnl13', 'offset': 0}

runs = []
while True:
  j = requests.get('https://www.speedrun.com/api/v1/runs', params=params).json()
  runs += j['data']
  print(f'Found {len(runs)} runs')

  if any(link['rel'] == 'next' for link in j['pagination']['links']):
    params['offset'] += 20
  else:
    break

runs.sort(key=lambda run: run['submitted'])

names = {}

runners = []
run_counts = {}

for run in runs:
  if 'id' in run['players'][0]:
    runner = run['players'][0]['id']
  else:
    runner = run['players'][0]['name'] # Guests
    names[runner] = runner
    runners.append((runner, run['submitted']))
    run_counts[runner] = 1

  if runner not in names:
    j = requests.get(f'https://www.speedrun.com/api/v1/users/{runner}').json()
    names[runner] = j['data']['names']['international']

    runners.append((runner, run['submitted']))
    run_counts[runner] = 1
  else:
    run_counts[runner] += 1

runners.sort(key=lambda s: s[1])
for runner, date in runners:
  if run_counts[runner] >= 5:
    print(f'Runner {names[runner].ljust(20)} first submitted on {date}, has a total of {run_counts[runner]} runs')


