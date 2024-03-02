from pathlib import Path
import json

try:
  cards_file = Path('cards.json')
  cardlist = json.load(cards_file.open('r', encoding='utf-8'))
  for k, v in list(cardlist.items()):
    del cardlist[k]
    cardlist[int(k)] = v # Json doesn't support integer keys but python does
except Exception as e:
  print(e)
  import requests
  r = requests.get('https://api.hearthstonejson.com/v1/latest/all/cards.collectible.json')
  j = r.json()
  with Path('cards.collectible.json').open('w', encoding='utf-8') as f:
    json.dump(j, f)
  
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
  normalized_cards = normalize_deck(cards)
  normalized_cards.sort()

  for i, card in enumerate(normalized_cards):
    print(f'Card {i+1:<2}: {card:<5} {cardlist[card]}')

  return normalized_cards

# Simulate C++/C# truncation
def trunc(val, bits=64):
  val = val & (2 ** bits - 1) # Truncate high bits
  if val & (2 ** (bits - 1)): # Adjust for sign
    return val - (2 ** bits)
  return val

def normalize_deck(cards):
  normalized_cards = []
  for card in cards:
    card_variants = [k for k, v in cardlist.items() if v == cardlist[card]]
    normalized_cards.append(min(card_variants))

  normalized_cards.sort()
  return normalized_cards

def hash_step(hash, card):
    return hash ^ trunc(card + 2654435769 + (hash << 6) + (hash >> 2))

def hash_deck(cards):
  hash = 0
  for card in cards:
    hash = hash_step(hash, card)
  return hash

decklist = decode_decklist('AAEBAaoIDLSKBLaKBKyfBNugBOCgBJbUBKDUBKnUBPzbBMviBJakBfCuBQmf1ASo2QS12QT03ASz3QS14gSl5ATF7QTK7QQA')

print('Actual hash:  ', hash_deck(decklist))
print('Expected hash: -8433254302802380797')



unknown_hash = 4901740154402535512 # For the new deck code :)




def bits(x):
  str = bin(x).replace('0b', '')[-16:]
  return '0' * (16 - len(str)) + str

def bad_hash(x):
  return x ^ ((x >> 2) + (x << 6))

import random
random.seed(42) # For ease of testing/stability
for i in range(10):
  print('-'*10, 'Attempt', i+1)
  x = random.randint(2 ** 15, 2 ** 16)
  y = trunc(bad_hash(x))

  # We don't have any real data about the first two bits, but usually they will trial-and-error away.
  for initial_guess in [0b00, 0b01, 0b10, 0b11]:
    guess = initial_guess
    for j in range(2, 16):
      mask = (1 << (j - 1)) - 1
      bit = 1 << j

      # TODO: Is it ever possible for both to be true?
      if (bad_hash(guess) & mask) == (y & mask):
        continue
      elif (bad_hash(guess | bit) & mask) == (y & mask):
        guess |= bit
        continue
      break
    if bad_hash(guess) != y:
      continue # Double check in case we exited early (and also for high bits)
    print('Guessed x', bits(guess))
  print('Actual x ', bits(x))

