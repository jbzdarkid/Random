want = '''
[Cloud]: SUCCEESS retrieved cfg/config.cfg from remote storage into cfg/config.cfg
[Cloud]: SUCCEESS saving cfg/config.cfg in remote storage
Damage Given to "***" - ** in * hits
Global search time avg:   ***
Host_WriteConfiguration: Wrote cfg/config.cfg
Server reservation check 0x*** will not queue connect
Server reservation2 is awaiting *
SetConVar: *** = "0"
Votes: Option1 - *, Option2 - *, Option3 - 0, Option4 - 0, Option5 - 0
PopulateLevelInfo: de_dust2 classic casual
'''

notwant = '''
-------------------------
  Attempted to attach particle effect weapon_muzzle_flash_assaultrifle_fallback to an unknown attachment on entity predicted_viewmodel
  Avatar image for user *** cached [refcount=1]
  Avatar image for user *** released [refcount=1]
  CScaleformComponent_ImageCache evicting avatar ***
  Damage Taken from "***" - ** in * hits
  Restarting sound playback
  Shutdown 2 predictable entities and 0 client-created entities
  Unknown command: -pref_lookataweapon
Bad sequence in GetSequenceName() for model \'weapons\\***.mdl\'!
Inventory image for item *** released [refcount=0]
'''

chars = {}
for line in want.split('\n'):
	line_chars = set(line)
	for char in line_chars:
		if char not in chars:
			chars[char] = 0
		chars[char] += 1

ordered_chars = []
for k, v in zip(chars.keys(), chars.values()):
	ordered_chars.append([v, k])
ordered_chars.sort()
for [k, v] in ordered_chars:
	print v, k

raw_input()
pairs = {}
for line in want.split('\n'):
	line_pairs = set()
	for i in range(len(line)-1):
		pair = line[i]+line[i+1]
		line_pairs.add(pair)
	for pair in line_pairs:
		if pair not in pairs:
			pairs[pair] = 0
		pairs[pair] += 1

for line in notwant.split('\n'):
	line_pairs = set()
	for i in range(len(line)-1):
		pair = line[i]+line[i+1]
		line_pairs.add(pair)
	for pair in line_pairs:
		if pair not in pairs:
			pairs[pair] = 0
		pairs[pair] -= 1

ordered_pairs = []
for k, v in zip(pairs.keys(), pairs.values()):
	ordered_pairs.append([v, k])
ordered_pairs.sort()
for [k, v] in ordered_pairs:
	print k, v