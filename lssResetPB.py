import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def parse_time(date_string):
  parsed = None
  try:
    parsed = datetime.strptime(date_string, '%H:%M:%S.%f0')
  except:
    pass
  try:
    parsed = datetime.strptime(date_string, '%H:%M:%S')
  except:
    pass

  if not parsed:
    raise ValueError('Unable to parse: ' + date_string)

  return timedelta(
    hours = parsed.hour,
    minutes = parsed.minute,
    seconds = parsed.second,
    microseconds = parsed.microsecond
  )

def to_string(delta):
  dt = datetime(1970,1,1) + delta
  return datetime.strftime(dt, '%H:%M:%S.%f0')

tree = ET.parse('GGSD-original.lss')
root = tree.getroot()

xml_attempt_history = root.find('AttemptHistory')
xml_segments = root.find('Segments')

attempts = {}
for xml_attempt in xml_attempt_history:
  if len(xml_attempt) == 0:
    continue # Only consider completed attempts
  data = {
    'id': xml_attempt.attrib['id'],
    'cumulative': timedelta(),
    'segments': [],
  }
  attempts[data['id']] = data

for xml_segment in xml_segments:
  for xml_attempt in xml_segment.find('SegmentHistory'):
    id = xml_attempt.attrib['id']
    if id not in attempts:
      continue
    if len(xml_attempt) == 0:
      attempts[id]['segments'].append(None)
      continue
    time = parse_time(xml_attempt.find('RealTime').text)
    attempts[id]['cumulative'] += time
    attempts[id]['segments'].append(attempts[id]['cumulative'])

pb = timedelta(hours=9999)
for k in attempts:
  if attempts[k]['cumulative'] < pb:
    pb_id = k
    pb = attempts[k]['cumulative']

for xml_attempt in xml_attempt_history:
  if len(xml_attempt) == 0:
    continue # Only consider completed attempts
  xml_attempt.find('RealTime').text = to_string(attempts[data['id']]['cumulative'])

for i in range(len(xml_segments)):
  split_time = xml_segments[i].find('SplitTimes').find('SplitTime')
  real_time = split_time.find('RealTime')

  pb_segment = attempts[pb_id]['segments'][i]
  if pb_segment is None: # Skipped split in PB
    split_time.remove(real_time)
  else:
    real_time.text = to_string(pb_segment)

tree.write('GGSD-mod.lss')
