import logging
import logging.handlers
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


# https://stackoverflow.com/a/6692653
class CustomFormatter(logging.Formatter):
  def format(self, r):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    return f'[{current_time}] {r.thread:5} {r.module:20} {r.funcName:20} {r.lineno:3} {r.msg % r.args}'


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler('out.log', maxBytes=5_000_000, backupCount=1, encoding='utf-8', errors='replace')
handler.setLevel(logging.NOTSET)
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.ERROR)
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)











logger.info('INFO')
logger.debug('DEBUG')
logger.error('ERROR')

raise

def worker(data):
  for i in range(1):
    time.sleep(random.randint(1, 100) / 100)
    logger.info(f'{i}: {data}')
  return data * 10


with ThreadPoolExecutor(8) as pool:
  for i, data in enumerate(pool.map(worker, range(10))):
    logger.info(f'{i}: {data}')
