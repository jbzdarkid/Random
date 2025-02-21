import requests
import datetime
import utils
import time

# src_id = utils.search_src_user(input('Enter your Speedrun.com username: '))
# print(f'Found Speedrun.com user {src_id}')
# runs = utils.get_runs(user=src_id, orderby='date', direction='asc')

game_id = utils.get_game_id(input('Enter the Speedrun.com game: '))
print(f'Found Speedrun.com game {game_id}')

categories = utils.get_categories(game_id)
for category in categories:
  runs = utils.get_runs(game=game_id, category=category, orderby='date', direction='asc')

  # There are two kinds of runs that we care about retaining: PBs and WRs.
  # For PBs, we just care about the best time per user. (iterate all runs, track best per user)
  # For WRs, we care about the best run at a given moment in time. (iterate all runs in order, track decrementing times)
  pbs = {}
  wrs = []

  for run in runs:
    players = set(parse_name(player) for player in new_run['players']['data'])
    run_time = run['times']['primary_t']
    if players not in pbs:
      pbs[players] = run
    elif run_time < pbs[players]['times']['primary_t']:
      pbs[players] = run

    if run_time < wrs[-1]['times']['primary_t']:
      wrs.append(run)

  print(pbs)
  print(wrs)
  input()
