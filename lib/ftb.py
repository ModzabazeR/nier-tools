import csv
import lib.unicodetools as ut

class Character:
	def __init__(self, unicode: int, texId: int, width: int, height: int, u: int, v: int):
		self.unicode = unicode
		self.texId = texId
		self.width = width
		self.height = height
		self.u = u
		self.v = v

	def swap_info(self, char: 'Character'):
		# swap everything except unicode
		self.texId, self.width, self.height, self.u, self.v = char.texId, char.width, char.height, char.u, char.v

	def __str__(self) -> str:
		return f"Character(unicode={self.unicode}[{chr(self.unicode)}], texId={self.texId}, width={self.width}, height={self.height}, u={self.u}, v={self.v})"

class File:
	@staticmethod
	def parse(path):
		with open(path, "rb") as f:
			file = File()
			magic = f.read(4)
			if magic != b"FTB\x20":
				raise ValueError("Invalid file")
			
			f.seek(0x7a)
			file.chars_count = int.from_bytes(f.read(2), "little")
			
			f.seek(0x80)
			file.chars_offset = int.from_bytes(f.read(4), "little")

			file.characters = []
			f.seek(file.chars_offset)
			for _ in range(file.chars_count):
				unicode = int.from_bytes(f.read(2), "little")
				texId = int.from_bytes(f.read(2), "little")
				width = int.from_bytes(f.read(2), "little")
				height = int.from_bytes(f.read(2), "little")
				u = int.from_bytes(f.read(2), "little")
				v = int.from_bytes(f.read(2), "little")
				file.characters.append(Character(unicode, texId, width, height, u, v))

			# read remaining bytes
			file.footer = f.read()

			# read whole file but before the characters
			f.seek(0)
			file.header = f.read(file.chars_offset)

			return file

	def tranform_thai(self):
		for char in self.characters:
			if (char.unicode >= 3585 and char.unicode <= 3675) or (char.unicode >= 63232 and char.unicode <= 63258):
				char.unicode = ut.UNICODE_MAP_DEC[char.unicode]
		# sort by unicode
		self.characters.sort(key=lambda char: char.unicode)

	# for testing purposes
	def to_csv(self, output_path: str):
		with open(output_path, "w", newline="", encoding="utf-16") as f:
			writer = csv.writer(f)
			writer.writerow(["unicode", "char", "texId", "width", "height", "u", "v"])
			for char in self.characters:
				writer.writerow([char.unicode, chr(char.unicode), char.texId, char.width, char.height, char.u, char.v])

	def rewrite(self, path):
		with open(path, "wb") as f:
			# write header
			f.write(self.header)

			# write characters
			for char in self.characters:
				f.write(char.unicode.to_bytes(2, "little"))
				f.write(char.texId.to_bytes(2, "little"))
				f.write(char.width.to_bytes(2, "little"))
				f.write(char.height.to_bytes(2, "little"))
				f.write(char.u.to_bytes(2, "little"))
				f.write(char.v.to_bytes(2, "little"))

			# write footer
			f.write(self.footer)

if __name__ == "__main__":
	ftb_path = "C:/Users/modda/OneDrive/Documents/OmegaT Project/assembly/font/font_11.dat/font_11.ftb"
	result = File.parse(ftb_path)
	# result.tranform_thai()
	# result.rewrite("C:/Users/modda/OneDrive/Documents/OmegaT Project/assembly/font/font_11.dat/font_11_test.ftb")