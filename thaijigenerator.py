from lib.unicodetools import NC, AC, RC, DC, NV, BV, AV, tone, HCC, MCC, LCC
from PIL import Image, ImageDraw, ImageFont
from unicodeescape import string_to_unicode_escape
import os
import csv

def find_consonant(text: str) -> str:
	for c in NC + AC + RC + DC + ["\uf700", "\uf70f"]:
		if c in text:
			return c
	if len(text) == 1:
		for v in NV:
			if v == text:
				return v
		for latin in range(33, 127):
			if chr(latin) == text:
				return chr(latin)
		for thai in range(3585, 3676):
			if chr(thai) == text:
				return chr(thai)
	return "ก"

def text_to_image(text: str, font_path: str, font_size: int, image_path: str, cell_height: int, padding_x: int = 5, do_escape: bool = True, font_name: str = None):
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
	draw.fontmode = "RGBA"

	# align text center and draw
	text_width, text_height = bbox[2:]
	if font_name == "font_11":
		draw.text(((image.width - text_width) // 2, (image.height - text_height) // 2), text, font=font, fill=(255, 255, 255, 255), stroke_width=1, stroke_fill=(255, 255, 255, 0))
	elif font_name == "font_05":
		# draw text shadow
		shadow_color = (50, 50, 50, 0)
		draw.text(((image.width - text_width) // 2 + 1, (image.height - text_height) // 2 + 1), text, font=font, fill=shadow_color)
		draw.text(((image.width - text_width) // 2, (image.height - text_height) // 2), text, font=font, fill=(200, 200, 200, 255))
	else:
		draw.text(((image.width - text_width) // 2, (image.height - text_height) // 2), text, font=font, fill=(255, 255, 255, 255))

	# pixels = image.load()
	# if font_name != "font_11":
	# 	# copy pixel values from alpha to r, g, and b channels
	# 	for y in range(image.height):
	# 		for x in range(image.width):
	# 			alpha = pixels[x, y][3]
	# 			pixels[x, y] = (alpha, alpha, alpha, alpha)
		
	if font_name == "font_11":
		image = image.crop((0, 0, image.width, image.height - 10))
	elif font_name == "font_04":
		image = image.crop((0, 0, image.width, image.height - 14))

	# Save image
	image.save(image_path)

def generate_combinations(explicit_add: "list[str]" = None) -> "list[str]":
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
						(consonant in HCC and t in ["๊", "๋"] and vowel != "ั") or \
						(consonant in LCC and t in ["๊", "๋"] and vowel != "ั"):
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

	if explicit_add:
		combinations += explicit_add

	print(f"Generated {len(combinations)} combinations...")

	return sorted(list(set(combinations)))

COMBINATIONS = generate_combinations(["ธุ์"])

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

def generate_font_images(font_name: str, fonts: dict, generate_thai: bool = False, generate_latin: bool = False, generate_thaiji: bool = False):
	print(f"----* Generating images for {font_name}... *----")

	font = fonts[font_name]

	if generate_thai:
		print("Generating normal Thai characters...")
		for i in range(3585, 3676):
			if i in [3633, 3635, 3636, 3637, 3638, 3639, 3640, 3641, 3642, 3643, 3644, 3645, 3646, 3655, 3656, 3657, 3658, 3659, 3660, 3661, 3662]:
				continue
			text_to_image(chr(i), font["path"], font["size"], f"output/{font_name}/thai/{i:04x}.png", font["cell_height"], font["padding_x"], False, font_name=font_name)

	if generate_latin:
		print("Generating latin characters...")
		for i in range(33, 127):
			text_to_image(chr(i), font["path"], font["size"], f"output/{font_name}/latin/{i:04x}.png", font["cell_height"], font["padding_x"], False, font_name=font_name)

	if generate_thaiji:
		start = 3712
		print("Generating Thaiji characters...")
		for c in COMBINATIONS:
			text_to_image(c, font["path"], font["size"], f"output/{font_name}/thaiji/{start:04x}.png", font["cell_height"], font["padding_x"], font_name=font_name)
			start += 1

fonts = {
	"font_01": {
		"path": "fonts/FC Iconic Regular.ttf",
		"size": 38,
		"cell_height": 52,
		"padding_x": 5,
	},
	"font_36": {
		"path": "fonts/FC Iconic Light.ttf",
		"size": 38,
		"cell_height": 52,
		"padding_x": 5,
	},
	"font_11": {
		"path": "fonts/LayijiMahaniyomV1.ttf",
		"size": 38,
		"cell_height": 60,
		"padding_x": 4,
	},
	"font_05": {
		"path": "fonts/FC Iconic Medium.ttf",
		"size": 30,
		"cell_height": 41,
		"padding_x": 6,
	},
	"font_04": {
		"path": "fonts/supermarket_test.ttf",
		"size": 38,
		"cell_height": 68,
		"padding_x": 5,
	},
	"font_00": {
		"path": "fonts/2005_iannnnnAMD.ttf",
		"size": 52,
		"cell_height": 52,
		"padding_x": 5,
	},
	"font_03": {
		"path": "fonts/TP Tankhun Bold.ttf",
		"size": 54,
		"cell_height": 60,
		"padding_x": 5,
	},
	"font_02": {
		"path": "fonts/FC Iconic Medium.ttf",
		"size": 72,
		"cell_height": 80,
		"padding_x": 5,
	}
}

generate_thaiji_csv(COMBINATIONS, "output/thaiji.csv")
# generate_shell_code(COMBINATIONS, "output/code.txt")

generate_font_images("font_00", fonts, generate_thai=True, generate_latin=True, generate_thaiji=True)
generate_font_images("font_01", fonts, generate_thai=True, generate_latin=True, generate_thaiji=True)
generate_font_images("font_02", fonts, generate_thai=True, generate_latin=True, generate_thaiji=True)
generate_font_images("font_03", fonts, generate_thai=True, generate_latin=True, generate_thaiji=True)
generate_font_images("font_04", fonts, generate_thai=True, generate_latin=True, generate_thaiji=True)
generate_font_images("font_05", fonts, generate_thai=True, generate_latin=True, generate_thaiji=True)
generate_font_images("font_11", fonts, generate_thai=True, generate_latin=True, generate_thaiji=True)
generate_font_images("font_36", fonts, generate_thai=True, generate_latin=True, generate_thaiji=True)