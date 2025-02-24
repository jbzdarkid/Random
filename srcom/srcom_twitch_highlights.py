import sys
import utils

from SpeedrunBot.source import src_apis

if len(sys.argv) < 1:
  game_name = input('Enter the Speedrun.com game: ')
else:
  game_name = sys.argv[1]
game_id = utils.get_game_id(game_name)
print(f'Parsing Speedrun.com game {game_name} ({game_id})')


# There are two kinds of runs that we care about retaining: PBs and WRs.
# For PBs, we just care about the best time per user. (iterate all runs, track best per user)
# For WRs, we care about the best run at a given moment in time. (iterate all runs in order, track decrementing times)
data = {}
runs = utils.get_runs(game=game_id, orderby='date', direction='asc')
for run in runs:
  category = utils.get_full_category(run)
  if category not in data:
    data[category] = {'pbs': {}, 'wrs': []}
  pbs = data[category]['pbs']
  wrs = data[category]['wrs']

  players = ', '.join([src_apis.parse_name(player) for player in run['players']['data']])
  run_time = run['times']['primary_t']
  if players not in pbs:
    pbs[players] = run
  elif run_time < pbs[players]['times']['primary_t']:
    pbs[players] = run
    
  if len(wrs) == 0:
    wrs.append(run)
  elif run_time < wrs[-1]['times']['primary_t']:
    wrs.append(run)

for category in sorted(data.keys()):
  print('\t\tCategory', category)

  pbs = list(data[category]['pbs'].values())
  pbs.sort(key = lambda run: run['times']['primary_t'])
  print(f'\tCurrent leaderboard ({len(pbs)} PBs):')
  for run in pbs:
    video = run['videos']['links'][0]['uri']
    if 'twitch' in video:
      print('[TWITCH VOD] ', end='')
    print(utils.run_to_short_string(run))

  wrs = data[category]['wrs']
  print(f'\tWR timeline ({len(wrs)} WRs):')
  for run in wrs:
    if 'text' in run['videos']:
      video = run['videos']['text']
    elif 'links' in run['videos']:
      video = run['videos']['links'][0]['uri']
    else:
      video = None

    if 'twitch' in video:
      print('[TWITCH VOD] ', end='')
    print(utils.run_to_short_string(run))
