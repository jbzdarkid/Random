from math import factorial
from math import log2
from math import prod
import itertools

def l2p(x, y=None):
  if y:
    x = str(x)
    print(x, (40 - len(x)) * ' ', end=':')
    x = y
  sign = ' '
  if x < 0: # Can't take a logarithm of a negative number
    x *= -1
    sign = '-'
  print(f'{sign}2^{log2(x)}')

print('R', '\t', 'actual\t\t', '\t', 'guess')
max = 120
for i in range(10, 50):
  base = (max + i) / 2.17
  pow = (max - i)
  print(i, '\t', log2(factorial(max) / factorial(i)), '\t', log2(base ** pow))



exit()

"""
# 100! / 19!
l2p('actual value', factorial(100) / factorial(19))
# I estimated this by doing:
# (100 * 20) * (99 * 21) * (98 * 22) * ...
# which is (60^2 - 40^2) * (60^2 - 39^2) * (60^2 - 38^2) * ...
# which is, well, a lot of crossterms. But the first term is 60^81, which is only a few orders of magnitude off.
cross0 = 60 ** 81
l2p('0th term', cross0)
# but, crossterms.
# So, let's start doing the math on those:
terms = []
for i in range(40, 0, -1):
  terms.append((60**2, -i**2))

product = 60
for a, b in terms:
  product *= (a + b)
l2p('full crossproduct', product)
# math checks out to here


cross1 = 0
for _, b in terms:
  cross1 += b
cross1 *= 60 ** 79
l2p('1st term', cross1)

l2p('0+1', cross0 + cross1)
"""

def estimate(max, min):
  l2p(f'{max}! / {min}!', factorial(max) / factorial(min))

  base = (max + min + 1) / 2
  pow = (max - min)

  terms = []
  for i in range(pow // 2, 0, -1):
    terms.append(-i**2)

  sum = 0
  for i in range(4):
    cross = 0
    for combo in itertools.combinations(terms, i):
      cross += prod(combo)
    cross *= base ** (pow - i*2)
    l2p(f'term {i}', cross)
    sum += cross
    l2p('    sum', sum)
    print()

estimate(51, 4)
