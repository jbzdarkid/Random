import sys
from struct import unpack

from amfparser import Bytes

def to_hex_str(num, len=8):
  import builtins
  # TODO: return '0x' + builtins.hex(num)[2:].upper()
  return '0x' + builtins.hex(num)[2:].upper().zfill(len)

from pathlib import Path
home = Path.home()

savefiles = []

for folder in [
  f'{home}/Library/Application Support/Google/Chrome/Default/Pepper Data/Shockwave Flash/WritableRoot/#SharedObjects',
  f'{home}/Library/Preferences/Macromedia/Flash Player/#SharedObjects',
  f'{home}/AppData/Local/Google/Chrome',
  f'{home}/AppData/Macromedia/Flash Player/#SharedObjects',
  f'{home}/AppData/Local/Chromium/User Data/Default/Pepper Data/Shockwave Flash/WritableRoot/#SharedObjects',
]:
  savefiles += Path(folder).glob('**/MARDEKv3__sg_*.sol')
savefiles.sort()

for file in savefiles:
  print(f'\nSave file {file.name}')
  b = Bytes(file)
  b.seek(b'playtime')
  print('Playtime: %d:%02d:%02d' % b.amf0_read())

  b.seek(b'PCloc')
  x, y, map_name = b.amf0_read()
  map_name = map_name
  print(map_name.encode('utf-8'))
  if player_loc := input('Set player location (Currently at [%d, %d] in %s): ' % (x, y, map_name)):
    if player_loc.count(' ') == 0:
      map_name = player_loc
    elif player_loc.count(' ') == 1:
      x, y = player_loc.split(' ')
    elif player_loc.count(' ') == 2:
      x, y, map_name = player_loc.split(' ')
    else:
      raise ValueError('Error: Expected "map_name", "X Y", or "X Y map_name"')
    b.seek(b'PCloc')
    b.amf0_write([int(x), int(y), map_name])

  b.seek(b'GAME_NAME')
  game_name = b.amf0_read()
  if game_name := input('Change game name? (Currently: "%s"): ' % game_name):
    b.seek(b'GAME_NAME')
    b.amf0_write(game_name)

  if clear_maps := input('Change maps? ("Hide"/"Show"/""): '):
    rle_char = 'Y' if (clear_maps.lower()[0] == 's') else 'N'
    b.seek(b'Maps')
    maps = b.amf0_read()
    for name, rle in maps.items():
      width, height = map(int, rle.split('|')[0].split('_'))
      maps[name] = rle.split('|')[0] + f'|{width * height}{rle_char}'
    b.seek(b'Maps')
    b.amf0_write(maps)
  b.write_to_disk()

