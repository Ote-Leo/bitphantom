import random

from pyrent.bencode import decode, encode
from tests import (
	assert_equal,
	find_tests,
	generate_bytestring,
	generate_dictionary,
	generate_integer,
	generate_list,
	generate_obj,
)

DID_NOT_CONSUME_ERROR: str = "did not consume the whole bencode"
MISMATCH_DECODE: str = "produced different object than the original"

MIN_DEPTH: int = 1
MAX_DEPTH: int = 3  # NOTE: beware of the exponential growth


def test_if_decoding_is_the_opposite_of_encoding_in_general():
	iterations = 100
	for _ in range(iterations):
		obj = generate_obj(MIN_DEPTH, MAX_DEPTH)
		bencode = encode(obj)
		benval, offset = decode(bencode)
		assert_equal(benval, obj, MISMATCH_DECODE)
		assert_equal(len(bencode[offset:]), 0, DID_NOT_CONSUME_ERROR)


def test_if_decoding_is_the_opposite_of_encoding_a_bytestrings():
	iterations = 100
	for _ in range(iterations):
		obj = generate_bytestring(MIN_DEPTH)
		bencode = encode(obj)
		benval, offset = decode(bencode)
		assert_equal(benval, obj, MISMATCH_DECODE)
		assert_equal(len(bencode[offset:]), 0, DID_NOT_CONSUME_ERROR)


def test_if_decoding_is_the_opposite_of_encoding_a_integers():
	iterations = 100
	for _ in range(iterations):
		obj = generate_integer(MIN_DEPTH)
		bencode = encode(obj)
		benval, offset = decode(bencode)
		assert_equal(benval, obj, MISMATCH_DECODE)
		assert_equal(len(bencode[offset:]), 0, DID_NOT_CONSUME_ERROR)


def test_if_decoding_is_the_opposite_of_encoding_a_list():
	iterations = 100
	for _ in range(iterations):
		depth = random.randint(MIN_DEPTH, MAX_DEPTH)
		obj = generate_list(depth)
		bencode = encode(obj)
		benval, offset = decode(bencode)
		assert_equal(benval, obj, MISMATCH_DECODE)
		assert_equal(len(bencode[offset:]), 0, DID_NOT_CONSUME_ERROR)


def test_if_decoding_is_the_opposite_of_encoding_a_dictionary():
	iterations = 100
	for _ in range(iterations):
		depth = random.randint(MIN_DEPTH, MAX_DEPTH)
		obj = generate_dictionary(depth)
		bencode = encode(obj)
		benval, offset = decode(bencode)
		assert_equal(benval, obj, MISMATCH_DECODE)
		assert_equal(len(bencode[offset:]), 0, DID_NOT_CONSUME_ERROR)


def load_tests(_loader, suite, _pattern):
	tests = find_tests(__name__)
	suite.addTests(tests)
	return suite
