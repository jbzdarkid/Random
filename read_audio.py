import zipfile
import os.path
import sys
from os import system, unlink
from os.path import splitext
import lz4

ROOT = 'C:/Program Files (x86)/Steam/steamapps/common/The Witness/data-pc'
TMP = os.path.dirname(os.path.abspath(__file__)) + '/tmp'
if not os.path.isdir(TMP):
  os.mkdir(TMP)


def convert(file):
  data = open(file, 'rb').read()

  start = str(data[:120])
  pos = start.find('RIFF')
  if pos > 16:
    audio_type = 'wav'
    offset = 12
  elif pos > -1:
    audio_type = 'wav'
    offset = 16
  elif 'Ogg' in start:
    audio_type = 'ogg'
    offset = 16
  else:
    raise Exception('Unknown format: {}'.format(file))
  
  dest = file.replace('sound', audio_type)
  
  if audio_type == 'ogg' or (audio_type == 'wav' and offset == 16):
    with open(dest, 'wb') as f:
      f.write(data[offset:])
    os.remove(file)
  elif audio_type == 'wav':
    pass # See https://gist.github.com/zlorf/4c29170d59e74a7667f6


  
  
"""
packages = [file for file in files if file.endswith('.pkg')]
for package in packages:
  z.extract(package, path=TMP)
  z2 = zipfile.ZipFile(TMP + '/' + package)
  
  sounds = [file for file in z2.namelist() if file.endswith('.sound')]
  
  # Do stuff with sounds here!
  os.remove(package)
  print(z2.namelist())
  exit()
"""

if __name__ == '__main__':
  z = zipfile.ZipFile(ROOT + '.zip')
  for file in z.namelist():
    if file.endswith('sound'):
      z.extract(file, path=TMP)
      convert(TMP + '/' + file)
    elif file.endswith('pkg'):
      z.extract(file, path=TMP)
      z2 = zipfile.ZipFile(TMP + '/' + file)
      for file in z2.namelist():
        if (file.endswith('sound')):
          z2.extract(file, path=TMP)
          convert(TMP + '/' + file)
