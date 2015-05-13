from time import sleep
from threading import Lock, Thread

must_hit = '''
Damage Given to "***" - ** in * hits
Votes: Option1 - *, Option2 - *, Option3 - 0, Option4 - 0, Option5 - 0
'''.split('\n')[1:-1]

hit = '''
Confirmation number *** for *** (**/*) (* tokens)
Matchmaking abandon notification: */***.**.***.**:27***/***
map de_***
*** connected.
SetConVar: *** = "*"
'''.split('\n')[1:-1]

must_miss = '''
Avatar image for user *** cached [refcount=*]
CScaleformComponent_ImageCache evicting avatar ***
Avatar image for user *** released [refcount=*]
Bad sequence in GetSequenceName() for model \'weapons\\v_***.mdl\'!
'''.split('\n')[1:-1]

miss = '''
Unknown command: ***
Player: *** - Damage Given
Player: *** - Damage Taken
-------------------------
0: Reinitialized * predictable entities and * client-created entities
Shutdown * predictable entities and 0 client-created entities
'''.split('\n')[1:-1]


search = ''
for line in hit+miss+must_hit+must_miss:
	for char in line:
		if char.lower() not in search:
			search += char.lower()
search += ''
print search

output = []
threads = []
lock = Lock()

def t(char1):
	# State 0: Appears in console but not on screen.
	#		Matches neither
	# State 1: Appears in console and on screen.
	#		Matches filter
	# State 2: Does not appear.
	#		Matches filter out
	# State 3: Does not appear.
	#		Matches both
	if char1 == '*':
		return
	for char2 in search:
		for line in must_hit:
			line += '*'
			state = 0
			for i in range(len(line)-1):
				if state%2 == 0:
					if char1 == line[i].lower():
						if char2 == '*' or char2 == line[i+1].lower():
								state += 1
			breakOut = False
			if state != 1:
				breakOut = True
				break
		if breakOut:
			continue
		
		for char3 in search:
			if char3 == '*':
				continue
			for char4 in search:
				for line in must_miss:
					line += '*'
					state = 0
					for i in range(len(line)-1):
						if state%2 == 0:
							if char1 == line[i].lower():
								if char2 == '*' or char2 == line[i+1].lower():
										state += 1
						if state/2 == 0:
							if char3 == line[i].lower():
								if char4 == '*' or char4 == line[i+1].lower():
									state += 2
					breakOut = False
					if state == 1:
						breakOut = True
						break
				if breakOut:
					continue
				
				score = 0
				for line in hit:
					line += '*'
					state = 0
					for i in range(len(line)-1):
						if state%2 == 0:
							if char1 == line[i].lower():
								if char2 == '*' or char2 == line[i+1].lower():
									state += 1
						if state/2 == 0:
							if char3 == line[i].lower():
								if char4 == '*' or char4 == line[i].lower():
									state += 2
					if state == 1:
						score += 3
					if state == 0:
						score += 1
				
				for line in miss:
					line += '*'
					state = 0
					for i in range(len(line)-1):
						if state%2 == 0:
							if char1 == line[i].lower():
								if char2 == '*' or char2 == line[i+1].lower():
									state += 1
						if state/2 == 0:
							if char3 == line[i].lower():
								if char4 == '*' or char4 == line[i+1].lower():
									state += 2
					if state < 2:
						score -= 2
				
				if score >= 0:
					lock.acquire()
					settings = 'con_filter_text "'+char1
					if char2 != '*':
						settings += char2
					settings += '"; con_filter_text_out "'+char3
					if char4 != '*':
						settings += char4
					settings += '"'
					output.append([score, settings])
					lock.release()


for char1 in search:
	thread = Thread(target=t, kwargs={'char1':char1})
	threads.append(thread)
	thread.start()
	sleep(0.1)

for thread in threads:
	thread.join()

for o in sorted(output):
	print o[0], o[1]
print len(output), 'valid options'