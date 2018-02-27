from socket import socket
from re import compile
from select import select
import threading

from Tkinter import *

username = 'jbzdarkid'
CHAT_MSG = compile('^:(\w+)!\w+@\w+.tmi.twitch.tv PRIVMSG #' + username + ' :(.*)\r\n$')

class Popup(object):
  def __init__(self,master):
    top = self.top = Toplevel(master)
    self.label = Label(top, text="Hello World")
    self.label.pack()
    self.entry = Entry(top)
    self.entry.pack()
    self.button = Button(top, text='Ok', command = self.cleanup)
    self.button.pack()

  def cleanup(self):
    self.value = self.entry.get()
    self.top.destroy()

class IrcBot(Frame):
  # def popup(self):
    # self.popupWindow = popupWindow(self.master)
    # self.master.wait_window(self.popupWindow.top)

  def say_hi(self):
    print "hi there, everyone!"

  def createWidgets(self):
    self.connect = Button(self)
    self.connect['text'] = 'Connect to IRC'
    self.connect['command'] = self.connect
    self.connect.pack()
  
    self.QUIT = Button(self)
    self.QUIT["text"] = "QUIT"
    self.QUIT["fg"]   = "red"
    self.QUIT["command"] =  self.quit

    self.QUIT.pack({"side": "left"})

    self.hi_there = Button(self)
    self.hi_there["text"] = "Hello",
    self.hi_there["command"] = self.say_hi

    self.hi_there.pack({"side": "left"})

  def __init__(self, master=None):
    Frame.__init__(self, master)
    self.pack()
    self.createWidgets()




def on_chat(username, message):
  print(username+': '+message)
  
  if message.startswith('!'):
    message_parts = message[1:].split(' ')
    if message_parts[0] in COMMANDS:
      COMMANDS[message_parts[0]](message_parts[1:])

def votekick(username, *args):
  print('votekick start', username)

def ping(*args):
  send_message('pong')
  
def commands(*args):
  command_list = COMMANDS.keys()
  command_list.sort()
  send_message('List of commands: ' + ', '.join(command_list))

COMMANDS = {
  'votekick': votekick,
  'ping': ping,
  'commands': commands,
}

def start_ui():
  root = Tk()
  app = IrcBot(master=root)
  app.mainloop()
  root.destroy()

if __name__ == '__main__':
  thread = threading.Thread(target=start_ui)
  thread.daemon = True
  thread.start()

  # Connect to twitch
  irc = socket()
  irc.connect(('irc.chat.twitch.tv', 6667))
  with open('twitchtoken.txt', 'rb') as f:
    irc.send('PASS ' + f.read() + '\r\n')
  irc.send('NICK ' + username + '\r\n')
  data = irc.recv(4096) # You are in a maze of twisty passages

  irc.send('JOIN #' + username + '\r\n') 
  data = irc.recv(1024) # /JOIN
  data = irc.recv(1024) # End of /NAMES list
  irc.setblocking(0)
  
  while 1:
    # Wait for new data so that control-C works
    ready = select([irc], [], [], 1) # 1 second timeout
    if ready[0]:
      data = irc.recv(4096)
      if data == 'PING :tmi.twitch.tv\r\n':
        irc.send('PONG :tmi.twitch.tv\r\n'.encode("utf-8"))
        continue
      m = CHAT_MSG.search(data)
      if not m:
        print 'Unable to parse message: "' + data + '"'
        continue
      on_chat(m.group(1), m.group(2))

  def send_message(message):
    irc.send('PRIVMSG #'+username+' :'+message+'\r\n')
  

