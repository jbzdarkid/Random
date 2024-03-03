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

def bad_hash(x, val=0):
  return x ^ (val + 2654435769 + (x << 6) + (x >> 2))

def hash_deck(cards):
  hash = 0
  for card in cards:
    hash = trunc(bad_hash(hash, card))
  return hash

unknown_hash = 4901740154402535512 # For the new deck code :)

decklist = decode_decklist('AAEBAaoIDLSKBLaKBKyfBNugBOCgBJbUBKDUBKnUBPzbBMviBJakBfCuBQmf1ASo2QS12QT03ASz3QS14gSl5ATF7QTK7QQA')

print('Actual hash:  ', hash_deck(decklist))
print('Expected hash: -8433254302802380797')

def bits(x, bits=64):
  if x & (1 << (bits - 1)): # Adjust for sign
    x = x + (1 << bits)
  str = bin(x).replace('0b', '')[-bits:]
  return '0' * (bits - len(str)) + str


def reverse_hash(y, val):
  # We don't have any real data about the first two bits, but usually they will trial-and-error away.
  for initial_guess in [0b00, 0b01, 0b10, 0b11]:
    guess = initial_guess
    for j in range(2, 64):
      mask = (1 << (j - 1)) - 1
      bit = 1 << j

      if (bad_hash(guess, val) & mask) == (y & mask):
        continue
      elif (bad_hash(guess | bit, val) & mask) == (y & mask):
        guess |= bit
        continue
      break
    # Double check in case we exited early (also verifies the high 2 bits)
    if bad_hash(guess, val) != y:
      continue
    return guess
  return None


"""
import random
for i in range(100):
  print('-'*10, 'Attempt', i+1)
  x = random.randint(2 ** 63, 2 ** 64)
  v = random.randint(1, 1000)
  y = bad_hash(x, v)
  guess = reverse_hash(y, v)
  print('Guessed x', bits(guess))
  print('Actual x ', bits(x))
  assert(guess == x)
"""

print('Something bad happening')
x = 191242499615597045949
y = 12106176445390699504078

print(bad_hash(x, 46667))
print(y)

x2 = reverse_hash(y, 46667)
print(x2)
exit()


hash = 0
for i, card in enumerate(decklist):
  print('-'*50, 'i', i)
  print('pre hash', hash)
  print('card', card)
  hash = bad_hash(hash, card)
  print('post hash', hash)
  rhash = reverse_hash(hash, card)
  print('rhash', rhash)
  assert rhash is not None
  print('rebuild', bad_hash(rhash, card))
  