# TODO: marshaling
# TODO: add logging
# TODO: use errors as values instead of raising them


from .bencode_types import Bencode


def encode(bencode: Bencode, buf: bytearray | None = None) -> bytes:
	buf = encode_value(bencode)
	return bytes(buf)


def encode_value(bencode: Bencode, buf: bytearray | None = None) -> bytearray:
	if buf is None:
		buf = bytearray()

	if isinstance(bencode, list):
		return encode_list(bencode, buf)
	elif isinstance(bencode, dict):
		return encode_dictionary(bencode, buf)
	elif isinstance(bencode, int):
		return encode_integer(bencode, buf)
	elif isinstance(bencode, (bytes, bytearray, str)):
		return encode_bytestring(bencode, buf)


def encode_bytestring(bs: bytes | bytearray | str, buf: bytearray | None = None) -> bytearray:
	if buf is None:
		buf = bytearray()

	size = len(bs)
	buf += str(size).encode()
	buf.append(ord(b":"))

	if isinstance(bs, str):
		buf += bs.encode()
	else:
		buf += bs

	return buf


def encode_integer(i: int, buf: bytearray | None = None) -> bytearray:
	if buf is None:
		buf = bytearray()
	buf += f"i{i}e".encode()
	return buf


def encode_list(ls: list[Bencode], buf: bytearray | None = None) -> bytearray:
	if buf is None:
		buf = bytearray()

	buf.append(ord(b"l"))
	for bencode in ls:
		encode_value(bencode, buf)
	buf.append(ord(b"e"))

	return buf


def encode_dictionary(d: dict[str, Bencode], buf: bytearray | None = None) -> bytearray:
	if buf is None:
		buf = bytearray()

	buf.append(ord(b"d"))
	keys = sorted((key for key in d))
	for key in keys:
		encode_bytestring(key, buf)
		encode_value(d[key], buf)
	buf.append(ord(b"e"))

	return buf
