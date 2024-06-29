import csv
import os
from dotenv import load_dotenv

load_dotenv()

def parse_properties(path: str) -> "dict[str, str]":
	properties = {}
	with open(path, "r", encoding="utf-8") as f:
		for line in f.readlines():
			if line.startswith("#"):
				continue
			key, value = line.rstrip("\n").split("=", 1)
			properties[key] = value
	return properties

def pack_csv(output_path: str, eng_path: str, jp_path: str, th_path: str = "") -> None:
	output_path_base = os.path.dirname(output_path)
	if not os.path.exists(output_path_base):
		os.makedirs(output_path_base)
	
	eng_properties = parse_properties(eng_path)
	jp_properties = parse_properties(jp_path)
	th_properties = parse_properties(th_path) if th_path else None

	with open(output_path, "w", newline="", encoding="utf-8") as f:
		writer = csv.writer(f)
		writer.writerow(["Key", "English", "Japanese", "Thai"])
		for key in eng_properties:
			eng_value = eng_properties.get(key)
			jp_value = jp_properties.get(key, "null")
			th_value = th_properties.get(key, "") if th_properties else ""

			if th_value == eng_value:
				th_value = ""

			writer.writerow([key, eng_value, jp_value, th_value])

def main():
	eng_base_path = os.getenv("ENG_BASE_PATH")
	jp_base_path = os.getenv("JP_BASE_PATH")
	th_base_path = os.getenv("TH_BASE_PATH")
	output_base_path = os.getenv("CSV_BASE_PATH")

	base_files = [file for file in os.listdir(eng_base_path) if file.endswith(".properties")]

	for file in base_files:
		print(f"Processing {file}...")
		file_name = file.split(".")[0]
		if file_name in ["subtitle0482", "messloading", "messending", "g11516_2ccba2ea_scp", "global_638e40c8_scp", "messcore", "messtitle", "messoption", "core_hap", "txt_pause_add", "txt_core_add", "p100_6695192d_scp", "subtitle0170"]:
			pack_csv(f"{output_base_path}/{file_name}.csv", f"{eng_base_path}/{file}", f"{jp_base_path}/{file}", f"{th_base_path}/{file_name}_th.properties")
		else:
			pack_csv(f"{output_base_path}/{file_name}.csv", f"{eng_base_path}/{file}", f"{jp_base_path}/{file}")

if __name__ == "__main__":
	main()