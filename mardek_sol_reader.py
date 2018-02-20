from struct import unpack
from os import walk, sep
from os.path import expanduser
from re import search

shared_objects_dirs = [
  'Library/Application Support/Google/Chrome/Default/Pepper Data/Shockwave Flash/WritableRoot/#SharedObjects',
  'Library/Preferences/Macromedia/Flash Player/#SharedObjects',
  'AppData\Local\Google\Chrome',
  'AppData\Macromedia\Flash Player\#SharedObjects',
]

savefiles = []
for shared_objects_dir in shared_objects_dirs:
  for root, dirs, files in walk(expanduser('~')+sep+shared_objects_dir):
    for file in files:
      if file[:13] == 'MARDEKv3__sg_':
        savefiles.append((root.split(sep)[-1], int(file[13:-4]), root+sep+file))

savefiles.sort()
for dir, file_num, path in savefiles:
  f = open(path, 'rb').read()
  # 8 represents array, 0003 means 3 elements
  m = search('playtime\x08\x00\x00\x00\x03(.{36})', f)
  if m:
    print 'Save file %d from "%s":' % (file_num, dir),
    print '\t%d:%02d:%02d' % unpack('>4xd4xd4xd', m.group(1))
