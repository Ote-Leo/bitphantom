# TODO: unmarshaling
# TODO: add an initial scanning for basic syntax checking so that no allocations are wasted
# TODO: add logging
# TODO: use errors as values instead of raising them

from collections.abc import Callable
from typing import TypeAlias

from .bencode_types import Bencode

Offset: TypeAlias = int


EARLY_EOB: str = "buffer ended too early"


def decode(buf: bytes) -> tuple[Bencode, Offset]:
	if len(buf) < 2:  # smallest bencodes are ``0:``, ``le``, ``de``
		raise ValueError(EARLY_EOB)

	decoder: Callable[[bytes], tuple[Bencode, Offset]]
	c = buf[0]

	if c == ord(b"i"):
		decoder = decode_integer
	elif c == ord(b"l"):
		decoder = decode_list
	elif c == ord(b"d"):
		decoder = decode_dictionary
	elif ord(b"0") <= c <= ord(b"9"):
		return decode_bytestring(buf)
	else:
		raise ValueError(f"invalid tokens at {chr(c)}")

	val, offset = decoder(buf[1:])
	return val, offset + 1


def decode_bytestring(buf: bytes) -> tuple[bytes, Offset]:
	idx = buf.find(b":")
	if idx < 1:
		raise ValueError("invalid string literal")

	size_str = buf[:idx]
	try:
		size = int(size_str)
	except ValueError:
		raise ValueError(f"failed to read {size_str} an integer")

	start = idx + 1
	end = start + size
	bytestring = buf[start:end]
	actual_size = len(bytestring)
	if actual_size != size:
		raise ValueError(f"bytestring of size {actual_size} does not match encoded size of {size}")

	return bytestring, end


def decode_integer(buf: bytes) -> tuple[int, Offset]:
	end = buf.find(b"e")
	if end < 1:
		raise ValueError("empty integer literal")

	integer_str = buf[:end]
	try:
		integer = int(integer_str)
	except ValueError:
		raise ValueError(f"failed to read {integer_str} an integer")

	return integer, end + 1


def decode_list(buf: bytes) -> tuple[list[Bencode], Offset]:
	res: list[Bencode] = []
	offset: int = 0

	while True:
		if len(buf) < 1:
			raise ValueError(EARLY_EOB + " while processing a list")
		elif buf[0] == ord(b"e"):
			return res, offset + 1
		else:
			val, j = decode(buf)
			buf = buf[j:]
			offset += j
			res.append(val)


def decode_dictionary(buf: bytes) -> tuple[dict[str, Bencode], Offset]:
	res: dict[str, Bencode] = {}
	offset: int = 0

	while True:
		if len(buf) < 1:
			raise ValueError(EARLY_EOB + " while processing a dictionary")
		elif buf[0] == ord(b"e"):
			return res, offset + 1
		else:
			key_bytes, j = decode_bytestring(buf)
			try:
				key = key_bytes.decode(encoding="utf-8", errors="strict")
			except UnicodeDecodeError:
				raise ValueError("non utf8 dictionary key")
			buf = buf[j:]
			offset += j

			val, j = decode(buf)
			buf = buf[j:]
			offset += j

			res[key] = val
