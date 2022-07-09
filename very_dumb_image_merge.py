from PIL import Image

img1 = Image.open(r"C:\Users\joblac\Downloads\mononoke022.jpg")
img2 = Image.open(r"C:\Users\joblac\Downloads\mononoke021.jpg")

merged = Image.new('RGB', (img1.width, img1.height + img2.height))
merged.paste(img1, (0, 0))
merged.paste(img2, (0, img1.height))
merged.show()
input()
