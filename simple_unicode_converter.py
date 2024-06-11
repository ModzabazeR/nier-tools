import lib.unicodetools as ut

while True:
	char = input("Enter a character: ")

	if char == "exit":
		break

	if len(char) > 1 and not char.startswith("\\u"):
		print("Please enter only one character.")
		continue

	converted_char = char
	if char.startswith("\\u"):
		char = char[2:]
		char = chr(int(char, 16))
		converted_char = char

	try:
		converted_char = ut.UNICODE_MAP[char]
	except KeyError:
		pass

	print(f"\\u{ord(char):04x} ({char}) => \\u{ord(converted_char):04x}")