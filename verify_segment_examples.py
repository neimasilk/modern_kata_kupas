from modern_kata_kupas import ModernKataKupas

separator = ModernKataKupas()

examples = [
    "makanan",
    "dibaca",
    "memukul",
    "mengupas",
    "keberhasilan",
    "mempertaruhkan",
    "rumah-rumah",
    "mobil-mobilan",
    "bermain-main",
    "bukunyalah",
    "buku-bukunya" # From "Output Format" section
]

expected_outputs = {
    "makanan": "makan~an",
    "dibaca": "di~baca",
    "memukul": "meN~pukul",
    "mengupas": "meN~kupas",
    "keberhasilan": "ke~ber~hasil~an",
    "mempertaruhkan": "meN~per~taruh~kan",
    "rumah-rumah": "rumah~ulg",
    "mobil-mobilan": "mobil~ulg~an",
    "bermain-main": "ber~main~ulg",
    "bukunyalah": "buku~nya~lah",
    "buku-bukunya": "buku~ulg~nya"
}

print("Verifying segment() examples from README.md:")
all_match = True
for word in examples:
    actual_output = separator.segment(word)
    expected_output = expected_outputs[word]
    if actual_output == expected_output:
        print(f"OK: separator.segment(\"{word}\") -> \"{actual_output}\" (Matches expected)")
    else:
        all_match = False
        print(f"MISMATCH: separator.segment(\"{word}\")")
        print(f"  Actual:   \"{actual_output}\"")
        print(f"  Expected: \"{expected_output}\"")

if all_match:
    print("\nAll segment() examples in README.md are consistent with current output.")
else:
    print("\nSome segment() examples in README.md need updating!")
