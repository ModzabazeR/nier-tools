import unicodetools as ut

class File:
	@staticmethod
	def parse(path):
		with open(path, "rb") as f:
			file = File()
			file.pairs_amount = int.from_bytes(f.read(2), "little")

			file.pairs = []
			for _ in range(file.pairs_amount):
				left = int.from_bytes(f.read(2), "little")
				right = int.from_bytes(f.read(2), "little")
				amount = int.from_bytes(f.read(2), "little")
				file.pairs.append({"left": left, "right": right, "amount": amount})
			
			return file
		
	def transform_thai(self):
		for pair in self.pairs:
			if (pair["left"] >= 3585 and pair["left"] <= 3675) or (pair["left"] >= 63232 and pair["left"] <= 63258):
				pair["left"] = ut.UNICODE_MAP_DEC[pair["left"]]
			if (pair["right"] >= 3585 and pair["right"] <= 3675) or (pair["right"] >= 63232 and pair["right"] <= 63258):
				pair["right"] = ut.UNICODE_MAP_DEC[pair["right"]]

		# sort by left then right
		self.pairs.sort(key=lambda x: (x['left'] if x['left'] else -1, x['right'] if x['right'] else -1))

		return self
	
	def rewrite(self, path):
		with open(path, "wb") as f:
			f.write(len(self.pairs).to_bytes(2, "little"))
			for pair in self.pairs:
				f.write(pair["left"].to_bytes(2, "little"))
				f.write(pair["right"].to_bytes(2, "little"))
				f.write(pair["amount"].to_bytes(2, "little"))

	def __str__(self) -> str:
		return f"File(pairs_amount={self.pairs_amount}, pairs={self.pairs})"
	
if __name__ == "__main__":
	base_path = "C:/Users/modda/OneDrive/Documents/OmegaT Project/unpacked/font"
	ktb_paths = [
					f"{base_path}/font_01.dat/font_01.ktb", 
					f"{base_path}/font_36.dat/font_36.ktb",
					f"{base_path}/font_04.dat/font_04.ktb",
					f"{base_path}/font_05.dat/font_05.ktb",
					f"{base_path}/font_11.dat/font_11.ktb",
				 ]
	
	for ktb_file in ktb_paths:
		file = File.parse(ktb_file)
		file.transform_thai()
		file.rewrite(ktb_file)
		print(f"Successfully transformed {ktb_file}")
		# break