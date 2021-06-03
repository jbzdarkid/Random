from selenium import webdriver
from Tkinter import *

from PIL import Image

driver = webdriver.Chrome()
driver.set_window_size(500, 500)
driver.get('https://www.google.com')
while(1):
  pass
driver.save_screenshot('temp.png')
driver.quit()
img = Image.open('temp.png')
img_tk = ImageTk.PhotoImage(Image.open('temp.png'))

root = Tk()
root.title('Ircbot')
root.geometry('500x500')

panel = tk.Label(window, image = img)
panel.pack(side='bottom', fill='both', expand='yes')

root.mainloop()
root.destroy()
