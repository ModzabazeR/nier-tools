UNICODE_MAP = {
	# Thai to Latin Extended-A
	"\u0e01": "\u0100",
	"\u0e02": "\u0101",
	"\u0e03": "\u0102",
	"\u0e04": "\u0103",
	"\u0e05": "\u0104",
	"\u0e06": "\u0105",
	"\u0e07": "\u0106",
	"\u0e08": "\u0107",
	"\u0e09": "\u0108",
	"\u0e0a": "\u0109",
	"\u0e0b": "\u010a",
	"\u0e0c": "\u010b",
	"\u0e0d": "\u010c",
	"\u0e0e": "\u010d",
	"\u0e0f": "\u010e",
	"\u0e10": "\u010f",
	"\u0e11": "\u0110",
	"\u0e12": "\u0111",
	"\u0e13": "\u0112",
	"\u0e14": "\u0113",
	"\u0e15": "\u0114",
	"\u0e16": "\u0115",
	"\u0e17": "\u0116",
	"\u0e18": "\u0117",
	"\u0e19": "\u0118",
	"\u0e1a": "\u0119",
	"\u0e1b": "\u011a",
	"\u0e1c": "\u011b",
	"\u0e1d": "\u011c",
	"\u0e1e": "\u011d",
	"\u0e1f": "\u011e",
	"\u0e20": "\u011f",
	"\u0e21": "\u0120",
	"\u0e22": "\u0121",
	"\u0e23": "\u0122",
	"\u0e24": "\u0123",
	"\u0e25": "\u0124",
	"\u0e26": "\u0125",
	"\u0e27": "\u0126",
	"\u0e28": "\u0127",
	"\u0e29": "\u0128",
	"\u0e2a": "\u0129",
	"\u0e2b": "\u012a",
	"\u0e2c": "\u012b",
	"\u0e2d": "\u012c",
	"\u0e2e": "\u012d",
	"\u0e2f": "\u012e",
	"\u0e30": "\u012f",
	"\u0e31": "\u0130",
	"\u0e32": "\u0131",
	"\u0e33": "\u0132",
	"\u0e34": "\u0133",
	"\u0e35": "\u0134",
	"\u0e36": "\u0135",
	"\u0e37": "\u0136",
	"\u0e38": "\u0137",
	"\u0e39": "\u0138",
	"\u0e3a": "\u0139",
	"\u0e3f": "\u013a",
	"\u0e40": "\u013b",
	"\u0e41": "\u013c",
	"\u0e42": "\u013d",
	"\u0e43": "\u013e",
	"\u0e44": "\u013f",
	"\u0e45": "\u0140",
	"\u0e46": "\u0141",
	"\u0e47": "\u0142",
	"\u0e48": "\u0143",
	"\u0e49": "\u0144",
	"\u0e4a": "\u0145",
	"\u0e4b": "\u0146",
	"\u0e4c": "\u0147",
	"\u0e4d": "\u0148",
	"\u0e4e": "\u0149",
	"\u0e4f": "\u014a",
	"\u0e50": "\u014b",
	"\u0e51": "\u014c",
	"\u0e52": "\u014d",
	"\u0e53": "\u014e",
	"\u0e54": "\u014f",
	"\u0e55": "\u0150",
	"\u0e56": "\u0151",
	"\u0e57": "\u0154",
	"\u0e58": "\u0155",
	"\u0e59": "\u0156",
	"\u0e5a": "\u0157",
	"\u0e5b": "\u0158",
	# Thai PUA to Latin Extended-A
	"\uf700": "\u0159",
	"\uf701": "\u015a",
	"\uf702": "\u015b",
	"\uf703": "\u015c",
	"\uf704": "\u015d",
	"\uf705": "\u015e",
	"\uf706": "\u015f",
	"\uf707": "\u0162",
	"\uf708": "\u0163",
	"\uf709": "\u0164",
	"\uf70a": "\u0165",
	"\uf70b": "\u0166",
	"\uf70c": "\u0167",
	"\uf70d": "\u0168",
	"\uf70e": "\u0169",
	"\uf70f": "\u016a",
	"\uf710": "\u016b",
	"\uf711": "\u016c",
	"\uf712": "\u016d",
	"\uf713": "\u016e",
	"\uf714": "\u016f",
	"\uf715": "\u0170",
	"\uf716": "\u0171",
	"\uf717": "\u0172",
	"\uf718": "\u0173",
	"\uf719": "\u0174",
	"\uf71a": "\u0175",
}

UNICODE_MAP_DEC = {ord(k): ord(v) for k, v in UNICODE_MAP.items()}

# tranform \uxxxx to \\uxxxx in a loop
UNICODE_MAP_ESCAPED = {
	k.encode("unicode-escape").decode("utf-8"): v.encode("unicode-escape").decode("utf-8") for k, v in UNICODE_MAP.items()
}

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

if __name__ == "__main__":
	# print(UNICODE_MAP)
	# print(UNICODE_MAP_DEC)
	print(UNICODE_MAP_ESCAPED)