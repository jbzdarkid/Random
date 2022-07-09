import requests
import datetime
import utils
import time

# src_id = utils.search_src_user(input('Enter your Speedrun.com username: '))
# print(f'Found Speedrun.com user {src_id}')
# runs = utils.get_runs(user=src_id, orderby='date', direction='asc')

game_id = utils.get_game_id(input('Enter the Speedrun.com game: '))
print(f'Found Speedrun.com game {game_id}')
runs = utils.get_runs(game=game_id, orderby='date', direction='asc')

for run in runs:
  if not run.get('videos') or 'links' not in run['videos']:
    continue

  video = run['videos']['links'][0]['uri']
  if 'youtube' not in video and 'youtu.be' not in video:
    continue

  submitted = datetime.datetime.strptime(run['submitted'], '%Y-%m-%dT%H:%M:%SZ')
  submitted = submitted.replace(tzinfo=datetime.timezone.utc) # strptime assumes local time, which is incorrect here.
  if submitted >= datetime.datetime(2017, 1, 1, tzinfo=datetime.timezone.utc):
    continue

  time.sleep(0.1)
  if utils.is_video_unlisted(video):
    weblink = run['weblink']
    print(f'Run from {submitted} is unlisted and will become private: <{weblink}> <{video}>')
print('Done processing runs')
