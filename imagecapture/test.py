from PIL.ImageGrab import grab
from mouse import mouse
from SendKeys import SendKeys
from time import sleep

mouse(0, 0)
sleep(10)

SendKeys('D{10}')

sleep(10)
SendKeys('S{10}')

image = grab()
image.show()
