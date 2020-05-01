import zipfile
import os.path
import lz4.frame

ROOT = 'C:/Program Files (x86)/Steam/steamapps/common/The Witness/data-pc'
TMP = os.path.dirname(os.path.abspath(__file__)) + '/tmp'
if not os.path.isdir(TMP):
  os.mkdir(TMP)

def fix_file(data):
  remainder = data[12:]
  datalen = len(remainder)

  B0 = datalen & 0xFF
  B1 = (datalen >> 8) & 0xFF
  B2 = (datalen >> 16) & 0xFF
  B3 = (datalen >> 24) & 0xFF

  #0x18 4C 21 02
  prefix = [0x02, 0x21, 0x4C, 0x18, B0, B1, B2, B3]

  final_data = prefix + list(remainder)
  return bytearray(final_data)

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
    # with open(dest, 'wb') as f:
    #   f.write(data[offset:])
    os.remove(file)
  elif audio_type == 'wav':
    # data = fix_file(data)
    # decompressed = lz4.frame.decompress(data)
    # decompressed = decompressed[4:]
    
    pass



def extract_sounds(package):
  for file in package.namelist():
    if not file.endswith('sound'):
      continue
    package.extract(file, path=TMP)
    convert(TMP + '/' + file)
    
if __name__ == '__main__':
  package = zipfile.ZipFile(ROOT + '.zip')
  extract_sounds(package)
  for file in package.namelist():
    if not file.endswith('pkg'):
      continue
    package.extract(file, path=TMP)
    subpackage = zipfile.ZipFile(TMP + '/' + file)
    extract_sounds(subpackage)
    subpackage.close()
    os.remove(TMP + '/' + file)
  package.close()
