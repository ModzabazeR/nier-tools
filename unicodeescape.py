from tkinter import filedialog, Tk
import lib.unicodetools as ut
import os

# Normal consonants (NC), without extra ascender/descender
NC = ["ก", "ข", "ฃ", "ค", "ฅ", "ฆ", "ง", "จ", "ฉ", "ช", "ซ", "ฌ", "ฑ", "ฒ", "ณ", "ด", "ต", "ถ", "ท", "ธ", "น", "บ", "ผ", "พ", "ภ", "ม", "ย", "ร", "ล", "ว", "ศ", "ษ", "ส", "ห", "อ", "ฮ"]
# Consonants with right extra ascender (AC), namely ป (PO PLA, U+0E1B), ฝ (FO FA, U+0E1D), ฟ (FO FAN, U+0E1F) and in some fonts ฬ (LO CHULA, U+0E2C)
AC = ["ป", "ฝ", "ฟ", "ฬ"]
# Consonants with removable descender (RC), namely ญ (YO YING, U+0E0D) and ฐ (THO THAN, U+0E10)
RC = ["ญ", "ฐ"]
# Consonants with strict descender (DC), namely ฎ (DO CHADA, U+0E0E) and ฏ (TO PATAK, U+0E0F)
DC = ["ฎ", "ฏ"]

# Normal vowels (NV)
NV = ["ะ", "า", "เ", "แ", "โ", "ใ", "ไ", "ๅ", "ๆ"]
# Below vowels (BV)
BV = ["ุ", "ู"]
# Shifted down below vowels (SDBV)
SDBV = ["\\uf718", "\\uf719"]
# Above vowels (AV)
AV = ['ั', 'ํ', 'ิ', 'ี', 'ึ', 'ื', "็"]
# Left vowels (LV)
LV = ["\\uf710", "\\uf711", "\\uf701", "\\uf702", "\\uf703", "\\uf704", "\\uf712"]

# all thai tones (T)
tone = ["่", "้", "๊", "๋", "์"]
# Low left tones (LLT)
LLT = ["\\uf705", "\\uf706", "\\uf707", "\\uf708", "\\uf709"]
# Low right tones (LRT) - same x as normal
LRT = ["\\uf70a", "\\uf70b", "\\uf70c", "\\uf70d", "\\uf70e"]
# Upper left tones (ULT)
ULT = ["\\uf713", "\\uf714", "\\uf715", "\\uf716", "\\uf717"]

def decompose_sara_am(text: str):
	# SARA AM (U+0E33) must be decomposed into NIKHAHIT (U+0E4D) and SARA AA (U+0E32).
	# And if a tone mark (T) is present before it, the NIKHAHIT must be reordered so it comes before the tone mark.
	text = text.replace("\u0e33", "\u0e4d\u0e32")
	for i, c in enumerate(text):
		if c == "\u0e4d":
			if i > 0 and text[i-1] in tone:
				# move NIKAHIT to the left
				text = text[:i-1] + "\u0e4d" + text[i-1] + text[i+1:]
			break
	return text

def above_mark_with_AC(text: str):
	# Any above-base combining mark (T, AV) that combines to consonant with extra ascender (AC) must be shifted left.
	# This is done by replacing the tone mark with 
	# case 1: AC + T (replace T with LLT)
	# case 2: AC + AV + T (replace T with ULT)
	# case 3: AC + BV + T (replace T with LLT)
	# finally: replace AV with LV
	
	# case 1
	for ac in AC:
		for t in tone:
			text = text.replace(ac+t, ac+LLT[tone.index(t)])
	
	# case 2
	for ac in AC:
		for av in AV:
			for t in tone:
				text = text.replace(ac+av+t, ac+av+ULT[tone.index(t)])

	# case 3
	for ac in AC:
		for bv in BV:
			for t in tone:
				text = text.replace(ac+bv+t, ac+bv+LLT[tone.index(t)])
	
	# finally
	for ac in AC:
		for av in AV:
			text = text.replace(ac+av, ac+LV[AV.index(av)])

	return text

def tone_without_AV(text: str):
	# If tone mark (T) is present without upper vowel (AV), it must be lower down.
	# This is done by replacing the tone mark with a low right tone mark (LRT) if a tone mark is placed immediately after a consonant.

	# case 1: C + T
	for c in NC+RC+DC:
		for t in tone:
			text = text.replace(c+t, c+LRT[tone.index(t)])

	# case 2: C + BV + T
	for c in NC+RC+DC:
		for bv in BV:
			for t in tone:
				text = text.replace(c+bv+t, c+bv+LRT[tone.index(t)])

	return text

def deal_with_DC(text: str):
	# If below vowel (BV) combines to consonant with strict descender (DC), it must be lowered down.
	# This is done by replacing the below vowel with a shifted down below vowel (SDBV).
	for dc in DC:
		for bv in BV:
			text = text.replace(dc+bv, dc+SDBV[BV.index(bv)])

	return text

def deal_with_RC(text: str):
	# If a RC is followed by a BV, use \uf700 to replace the ฐ and \uf70f to replace the ญ.
	for rc in RC:
		for bv in BV:
			if rc == "ฐ":
				text = text.replace(rc+bv, "\\uf700"+bv)
			else:
				text = text.replace(rc+bv, "\\uf70f"+bv)
	
	return text

def tranform_thai(text: str):
	for map in ut.UNICODE_MAP_ESCAPED:
		text = text.replace(map, ut.UNICODE_MAP_ESCAPED[map])
	return text

def string_to_unicode_escape(text: str, is_tranform: bool = True):
	text = decompose_sara_am(text)
	text = above_mark_with_AC(text)
	text = tone_without_AV(text)
	text = deal_with_DC(text)
	text = deal_with_RC(text)

	result = ""
	for c in text:
		if ord(c) >= 3585 and ord(c) <= 3675:
			result += f"\\u{ord(c):04x}"
		else:
			result += c

	if is_tranform:
		result = tranform_thai(result)

	return result

# test_result = r"\u0e1e\u0e35\u0e48\u0e1b\uf711\uf716\u0e32\u0e0e\uf719\u0e19\u0e39\uf70d\u0e40\u0e1b\uf705\u0e32\u0e1d\u0e38\uf705\u0e19\u0e2b\uf70f\u0e39\uf70a\u0e01\uf70b\u0e19\u0e1b\uf702\uf713\u0e40\u0e17\uf70a\u0e32\uf700\u0e38\u0e25\u0e35"
# print(string_to_unicode_escape("พี่ป๋ำฎูนู๋เป่าฝุ่นหญู่ก้นปี่เท่าฐุลี") == test_result)

def main():
	Tk().withdraw()
	file_paths = filedialog.askopenfilenames(initialdir="C:/Users/modda/OneDrive/Documents/OmegaT Project/target", title="Select translated files")
	save_dir = filedialog.askdirectory(initialdir="C:/Users/modda/OneDrive/Documents/OmegaT Project/unicodeescaped", title="Select save directory")
	
	# is_fake_latin = input("Is the text in fake Latin? (y/n): ").lower() == "y"
	for file_path in file_paths:
		file_name = os.path.basename(file_path)
		print(f"Processing {file_name}...")

		escaped_text = ""
		with open(file_path, "r", encoding="utf-8") as f:
			text = f.read()
			escaped_text = string_to_unicode_escape(text)

		with open(f"{save_dir}/{file_name}", "w", encoding="utf-8") as f:
			f.write(escaped_text)

if __name__ == "__main__":
	main()