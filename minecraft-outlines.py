from PIL import Image
from os.path import expanduser

pairs = [
	['coal_ore', 'coal_block'],
	['diamond_ore', 'diamond_block'],
	['emerald_ore', 'emerald_block'],
	['gold_ore', 'gold_block'],
	['iron_ore', 'iron_block'],
	['lapis_ore', 'lapis_block'],
	['quartz_ore', 'quartz_block_side'],
	['redstone_ore', 'redstone_block'],
]

blocks_dir = expanduser('~') + '/Library/Application Support/minecraft/resourcepacks/Random1.9/assets/minecraft/textures/blocks/'

for ore, block in pairs:
	im_ore = Image.open('%s%s.png' % (blocks_dir, ore))
	im_block = Image.open('%s%s.png' % (blocks_dir, block))
	x, y = im_ore.size
	im_block.paste(im_ore.crop((1, 1, x-1, y-1)), (1, 1))
	im_ore.close()
	im_block.save('%s%s.png' % (blocks_dir, ore))
