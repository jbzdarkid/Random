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
  dt = datetime(1970, 1, 1) + delta
  return datetime.strftime(dt, '%H:%M:%S.%f0')

tree = ET.parse('The_Witness_-_Any.lss')
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

print('Found ' + str(len(attempts)) + ' completed attempts')

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
for id in list(attempts.keys()):
  if attempts[id]['cumulative'] == timedelta(seconds=0):
    del attempts[id]
    continue
  if attempts[id]['cumulative'] < pb:
    pb_id = id
    pb = attempts[id]['cumulative']

print('Detected PB on attempt #' + pb_id + ': ' + to_string(pb))

print('Updating final times for attempts...')
for xml_attempt in xml_attempt_history:
  id = xml_attempt.attrib['id']
  if id not in attempts:
    continue
  old_time = xml_attempt.find('RealTime').text
  new_time = to_string(attempts[id]['cumulative'])
  if not old_time == new_time:
    print('Updating attempt #' + id + ' from ' + old_time + ' to ' + new_time)
    xml_attempt.find('RealTime').text = new_time

print('Reprocessing splits...')
for i in range(len(xml_segments)):
  split_time = xml_segments[i].find('SplitTimes').find('SplitTime')
  real_time = split_time.find('RealTime')

  pb_segment = attempts[pb_id]['segments'][i]
  if pb_segment is None: # Skipped split in PB
    split_time.remove(real_time)
  else:
    old_time = real_time.text
    new_time = to_string(pb_segment)
    if not old_time == new_time:
      print('Updating split #' + str(i) + ' (' + xml_segments[i].find('Name').text + ') from ' + old_time + ' to ' + new_time)
      real_time.text = new_time

tree.write('The_Witness_-_Any.lss')
