BenDictionary = dict[str, "Bencode"]
BenList = list["Bencode"]
Bencode = str | bytes | int | BenList | BenDictionary
