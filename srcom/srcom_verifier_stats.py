import requests
import utils

# Get game ID by name:
# https://www.speedrun.com/api/v1/games?name=The%20Witness

runs = utils.get_runs('ldegnl13')

runs.sort(key=lambda run: run['submitted'], reverse=True)
print()

def count_statistics(runs):
  counts = {}
  for run in runs:
    if 'examiner' not in run['status']:
      continue # Runs which have not yet been verified

    verifier = run['status']['examiner']
    if verifier not in counts:
      counts[verifier] = 1
    else:
      counts[verifier] += 1
  sorted_counts = [(utils.get_name(verifier), counts[verifier], round(counts[verifier] / len(runs) * 100, 2)) for verifier in counts]
  sorted_counts.sort(key=lambda s: s[1], reverse=True)
  return sorted_counts

stats = count_statistics(runs[:100])
for verifier, count, perc in stats:
  print(f'{verifier} has verified {count} of the past 100 runs')

print()

stats = count_statistics(runs)
for verifier, count, perc in stats:
  print(f'{verifier} has verified {perc}% of all runs')

