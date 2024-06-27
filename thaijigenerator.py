from lib.unicodetools import NC, AC, RC, DC, NV, BV, AV, tone, HCC, MCC, LCC
from PIL import Image, ImageDraw, ImageFont
from unicodeescape import string_to_unicode_escape
import os
import csv

def find_consonant(text: str) -> str:
	for c in NC + AC + RC + DC + ["\uf700", "\uf70f"]:
		if c in text:
			return c
	for v in NV:
		if v in text:
			return v
	return "ก"

def text_to_image(text: str, font_path: str, font_size: int, image_path: str, cell_height: int, padding_x: int = 5, do_escape: bool = True):
	if not os.path.exists(os.path.dirname(image_path)):
		os.makedirs(os.path.dirname(image_path))

	if do_escape:
		text = string_to_unicode_escape(text, False).replace("\\\\", "\\").encode("utf-8").decode("unicode-escape")

	# Load font
	font = ImageFont.truetype(font_path, font_size)
	bbox = font.getbbox(text)
	if len(text) > 1 or not (ord(text) >= 32 and ord(text) <= 126):
		bbox = font.getbbox(find_consonant(text) + "\uf719" + "่")
	cell_width = bbox[2] - bbox[0] + padding_x * 2

	# Create a blank image with transparent background
	image = Image.new("RGBA", (cell_width, cell_height), (0, 0, 0, 0))
	draw = ImageDraw.Draw(image)

	# align text center and draw
	text_width, text_height = bbox[2:]
	draw.text(((image.width - text_width) // 2, (image.height - text_height) // 2), text, font=font, fill=(255, 255, 255, 255))

	# copy pixel values from alpha to r, g, and b
	pixels = image.load()
	for y in range(image.height):
		for x in range(image.width):
			alpha = pixels[x, y][3]
			pixels[x, y] = (alpha, alpha, alpha, alpha)

	# Save image
	image.save(image_path)

def generate_combinations() -> "list[str]":
	consonants = NC + AC + RC + DC
	vowels = BV + AV

	combinations = []
	for consonant in consonants:
		for vowel in vowels:
			for t in tone:
				if (vowel == "็") or \
						(vowel in BV and t == "์") or \
						(vowel == "ํ" and t == "์") or \
						(vowel == "ั" and t == "์") or \
						(t == "์" and vowel not in ["ิ", "ุ"]) or \
						(vowel == "ํ") or \
						(consonant in HCC and t in ["๊", "๋"]) or \
						(consonant in LCC and t in ["๊", "๋"]):
					continue
				combinations.append(consonant + vowel + t)

	for consonant in consonants:
		for vowel in vowels:
			combinations.append(consonant + vowel)
	
	for consonant in consonants:
		for t in tone:
			if (consonant in HCC and t in ["๊", "๋"]) or \
					(consonant in LCC and t in ["๊", "๋"]):
				continue
			combinations.append(consonant + t)

	return sorted(list(set(combinations)))

def generate_thaiji_csv(comb: "list[str]", path: str):
	with open(path, "w", newline="", encoding="utf-8") as f:
		writer = csv.writer(f)
		writer.writerow(["raw", "encoded", "unicode"])
		for i, c in enumerate(comb):
			writer.writerow([c, string_to_unicode_escape(c, False), 3712 + i])

def generate_shell_code(comb: "list[str]", path: str):
	with open(path, "w") as f:
		for i, c in enumerate(comb):
			f.write(f"--char $((16#{3712 + i:04x})) fonts/${{1}}/{3712 + i:04x}.png \\\n")

def generate_font_images(font: str, generate_thai: bool = False, generate_latin: bool = False, generate_thaiji: bool = False):
	if generate_thai:
		print("Generating normal Thai characters...")
		for i in range(3585, 3676):
			if i in [3633, 3635, 3636, 3637, 3638, 3639, 3640, 3641, 3642, 3643, 3644, 3645, 3646, 3655, 3656, 3657, 3658, 3659, 3660, 3661, 3662]:
				continue
			text_to_image(chr(i), font["path"], font["size"], f"output/{font['name']}/thai/{i:04x}.png", font["cell_height"], font["padding_x"], False)

	if generate_latin:
		print("Generating latin characters...")
		for i in range(33, 127):
			text_to_image(chr(i), font["path"], font["size"], f"output/{font['name']}/latin/{i:04x}.png", font["cell_height"], font["padding_x"], False)

	if generate_thaiji:
		combinations = generate_combinations()
		print(f"Generating {len(combinations)} Thaijis...")
		start = 3712
		for c in combinations:
			text_to_image(c, font["path"], font["size"], f"output/{font['name']}/thaiji/{start:04x}.png", font["cell_height"], font["padding_x"])
			start += 1

fonts = [
	{
		"name": "font_01",
		"path": "fonts/Quark-Bold.otf",
		"size": 38,
		"cell_height": 52,
		"padding_x": 5,
	},
	{
		"name": "font_36",
		"path": "fonts/Quark-Light.otf",
		"size": 38,
		"cell_height": 52,
		"padding_x": 5,
	},
	{
		"name": "font_11",
		"path": "fonts/LayijiMahaniyomV1.ttf",
		"size": 44, # TODO: adjust font size
		"cell_height": 64, # TODO: adjust cell height
		"padding_x": 5, # TODO: adjust padding x
	},
	{
		"name": "font_05",
		"path": "fonts/Quark-Bold.otf",
		"size": 38,
		"cell_height": 52,
		"padding_x": 5,
	},
]

# generate_thaiji_csv(combinations, "output/thaiji.csv")
# generate_shell_code(combinations, "output/code.txt")

# generate_font_images(fonts[0], generate_thai=True, generate_latin=True, generate_thaiji=True) # font_01
# generate_font_images(fonts[1], generate_thai=True, generate_latin=True, generate_thaiji=True) # font_36
generate_font_images(fonts[2], generate_thai=True, generate_latin=True, generate_thaiji=True) # font_11
# generate_font_images(fonts[3], generate_thai=True, generate_latin=True, generate_thaiji=True) # font_05