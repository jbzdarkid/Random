from os import environ
from pathlib import Path
from json import load, dump

player_data = Path(environ['appdata']).parent / 'LocalLow' / 'Hyperbolic Magnetism' / 'Beat Saber' / 'PlayerData.dat'
player_data_json = load(player_data.open())

assert(player_data_json['version'] == '2.0.5')
local_player = player_data_json['localPlayers'][0]
local_player['shouldShowTutorialPrompt'] = True
for i, mission in enumerate(local_player['missionsStatsData']):
  mission['cleared'] = False
local_player['showedMissionHelpIds'] = []

dump(player_data_json, player_data.open('w'), separators=(',', ':'))

"""
Required:
1. Beat Saber              - 1:50
3. Be There For You        - 2:51
4b. Escape                 - 2:41
11. Breezer                - 2:01
15. Country Rounds         - 2:50
16a. [F] $100 Bills        - 2:21 * 0.833 = 1:57
17a. Unlimited Power       - 2:00
18. Be There For You       - 2:51
21. Legend                 - 1:57
28a. Be There For You      - 2:51
29. Rum n' Bass            - 3:09
30. Breezer                - 2:01
31. Unlimited Power        - 2:00

Chosen:
24c. Lvl Insane            - 1:50
8b. Turn Me On             - 1:51
24a. Turn Me On            - 1:51
2b. Legend                 - 1:57
13a. Legend                - 1:57
13b. Unlimited Power       - 2:00
23a. Unlimited Power       - 2:00
5a. Breezer                - 2:01
24b. Breezer               - 2:01
10. [S] Beat Saber         - 1:50 * 1.125 = 2:03
22b. [F] Elixia            - 2:33 * 0.833 = 2:07
5b. I Need You             - 2:10
19b. I Need You            - 2:10
20b. [S/OS] Legend         - 1:57 * 1.125 = 2:11
9a. Balearic Pumping       - 2:14
14a. [HM] Balearic Pumping - 2:14
2a. $100 Bills             - 2:21
4a. Commercial Pumping     - 2:21
7b. $100 Bills             - 2:21
9b. Commercial Pumping     - 2:21
12b. $100 Bills            - 2:21
14b. Commercial Pumping    - 2:21
16b. Commercial Pumping    - 2:21
22a. [F] Country Rounds    - 2:50 * 0.833 = 2:21
25. $100 Bills             - 2:21
23b. Be There For You      - 2:51

Skipped:
7a. Lvl Insane             - 1:50
20a. Turn Me On            - 1:51
27. Legend                 - 1:57
8a. [F] Escape             - 2:41 * 0.833 = 2:14
17b. [OS] $100 Bills       - 2:21 [Too hard]
6a. Escape                 - 2:41
12a. [HM] Escape           - 2:41
26. [OS/NF] Escape         - 2:41
6b. Country Rounds         - 2:50
12c. Rum n' Bass           - 3:09
19a. Rum n' Bass           - 3:09
28b. [HM/NF] Angel Voices  - 6:12

Skipped (notes): 6a, 6b, 12a, 12c, 17b, 19a, 26
"""
