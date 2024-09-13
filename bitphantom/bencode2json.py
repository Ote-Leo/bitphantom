"""A Bencode to JavaScript Object Notation (json) translator.

Useful for debugging purposes.
"""

# TODO: add a json to bencode functionality

import sys
import argparse as ap
from collections.abc import Sequence
from typing import NoReturn, TextIO
import json

from . import __version__
from .bencode import decode, Bencode


def err(*msg: str, file: TextIO = sys.stderr, exit_code: int = 1) -> NoReturn:
	print("\n".join(*msg), file=file)
	exit(exit_code)


def show_version() -> int:
	print(__version__)
	return 0


def handle_bytes(benval: Bencode) -> Bencode:
	if isinstance(benval, bytes):
		return benval.decode(encoding="utf-8", errors="backslashreplace")
	elif isinstance(benval, list):
		for i, e in enumerate(benval):
			benval[i] = handle_bytes(e)
		return benval
	elif isinstance(benval, dict):
		for k, v in benval.items():
			benval[k] = handle_bytes(v)
		return benval
	return benval


def init_parser() -> ap.ArgumentParser:
	parser = ap.ArgumentParser(description=__doc__)

	parser.add_argument(
		"-i",
		"--infile",
		help="path to the bencode file (defaults to stdin)",
		type=ap.FileType("rb"),
		nargs="?",
		default=sys.stdin,
	)
	parser.add_argument(
		"-o",
		"--outfile",
		help="path to the json file (defaults to stdout)",
		type=ap.FileType("w"),
		nargs="?",
		default=sys.stdout,
	)
	parser.add_argument(
		"-v",
		"--version",
		help="script version",
		action="store_true",
	)
	parser.add_argument(
		"--indent",
		help="format json with indentation",
		type=int,
	)
	parser.add_argument(
		"--sort-keys",
		help="sort json object keys",
		action="store_true",
	)
	parser.add_argument(
		"--no-ensure-ascii",
		help="output utf-8 encoded json",
		action="store_false",
		default=True,
	)

	return parser


def convert_bencode(ns: ap.Namespace) -> int:
	raw_bencode = ns.infile.read()
	try:
		benval, _ = decode(raw_bencode)
	except ValueError as e:
		err("invalid bencode", e.__str__())
	benval_stringfy = handle_bytes(benval)
	json.dump(
		benval_stringfy,
		ns.outfile,
		ensure_ascii=ns.no_ensure_ascii,
		indent=ns.indent,
		sort_keys=ns.sort_keys,
	)

	return 0


def main(args: Sequence[str] | None = None) -> int:
	parser = init_parser()
	ns = parser.parse_args(args)

	if ns.version:
		return show_version()

	return convert_bencode(ns)


if __name__ == "__main__":
	exit(main(sys.argv[1:]))
