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

def abs(x):
  return x if x > 0 else -x

import random
random.seed(41) # For ease of testing/stability
for i in range(2):
  print('-'*10, 'Attempt', i+1)
  x = random.randint(2 ** 15, 2 ** 16)
  y = trunc(x ^ ((x >> 2) + (x << 6)))

  def log(guess, j):
    if i != 1:
      return
    guess_int = sum((guess[k] << k for k in range(16)))

    print(f'Progress as of {j} bits:')
    j += 1 # indexing errors
    print('Actual', bits(x)[-j:])
    print('Guess ', bits(guess_int)[-j:])

  """
  print('X', bits(x))
  print('2', bits(x >> 2))
  print('6', bits(x << 6))
  print('4', bits((x >> 2) + (x << 6)))
  print('Y', bits(y))
  """

  # Start by guessing the bottom two bits of X (that got shifted off). We can confirm / reuse this guess later.
  # For simplicity, I'm converting Y to an array of true/false values
  x_bin = [(x & (1 << i)) >> i for i in range(16)]
  y_bin = [(y & (1 << i)) >> i for i in range(16)]
  for initial_guess in [0b00, 0b01, 0b10, 0b11]:
    #print('Initial guess', bits(initial_guess))
    guess = [0] * 16
    guess2 = []
    guess[0] = (initial_guess & 0b01)
    log(guess, 0)
    guess[1] = (initial_guess & 0b10) >> 1
    log(guess, 1)
    guess2 = []
    # Now we can infer bits 2 and 3 because y[0] = x[0] ^ (x[2] + x[-6]) = x[0] ^ x[2]
    guess[2] = y_bin[0] ^ guess[0]
    log(guess, 2)
    guess[3] = y_bin[1] ^ guess[1]
    log(guess, 3)
    # Same math for bits 4 and 5 because y[2] = x[2] ^ (x[4] + x[-4]) = x[2] ^ x[4]
    guess[4] = y_bin[2] ^ guess[2]
    log(guess, 4)
    guess[5] = y_bin[3] ^ guess[3]
    log(guess, 5)
    # Same math for bits 6 and 7 because y[5] = x[5] ^ (x[7] + x[-1]) = x[5] ^ x[7]
    guess[6] = y_bin[4] ^ guess[4]
    log(guess, 6)
    guess[7] = y_bin[5] ^ guess[5]
    log(guess, 7)
    # Now the <<6 starts being relevant, so y[6] = x[6] ^ (x[8] + x[0]), and thus
    # y[6] ^ x[6] = x[8] + x[0]
    # (y[6] ^ x[6]) - x[0] = x[8]
    # and we of course have our first error here, if we try to do 1 - 0 (since the previous operation could not carry)
    guess[8] = (y_bin[6] ^ guess[6]) - guess[0]
    log(guess, 8)
    if guess[8] < 0:
      continue
    # Now it becomes possible to have a carry -- i.e. if  both x[8] and x[0] were 1, we would have a carryover
    # Fortunately we can compute the carry, since we have guessed the previous two bits.
    # y[7] = x[7] ^ (x[9] + x[1] + carry)
    # y[7] ^ x[7] = x[9] + x[1] + carry
    # (y[7] ^ x[7]) - x[1] - carry = x[9]
    carry = (guess[0] and guess[8])
    guess[9] = (y_bin[7] ^ guess[7]) - guess[1] - carry
    log(guess, 9)
    if guess[9] < 0:
      # print('Invalid guess due to carry:', bits(initial_guess))
      continue
    # And we can just use this algorithm for the rest of the bits.
    guess[10] = abs((y_bin[8]  ^ guess[8])  - guess[2] - (guess[1] and guess[9]))
    log(guess, 10)
    guess[11] = abs((y_bin[9]  ^ guess[9])  - guess[3] - (guess[2] and guess[10]))
    log(guess, 11)
    guess[12] = abs((y_bin[10] ^ guess[10]) - guess[4] - (guess[3] and guess[11]))
    log(guess, 12)
    guess[13] = abs((y_bin[11] ^ guess[11]) - guess[5] - (guess[4] and guess[12]))
    log(guess, 13)
    guess[14] = abs((y_bin[12] ^ guess[12]) - guess[6] - (guess[5] and guess[13]))
    log(guess, 14)
    guess[15] = abs((y_bin[13] ^ guess[13]) - guess[7] - (guess[6] and guess[14]))
    log(guess, 15)
    if any(g == 2 for g in guess[10:]):
      # print('Invalid guess due to carry:', bits(initial_guess))
      continue

    # For the last two bits, we have all the data, so just confirm that it matches up:
    guess_int = sum((guess[i] << i for i in range(16)))
    guess_y = trunc(guess_int ^ ((guess_int >> 2) + (guess_int << 6)))
    if guess_y != y:
      continue

    # print('For initial guess', bits(initial_guess))
    print('Guessed x', bits(guess_int))
    print('Actual x ', bits(x))
