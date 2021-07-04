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
#     savefiles =
#     if file.name[:13] == '':
#       savefiles.append((file))
#       print(file.relative_to(folder).parts[0])
#       # root.split(sep)[-1] would be the final path segment of the root folder -- the first segment after the folder above
#       # file[13:-4] is stripping the save game number, this is unchanged
#       # root + sep + file is the full path.
#       # savefiles.append((root.split(sep)[-1], int(file[13:-4]), root+sep+file))

savefiles.sort()

for file in savefiles:
  print(f'\nSave file {file.name}')
  b = Bytes(file)
  if sys.argv[1] == 'read':
    b.seek(b'PCloc')
    print('Player location: (%d, %d) in %s' % b.amf0_read())
    b.seek(b'GAME_NAME')
    print('Game name: %s' % b.amf0_read())
    b.seek(b'playtime')
    print('Playtime: %d:%02d:%02d' % b.amf0_read())
  elif sys.argv[1] == 'write':
    if game_name := input('Game name: '):
      b.seek(b'GAME_NAME')
      b.amf0_write(game_name)
    if player_loc := input('Player location "X Y" or "X Y map_name": '):
      if player_loc.count(' ') == 1:
        b.seek(b'PCloc')
        _, _, map_name = b.amf0_read()
        x, y = map(int, player_loc.split(' '))
      elif player_loc.count(' ') == 2:
        x, y, map_name = player_loc.split(' ')
        x = int(x)
        y = int(y)
      else:
        raise ValueError('Bad space count. Provide "X Y" or "X Y map_name"')
      b.seek(b'PCloc')
      b.amf0_write([x, y, map_name])
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
