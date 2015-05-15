from threading import Lock, Thread

must_hit = '''
Damage Given to "***" - ** in * hits
Votes: Option1 - *, Option2 - *, Option3 - 0, Option4 - 0, Option5 - 0
'''.split('\n')[1:-1]

hit = '''
*** connected.
Confirmation number *** for *** (**/*) (* tokens)
Damage Taken from "World" - ** in 1 hit
Host_newgame on de_***
Lobby data: game:map = de_***
map de_***
Matchmaking abandon notification: */***.**.***.**:27***/***
PopulateLevelInfo: de_*** classic ***
SetConVar: *** = "*"
'''.split('\n')[1:-1]

must_miss = '''
Avatar image for user *** cached [refcount=*]
Avatar image for user *** released [refcount=*]
Bad sequence in GetSequenceName() for model \'weapons\\v_***.mdl\'!
CScaleformComponent_ImageCache evicting avatar ***
'''.split('\n')[1:-1]

miss = '''
-------------------------
0: Reinitialized * predictable entities and * client-created entities
Notification CDN download result: ok (code: 200, size: 2)...
Player: *** - Damage Taken
Shutdown * predictable entities and 0 client-created entities
SignalXWriteOpportunity(*)
Unknown command: ***
'''.split('\n')[1:-1]

search = set()
for line in hit+miss+must_hit+must_miss:
	for i in range(len(line)):
		for j in range(i-3, i):
			substring = line[j:i].lower()
			if substring.find('*')+1:
				continue
			if substring not in search:
				search.add(substring)

output = []
threads = []
lock = Lock()

def test_line(filter, filter_out, line):
	line = line.lower()
	if line.find(filter_out)+1:
		return 3 # Text is filtered out.
	if line.find(filter)+1:
		return 2 # Text is visible on-screen.
	else:
		return 1 # Text is visible in console.

for filter in search:
	for filter_out in search:
		score = (len(filter)+len(filter_out))**1.5
	
		skip = False
		for line in must_hit:
			ret = test_line(filter, filter_out, line)
			if ret == 1 or ret == 3:
				skip = True
				break
		if skip:
			continue
		for line in must_miss:
			ret = test_line(filter, filter_out, line)
			if ret == 1:
				score -= 3
			if ret == 2:
				skip = True
				break
		if skip:
			continue
		for line in hit:
			ret = test_line(filter, filter_out, line)
			if ret == 1:
				score += 3
			if ret == 2:
				score += 6
		for line in miss:
			ret = test_line(filter, filter_out, line)
			if ret == 1:
				score -= 2
			if ret == 2:
				score -= 4
				
		if score > 0:
			output.append([score, filter, filter_out])

for o in sorted(output):
	print round(o[0], 1), 'con_filter_text "'+o[1]+'"; con_filter_text_out "'+o[2]+'"'
print len(output), 'valid options of', len(search)**2, 'possibilities.'
