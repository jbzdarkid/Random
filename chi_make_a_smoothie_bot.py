from asyncio import sleep
import discord
import subprocess
import time
from datetime import datetime
import sys
from pathlib import Path

client = discord.Client()
client.started = False

@client.event
async def on_ready():
  if client.started: # @Hack: Properly deal with disconnection / reconnection
    await client.close()
    return
  client.started = True

  channel = client.get_channel(699493553444749367)
  sent_today = False
  while 1:
    now = datetime.now()
    tomorrow = datetime(now.year, now.month, now.day + 1)
    def is_a_workday(day):
      return day.weekday() >= 0 and day.weekday() <= 4

    if is_a_workday(tomorrow) and not sent_today and now.hour == 18: # 6 PM
      sent_today = True
      message = await channel.send(content=f'<@{client.user_id}>! Make a smoothie.')

    await sleep(60)

  await client.close()

if __name__ == '__main__':
  if 'subtask' not in sys.argv:
    while 1:
      subprocess.run([sys.executable, __file__, 'subtask'] + sys.argv)
      # Speedrun.com throttling limit is 100 requests/minute
      time.sleep(60)
  else:
    with open(Path(__file__).parent / 'chi_make_a_smoothie_token.txt', 'r') as f:
      token = f.read().strip()
    with open(Path(__file__).parent / 'chi_make_a_smoothie_user.txt', 'r') as f:
      client.user_id = f.read().strip()
    client.run(token, reconnect=True)

