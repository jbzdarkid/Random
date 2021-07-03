import requests
import utils

runs = utils.get_runs(game='ldegnl13', status='new')
announced_runs = set()
for run in runs:
  if run['id'] not in announced_runs:
    weblink = run['weblink']
    category = utils.get_category_name(run['category'])
    time = str(run['times']['realtime_t'] // 60) + ':' + str(run['times']['realtime_t'] % 60).zfill(2)
    user = utils.get_name(run['players'][0]['id'])
    print(f'New run submitted: {category} in {time} by {user}: <{weblink}>')

    announced_runs.add(run['id'])

