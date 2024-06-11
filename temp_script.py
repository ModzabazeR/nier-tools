import lib.unicodetools as ut

text = r"""--char $((16#0e01)) $((16#0e02)) \
--char $((16#0e01)) $((16#0e03)) \
--char $((16#0e01)) $((16#0e04)) \
--char $((16#0e01)) $((16#0e05)) \
--char $((16#0e01)) $((16#0e06)) \
--char $((16#0e01)) $((16#0e07)) \
--char $((16#0e01)) $((16#0e08)) \
--char $((16#0e01)) $((16#0e09)) \
--char $((16#0e01)) $((16#0e0a)) \
--char $((16#0e01)) $((16#0e0b)) \
--char $((16#0e01)) $((16#0e0c)) \
--char $((16#0e01)) $((16#0e0d)) \
--char $((16#0e01)) $((16#0e0e)) \
--char $((16#0e01)) $((16#0e0f)) \
--char $((16#0e01)) $((16#0e10)) \
--char $((16#0e01)) $((16#0e11)) \
--char $((16#0e01)) $((16#0e12)) \
--char $((16#0e01)) $((16#0e13)) \
--char $((16#0e01)) $((16#0e14)) \
--char $((16#0e01)) $((16#0e15)) \
--char $((16#0e01)) $((16#0e16)) \
--char $((16#0e01)) $((16#0e17)) \
--char $((16#0e01)) $((16#0e18)) \
--char $((16#0e01)) $((16#0e19)) \
--char $((16#0e01)) $((16#0e1a)) \
--char $((16#0e01)) $((16#0e1b)) \
--char $((16#0e01)) $((16#0e1c)) \
--char $((16#0e01)) $((16#0e1d)) \
--char $((16#0e01)) $((16#0e1e)) \
--char $((16#0e01)) $((16#0e1f)) \
--char $((16#0e01)) $((16#0e20)) \
--char $((16#0e01)) $((16#0e21)) \
--char $((16#0e01)) $((16#0e22)) \
--char $((16#0e01)) $((16#0e23)) \
--char $((16#0e01)) $((16#0e24)) \
--char $((16#0e01)) $((16#0e25)) \
--char $((16#0e01)) $((16#0e26)) \
--char $((16#0e01)) $((16#0e27)) \
--char $((16#0e01)) $((16#0e28)) \
--char $((16#0e01)) $((16#0e29)) \
--char $((16#0e01)) $((16#0e2a)) \
--char $((16#0e01)) $((16#0e2b)) \
--char $((16#0e01)) $((16#0e2c)) \
--char $((16#0e01)) $((16#0e2d)) \
--char $((16#0e01)) $((16#0e2e)) \
--char $((16#0e34)) $((16#0e31)) \
--char $((16#0e34)) $((16#0e35)) \
--char $((16#0e34)) $((16#0e36)) \
--char $((16#0e34)) $((16#0e37)) \
--char $((16#0e34)) $((16#0e47)) \
--char $((16#0e34)) $((16#0e4d)) \
--char $((16#0e38)) $((16#0e39)) \
--char $((16#0e48)) $((16#0e49)) \
--char $((16#0e48)) $((16#0e4a)) \
--char $((16#0e48)) $((16#0e4b)) \
--char $((16#0e48)) $((16#0e4c)) \
--char $((16#f701)) $((16#f702)) \
--char $((16#f701)) $((16#f703)) \
--char $((16#f701)) $((16#f704)) \
--char $((16#f701)) $((16#f710)) \
--char $((16#f701)) $((16#f711)) \
--char $((16#f701)) $((16#f712)) \
--char $((16#f705)) $((16#f706)) \
--char $((16#f705)) $((16#f707)) \
--char $((16#f705)) $((16#f708)) \
--char $((16#f705)) $((16#f709)) \
--char $((16#f713)) $((16#f714)) \
--char $((16#f713)) $((16#f715)) \
--char $((16#f713)) $((16#f716)) \
--char $((16#f713)) $((16#f717)) \
--char $((16#f70a)) $((16#f70b)) \
--char $((16#f70a)) $((16#f70c)) \
--char $((16#f70a)) $((16#f70d)) \
--char $((16#f70a)) $((16#f70e)) \
--char $((16#f718)) $((16#f719)) \
--char $((16#0e1b)) $((16#0e1d)) \
--char $((16#0e1b)) $((16#0e1f))"""

text_lst = text.split("\n")
result = []
for line in text_lst:
	target = line.find("16#")
	right = line[target + 7:]
	middle = line[target:target + 7]

	target2 = right.find("16#")
	middle2 = right[target2:target2 + 7]

	middle_hex = middle.split("#")[1]
	middle2_hex = middle2.split("#")[1]
	
	unicode = int(middle_hex, 16)
	unicode2 = int(middle2_hex, 16)
	
	try:
		unicode = ut.UNICODE_MAP_DEC[unicode]
	except KeyError:
		pass
	try:
		unicode2 = ut.UNICODE_MAP_DEC[unicode2]
	except KeyError:
		pass
	
	print(f"--char $((16#{hex(unicode)[2:].zfill(4)})) $((16#{hex(unicode2)[2:].zfill(4)})) \\")
	# print(f"{left}16#{hex(unicode)[2:].zfill(4)}{right}")