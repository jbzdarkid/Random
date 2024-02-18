from pathlib import Path
import json

"""
out = Path('C:\\Users\\localhost\\Downloads\\out')
data = []
for p in out.iterdir():
  hash = p.name
  card_id = p.open('r').read()
  time = p.stat().st_mtime
  data.append([time, card_id, hash])
  
data.sort()
for d in data:
  print(d)
exit()
"""

try:
  cards_file = Path('cards.json')
  cardlist = json.load(cards_file.open('r', encoding='utf-8'))
  for k, v in cardlist:
    cardlist[int(k)] = v
except:
  # import requests
  # r = requests.get('https://api.hearthstonejson.com/v1/latest/all/cards.collectible.json')
  
  with Path('cards.collectible.json').open('r', encoding='utf-8') as f:
    j = json.load(f)
  
  cardlist = {}
  for card in j:
    cardlist[card['dbfId']] = card['name']['enUS']

  with cards_file.open('w', encoding='utf-8') as f:
    json.dump(cardlist, f)

# Done loading cards


# From https://github.com/fmoo/python-varint/blob/master/varint.py
def read_varint(stream):
    shift = 0
    result = 0
    while True:
        raw = ord(stream.read(1))
        result |= (raw & 0x7f) << shift
        shift += 7
        if not (raw & 0x80):
            break

    return result
    
def read_array(stream):
    length = read_varint(stream)
    return [read_varint(stream) for _ in range(length)]

# From https://github.com/HearthSim/HearthDb/blob/master/HearthDb/Deckstrings/DeckSerializer.cs
def decode_decklist(decklist):
  import base64
  from io import BytesIO

  stream = BytesIO(base64.b64decode(decklist))
  read_varint(stream) # Unused
  read_varint(stream) # Encoding version (1)

  deck_format = read_varint(stream)

  heroes = read_array(stream)
  singletons = read_array(stream)
  doubletons = read_array(stream)
  
  cards = singletons + doubletons + doubletons
  cards.sort()
  
  return {
    'format': ['unknown', 'wild', 'standard', 'classic', 'twist'][deck_format],
    'hero': heroes[0],
    'cards': cards,
  }

# Simulate C++/C# truncation
def trunc(val, bits=64):
  val = val & (2 ** bits - 1) # Truncate high bits
  if val & (2 ** (bits - 1)): # Adjust for sign
    return val - (2 ** bits)
  return val

def hash_deck(cards):
  # First, we must normalize the cards:
  normalized_cards = []
  for card in cards:
    card_variants = [k for k, v in cardlist.items() if v == cardlist[card]]
    normalized_cards.append(min(card_variants))

  normalized_cards.sort()

  for i, card in enumerate(normalized_cards):
    print(f'Card {i+1:<2}: {card:<5} {cardlist[card]}')

  # Then we can go about the hash computation.
  hash = 0
  for card in normalized_cards:
    hash ^= trunc(card + 2654435769 + (hash << 6) + (hash >> 2))
  return hash

decklist = decode_decklist('AAEBAaoIDLSKBLaKBKyfBNugBOCgBJbUBKDUBKnUBPzbBMviBJakBfCuBQmf1ASo2QS12QT03ASz3QS14gSl5ATF7QTK7QQA')

# cards = [68441, 69723, 46667, 66868, 66870, 69728, 76310, 76319, 76319, 76320, 76329, 76968, 76968, 76981, 76981, 77308, 77428, 77428, 77491, 77491, 78133, 78133, 78155, 78373, 78373, 79557, 79557, 79562, 79562, 87920]
expected_hash = -8433254302802380797

print(hash_deck(decklist['cards']))
print(expected_hash)
