puzzles = {
'**1': 'A3 Star #2 (ABTU)',
'**2': 'A2 Star (Outside)',
'**3': 'A3 Star #1 (Outside)',
'**4': 'A4 Star (PiF)',
'**5': 'A1 Star (Outside)',
'**6': 'A5 Star #2 (FC)',
'**7': 'A5 Star #1 (TtDWTB)',
'**8': 'A6 Star (Outside)',
'**9': 'A7 Star (TPLB)',
'**10': 'B1 Star (SaaS)',
'**11': 'B2 Star (TT)',
'**12': 'B3 Star (BA)',
'**13': 'B4 Star #1 (TRA)',
'**14': 'B5 Star #1 (Outside)',
'**15': 'B7 Star #2 (Outside)',
'**16': 'B7 Star #1 (BSbS)',
'**17': 'C1 Star (Outside)',
'**18': 'C2 Star (ADaaF)',
'**19': 'C3 Star (W)',
'**20': 'C4 Star #2 (O)',
'**21': 'C4 Star #1 (TR)',
'**22': 'C5 Star #3 (D)',
'**23': 'C5 Star #2 (TF)',
'**24': 'B4 Star #2 (Outside',
'**25': 'Floor 3 Star',
'**26': 'Messenger Garden Star',
'**27': 'C5 Star #1 (UCaJ)',
'**28': 'Floor 0 Star',
'**29': 'C6 Star',
'**30': 'C7 Star',
'DI1': 'Poking a Sleeping Lion',
'DI2': 'Things to Do With Two Boxes',
'DJ1': 'Striding the Beaten Path',
'DJ2': 'Outnumbered',
'DJ3': 'Only the Two of Us',
'DJ4': 'Self-Help Tutorial',
'DJ5': 'Slightly Elevated Sigil',
'DL1': 'The Guards Must Be Crazy',
'DL2': 'You Know You Mustn\'t Cross the Streams',
'DL3': 'Locked from Inside',
'DT1': 'Going Over the Fence',
'DT2': 'One Little Buzzer',
'DT3': 'Trapped Inside',
'DT4': 'Double Plate',
'DZ1': 'A Switch out of Reach',
'DZ2': 'Hall of Windows',
'DZ3': 'Stashed for Later',
'DZ4': 'Mobile Mindfield',
'EL1': 'Jammed from Within',
'EL2': 'Merry Go \'Round',
'EL3': 'Peekaboo!',
'EL4': 'Unreachable Garden',
'EO1': 'Nexus',
'ES1': 'Nerve-Wrecker',
'ES2': 'Cat\'s Cradle',
'ES3': 'Dumb Dumb Mine',
'ES4': 'Cobweb',
'L10': 'Dead Man\'s Switch',
'MI1': 'Bouncing Side by Side',
'MJ1': 'Blown Away',
'ML1': 'Trio Bombasticus',
'ML2': 'Suicide Mission',
'ML3': 'Window through a Door',
'ML4': 'Crisscross Conundrum',
'MO1': 'Big Lump of Mine',
'MS1': 'Third Wheel',
'MS2': 'The Tomb',
'MT1': 'Peephole',
'MT2': 'A Bit Tied Up',
'MT3': 'Locked Me Up, Swallowed the Key',
'MT4': 'Branch it Out',
'MT5': 'Above All That...',
'MT6': 'Over the Fence',
'MT7': 'Road of Death',
'MT8': 'Man on The Moon',
'MT9': 'Sunshot',
'MZ1': 'Push it Further',
'MZ2': 'Don\'t Cross the Streams!',
'MZ3': 'Something about a Star',
'MZ4': 'Moonshot',
'NI1': 'Alley of the Pressure Plates',
'NI2': 'Egyptian Arcade',
'NI3': 'A Fan Across Forever',
'NI4': 'The Conservatory',
'NI5': 'Armory',
'NI6': 'Time Flies',
'NJ1': 'Whole Lotta Jamming',
'NJ2': 'Multiply Impossible Ascension',
'NJ3': 'Jammer Quarantine',
'NJ4': 'Circumlocution',
'NL1': 'An Escalating Problem',
'NL2': 'Deception',
'NL3': 'A Door Too Far',
'NL4': 'Two Pesky Little Buzzers',
'NL5': 'Higher Ground',
'NL6': 'Eagle\'s Nest',
'NL7': 'A Box Up High',
'NL8': 'Wrap Around the Corner',
'NL9': 'Me, Myself and Our Two Jammers',
'NO1': 'Windows into a Labyrinth',
'NO2': 'A Ditch and a Fence',
'NO3': 'Three Little Connectors... and a Fan',
'NO4': 'Time Crawls',
'NO5': 'Dumbwaiter',
'NO6': 'The Seven Doors of Recording',
'NO7': 'Carrier Pigeons',
'NS1': 'Behind the Iron Curtain',
'NS2': 'Rapunzel',
'NS3': 'Oubliette',
'NS4': 'Two Way Street',
'NT1': 'Pinhole Windows',
'NT2': 'Woosh!',
'NT3': 'The Right Angle',
'NT4': 'Redundant Power Supply',
'NT5': 'Labyrinth',
'NT6': 'Cemetery',
'NT7': 'Big Stairs, Little Stairs',
'NT8': 'Stables',
'NT9': 'Throne Room',
'NZ1': 'Friendly Crossfire',
'NZ2': 'Bichromatic Entanglement',
'NZ3': 'The Four Chambers of Flying',
'NZ4': 'Blowback',
'NZ5': 'The Short Wall',
'NZ6': 'Weathertop',
'T10': 'Just Doors and Windows',
'T10': 'Up Close and Jammed',
'T11': 'Prison Break',
'T12': 'Crisscross Conundrum Advanced'
}

log = open('/Users/joe/Library/Application Support/Steam/SteamApps/common/The Talos Principle/Log/Talos.All.log', 'rb')
start_time = None
game_starting = 0
current_world = None
out = open('out.txt', 'wb')
for line in log:
    try:
        time = int(line[0:2])*3600 + int(line[3:5])*60 + int(line[6:8])
    except ValueError: # Malformed line
        continue
    if 'Stopping simulation' in line:
        game_starting = 1
    if game_starting == 1 and 'Starting Talos simulation' in line:
        start_time = time
        loads = 0.0
        out.write('--- New Game started ')
        game_starting = 2
    if game_starting == 2 and 'Timestamp' in line:
        out.write('at %s ---\n' % line[26:-1])
        game_starting = 3
    if game_starting < 3:
        continue
    timedelta = time-start_time
    timestr = '%02d:%02d' % (timedelta/60, timedelta%60)

    if 'Started simulation' in line:
        loads += float(line.split()[-2])
    elif 'Picked:' in line:
        puzzle_name = puzzles[line[-4:-1]]
        out.write('%s : %s\n' % (timestr, puzzle_name))
    elif 'Changing to' in line:
        new_world = line.split('\'')[1]
        if new_world == 'Content/Talos/Levels/Nexus.wld' \
                and current_world is not None:
            world_name = current_world.split('/')[-1][5:-4]
            world_name = world_name.replace('_1_0', 'A')
            world_name = world_name.replace('_2_0', 'B')
            world_name = world_name.replace('_3_0', 'C')
            out.write('\t%s : Exited %s\n' % (timestr, world_name))
        current_world = new_world
    elif 'solved in' in line:
        out.write('\t%s : Unlocked %s\n' % (timestr, line.split('"')[1]))
    elif current_world == 'Content/Talos/Levels/Islands_03.wld' \
            and 'USER:' in line:
        out.write('Run completed: %s\n' % timestr)
        timedelta -= loads
        out.write('Loadless time: %02d:%02d\n' % (timedelta/60, timedelta%60))
    elif 'Core is shutting down' in line:
        out.write('--- Game Shutdown ---\n')
out.close()
