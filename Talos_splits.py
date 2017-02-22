from __future__ import print_function
from time import sleep, time
from re import match

settings = {
    "Split on return to Nexus": True,
    "Split on tetromino collection": True,
    "Split on star collection": False,
    "Split on item unlocks": True,
    "Split on tetromino world doors": False,
    "Split on tetromino star doors": False,
    "Split on tetromino tower doors": True,
    "Split on star collection in the Nexus": False,
    "Split on completing C*": False, # Community% completion
    "Split on tetromino collection in A6": False,

    "(DLC) Split on return to Hub": True,
    "(DLC) Split on puzzle doors": False,
}

variables = {
    'currentWorld': "",
    'gameStarting': False,
    'introCutscene': False,
    'lastLines': 0,
    'doubleSplit': False,
    'totalLoads': 0.0,
    'adminEnding': False,
}

SPLITS = [
    ['A Switch out of Reach', 50.0, 30.0],
    ['Peephole', 20.0, 20.0],
    ['Only the Two of Us', 20.0, 20.0],
    ['Trio Bombasticus', 30.0, 20.0],
    ['Poking a Sleeping Lion', 30.0, 20.0],
    ['A1', 10.0, 10.0],
]
RUN_SPLITS = []

STATE = 'STOPPED'
TIMER = None
last_split = None
FILE = '/Users/joe/Library/Application Support/Steam/SteamApps/common/The Talos Principle/Log/Talos.log'

def update(line):
    # Intro cutscene (booting up sequence) is excluded from IGT
    if variables['introCutscene'] and line.startswith("Player profile saved"):
        variables['totalLoads'] = time() - TIMER
        variables['introCutscene'] = False
    # Not removing the initial load (A1) because the run hasn't started yet
    m = match("^Started simulation on '.*?' in ([\d\.]*) seconds", line)
    if m and STATE == 'RUNNING':
        load = float(m.group(1))
        variables['totalLoads'] += load
    return True

def start(line):
    # Only start for A1, since restore backup / continue should mostly be on other worlds.
    if line.startswith("Started simulation on 'Content/Talos/Levels/Cloud_1_01.wld'"):
        variables['gameStarting'] = True
    # Ditto for Gehenna with the intro world.
    if line.startswith("Started simulation on 'Content/Talos/Levels/DLC_01_Intro.wld'"):
        variables.gameStarting = True
    if variables['gameStarting'] and "sound channels reinitialized." in line:
        variables['gameStarting'] = False
        variables['introCutscene'] = True
        return True

def reset(line):
    global variabes
    if line == "Saving talos progress upon game stop.":
        variables = {
            'currentWorld': "",
            'gameStarting': False,
            'introCutscene': False,
            'lastLines': 0,
            'doubleSplit': False,
            'totalLoads': 0.0,
            'adminEnding': False,
        }
        return True

def game_time():
    if variables['introCutscene']:
        return 0
    return time() - TIMER - variables['totalLoads']

def split(line):
    # Map changes
    if line.startswith("Changing over to"):
        map_name = line[17:]
        # Ensure 'restart checkpoint' doesn't trigger map change
        if map_name != variables['currentWorld']:
            variables['currentWorld'] = map_name
            if map_name == "Content/Talos/Levels/Nexus.wld":
                return settings["Split on return to Nexus"]
            elif map_name == "Content/Talos/Levels/DLC_01_Hub.wld":
                return settings["(DLC) Split on return to Hub"]
            elif map_name == "Content/Talos/Levels/Cloud_3_08.wld":
                variables['cStar'] = 0
    # Sigil and star collection
    if line.startswith("Picked:"):
        if variables['doubleSplit']:
            return False
        variables['doubleSplit'] = True
        if variables['currentWorld'] == "Content/Talos/Levels/Cloud_3_08.wld":
            variables['cStar'] += 1 #Sigils collected while in C Star
            if variables['cStar'] == 3:
                return settings["Split on completing C*"]
        if line[8:2] == "**":
            if settings["Split on star collection"]:
                return True
            elif variables['currentWorld'] == "Content/Talos/Levels/Nexus.wld":
                return settings["Split on star collection in the Nexus"]
        elif variables['currentWorld'] == "Content/Talos/Levels/Cloud_1_06.wld":
            return settings["Split on tetromino collection in A6"]
        else:
            return settings["Split on tetromino collection"]
    else:
        variables['doubleSplit'] = False # DLC Double-split prevention

    # Arranger puzzles
    if line.startswith('Puzzle "') and '" solved' in line:
        puzzle = line[8:]
        if puzzle.startswith("Mechanic"):
            return settings["Split on item unlocks"]
        elif puzzle.startswith("Door"):
            return settings["Split on tetromino world doors"]
        elif puzzle.startswith("SecretDoor"):
            return settings["Split on tetromino star doors"]
        elif puzzle.startswith("Nexus"):
            return settings["Split on tetromino tower doors"]
        elif puzzle.startswith("DLC_01_Secret"):
            return settings["(DLC) Split on puzzle doors"]
        elif puzzle.startswith("DLC_01_Hub"):
            variables.adminEnding = True # Admin puzzle door solved, so the Admin is saved.
            return settings["(DLC) Split on puzzle doors"]
    if variables['currentWorld'] == "Content/Talos/Levels/Islands_03.wld": # Base game Messenger Ending
        return line.startswith("USER:") # Line differs in languages.
    elif variables['currentWorld'] == "Content/Talos/Levels/Nexus.wld": # Base game Transcendence and Eternalize Ending
        return line == "USER: /transcend" or line == "USER: /eternalize"
    if variables['currentWorld'] == "Content/Talos/Levels/DLC_01_Hub.wld": # Any DLC ending
        if line == "Save Talos Progress: entered terminal":
            variables['lastLines'] = 0
        if line.startswith("USER:"):
            variables['lastLines'] += 1
            if variables['adminEnding']: # If admin is saved, it takes 5 lines to end the game
                return variables['lastLines'] == 5
            else: # In all other endings, game ends on the 4th dialogue after entering the terminal
                return variables['lastLines'] == 4

#### Mimics livesplit functionality
def tail():
    try: # Create the file if it doesn't exist
        open(FILE, 'w')
    except:
        pass
    with open(FILE, 'rb') as f:
        f.seek(0, 2) # Go to EOF
        while True:
            lastLine = f.readline()
            if not lastLine:
                sleep(0.01)
                continue
            yield lastLine[15:].strip()

for line in tail():
    if update(line):
        if STATE == 'RUNNING':
            if not reset(line):
                if split(line):
                    name, pb, gold = SPLITS[len(RUN_SPLITS)]
                    curr_time = game_time()
                    time_string = '%02d:%05.2f [' % (curr_time/60, curr_time%60)
                    delta = curr_time - pb
                    time_string += '+' if delta > 0 else '-'
                    delta = abs(delta)
                    time_string += '%02d:%05.2f] ' % (delta/60, delta%60)
                    if curr_time - last_split < gold:
                        time_string += '**%s**' % name
                        gold = curr_time - last_split
                    else:
                        time_string += name
                    RUN_SPLITS.append([name, curr_time-last_split, gold])
                    print(time_string)
                    last_split = curr_time
            else:
                STATE = 'STOPPED'
                TIMER = None
                last_split = None
                print('---- Run reset ----')
                for SPLIT in RUN_SPLITS:
                    print(SPLIT)
                RUN_SPLITS = []
        elif STATE == 'STOPPED':
            if start(line):
                STATE = 'RUNNING'
                TIMER = time()
                last_split = 0.0
                print('---- Run started ----')
