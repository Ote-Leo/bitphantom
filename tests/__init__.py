import unittest
import random
import string
import sys

from pyrent.bencode import Bencode

__test_self = unittest.TestCase()

assert_false = __test_self.assertFalse
assert_true = __test_self.assertTrue
assert_raises = __test_self.assertRaises
assert_warns = __test_self.assertWarns
assert_logs = __test_self.assertLogs
assert_no_logs = __test_self.assertNoLogs
assert_equal = __test_self.assertEqual
assert_not_equal = __test_self.assertNotEqual
assert_almost_equal = __test_self.assertAlmostEqual
assert_not_almost_equal = __test_self.assertNotAlmostEqual
assert_sequence_equal = __test_self.assertSequenceEqual
assert_list_equal = __test_self.assertListEqual
assert_tuple_equal = __test_self.assertTupleEqual
assert_set_equal = __test_self.assertSetEqual
assert_in = __test_self.assertIn
assert_not_in = __test_self.assertNotIn
assert_is = __test_self.assertIs
assert_is_not = __test_self.assertIsNot
assert_dict_equal = __test_self.assertDictEqual
assert_dict_contains_subset = __test_self.assertDictContainsSubset
assert_count_equal = __test_self.assertCountEqual
assert_multi_line_equal = __test_self.assertMultiLineEqual
assert_less = __test_self.assertLess
assert_less_equal = __test_self.assertLessEqual
assert_greater = __test_self.assertGreater
assert_greater_equal = __test_self.assertGreaterEqual
assert_is_none = __test_self.assertIsNone
assert_is_not_none = __test_self.assertIsNotNone
assert_is_instance = __test_self.assertIsInstance
assert_not_is_instance = __test_self.assertNotIsInstance
assert_raises_regex = __test_self.assertRaisesRegex
assert_warns_regex = __test_self.assertWarnsRegex
assert_regex = __test_self.assertRegex
assert_not_regex = __test_self.assertNotRegex


# NOTE: Be extra caucious the depth value 5 is more than enough
def generate_obj(min_size: int = 1, max_size: int = 5) -> Bencode:
	max_depth = random.randint(min_size, max_size)
	return generate_benval(max_depth)


def generate_benval(max_depth: int) -> Bencode:
	generator = random.choice([generate_integer, generate_bytestring, generate_list, generate_dictionary])
	return generator(max_depth)


def generate_list(max_depth: int, min_size: int = 5, max_size: int = 15) -> list[Bencode]:
	res = []
	if max_depth < 1:
		return res

	size = random.randint(min_size, max_size)
	for _ in range(size):
		res.append(generate_benval(max_depth - 1))
	return res


def generate_integer(_: int, min_size: int = -1_000, max_size: int = 1_000) -> int:
	return random.randint(min_size, max_size)


def generate_bytestring(_: int, min_size: int = 5, max_size: int = 30) -> bytes:
	size = random.randint(min_size, max_size)
	bs = random.randbytes(size)
	return bs


def generate_string(_: int, min_size: int = 5, max_size: int = 30) -> str:
	size = random.randint(min_size, max_size)
	buf = "".join(random.choices(string.printable, k=size))
	return buf


def generate_dictionary(max_depth: int, min_size: int = 5, max_size: int = 15) -> dict[str, Bencode]:
	res = {}
	if max_depth < 1:
		return res

	count = random.randint(min_size, max_size)
	for _ in range(count):
		key = generate_string(max_depth)
		val = generate_benval(max_depth - 1)
		res[key] = val
	return res


def find_tests(module_name: str, prefix: str = "test_") -> list[unittest.FunctionTestCase]:
	module = sys.modules[module_name]
	tests = []
	for symbol in dir(module):
		if symbol.startswith(prefix):
			function_symbol = getattr(module, symbol)
			tests.append(unittest.FunctionTestCase(function_symbol, description=function_symbol.__doc__))
	return tests


__all__ = [
	"assert_false",
	"assert_true",
	"assert_raises",
	"assert_warns",
	"assert_logs",
	"assert_no_logs",
	"assert_equal",
	"assert_not_equal",
	"assert_almost_equal",
	"assert_not_almost_equal",
	"assert_sequence_equal",
	"assert_list_equal",
	"assert_tuple_equal",
	"assert_set_equal",
	"assert_in",
	"assert_not_in",
	"assert_is",
	"assert_is_not",
	"assert_dict_equal",
	"assert_dict_contains_subset",
	"assert_count_equal",
	"assert_multi_line_equal",
	"assert_less",
	"assert_less_equal",
	"assert_greater",
	"assert_greater_equal",
	"assert_is_none",
	"assert_is_not_none",
	"assert_is_instance",
	"assert_not_is_instance",
	"assert_raises_regex",
	"assert_warns_regex",
	"assert_regex",
	"assert_not_regex",
	"generate_obj",
	"generate_benval",
	"generate_list",
	"generate_integer",
	"generate_bytestring",
	"generate_string",
	"generate_dictionary",
]
