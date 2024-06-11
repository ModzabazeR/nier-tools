import lib.ftb as ftb

gamerip_path = "C:/Users/modda/OneDrive/Documents/Modding/NieR/gamerip/data009.cpk/font/nier2blender_extracted"
ftb_paths = ktb_paths = [f"{gamerip_path}/font_{i}.dat/font_{i}.ftb" for i in ["00", "01", "04", "05", "11"]]
chars_lst = []

for ftb_path in ftb_paths:
	result = ftb.File.parse(ftb_path)
	# check unicode in range latin extended-A
	chars_lst.append([char.unicode for char in result.characters if char.unicode >= 256 and char.unicode <= 383])

print(chars_lst)