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

runs.sort(key=lambda run: run['submitted'], reverse=True)
print()

verifier_names = {}

def count_statistics(runs):
  counts = {}
  for run in runs:
    if 'examiner' not in run['status']:
      continue # Runs which have not yet been verified

    verifier = run['status']['examiner']
    if verifier not in verifier_names:
      j = requests.get(f'https://www.speedrun.com/api/v1/users/{verifier}').json()
      verifier_names[verifier] = j['data']['names']['international']

    if verifier not in counts:
      counts[verifier] = 1
    else:
      counts[verifier] += 1
  sorted_counts = [(verifier_names[verifier], counts[verifier], round(counts[verifier] / len(runs) * 100, 2)) for verifier in counts]
  sorted_counts.sort(key=lambda s: s[1], reverse=True)
  return sorted_counts

stats = count_statistics(runs[:100])
for verifier, count, perc in stats:
  print(f'{verifier} has verified {count} of the past 100 runs')

print()

stats = count_statistics(runs)
for verifier, count, perc in stats:
  print(f'{verifier} has verified {perc}% of all runs')

