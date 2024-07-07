import csv
import os
from dotenv import load_dotenv
from unicodeescape import string_to_thaiji_escape

load_dotenv()

def create_properties_file(output_path: str, key_list: "list[str]", th_value_list: "list[str]", en_value_list: "list[str]") -> None:
	output_path_base = os.path.dirname(output_path)
	if not os.path.exists(output_path_base):
		os.makedirs(output_path_base)
	
	with open(output_path, "w", encoding="utf-8") as f:
		for key, th_value, en_value in zip(key_list, th_value_list, en_value_list):
			if th_value == "":
				f.write(f"{key}={en_value}\n")
			else:
				f.write(f"{key}={string_to_thaiji_escape(th_value)}\n")

def parse_csv(path: str) -> "tuple[list[str], list[str]]":
	key_list = []
	en_value_list = []
	th_value_list = []
	with open(path, "r", encoding="utf-8") as f:
		reader = csv.reader(f)
		next(reader)
		for row in reader:
			key_list.append(row[0]) # key
			en_value_list.append(row[1]) # english
			th_value_list.append(row[3]) # thai
	return key_list, th_value_list, en_value_list

def main():
	csv_base_path = os.getenv("CSV_BASE_PATH")
	th_base_path = os.getenv("TH_BASE_PATH")
	csv_files = [file for file in os.listdir(csv_base_path) if file.endswith(".csv")]

	for file in csv_files:
		print(f"Processing {file}...")
		file_name = file.split(".")[0]
		key_list, th_value_list, en_value_list = parse_csv(f"{csv_base_path}/{file}")
		create_properties_file(f"{th_base_path}/{file_name}_th.properties", key_list, th_value_list, en_value_list)

if __name__ == "__main__":
	main()