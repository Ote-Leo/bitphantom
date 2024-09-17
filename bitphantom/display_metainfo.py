import argparse as ap
import sys
from collections.abc import Sequence
from typing import NoReturn, TextIO

from . import __version__
from .meta_info import loads_metainfo

__description__ = """

	A utility script for displaying a metainfo (.torrent) file information.
	Including trackers, file content, info hash, etc.

"""


def err(*msg: str, file: TextIO = sys.stderr, exit_code: int = 1) -> NoReturn:
	print("\n".join(*msg), file=file)
	exit(exit_code)


def init_parser() -> ap.ArgumentParser:
	parser = ap.ArgumentParser(description=__description__)
	parser.add_argument(
		"-v",
		"--version",
		help="script version",
		action="store_true",
	)
	parser.add_argument(
		"-i",
		"--infile",
		help="path to the metainfo file (defaults to stdin)",
		type=ap.FileType("rb"),
		nargs="?",
		default=sys.stdin,
	)
	parser.add_argument(
		"-o",
		"--outfile",
		help="path to the output file (defaults to stdout)",
		type=ap.FileType("w"),
		nargs="?",
		default=sys.stdout,
	)
	return parser


def display_metainfo(ns: ap.Namespace) -> int:
	source = ns.infile.read()
	try:
		metainfo = loads_metainfo(source)
	except ValueError as e:
		err("invalid bencode", e.__str__())
	print(metainfo, file=ns.outfile)
	return 0


def main(args: Sequence[str] | None = None) -> int:
	parser = init_parser()
	ns = parser.parse_args(args)

	if ns.version:
		print(__version__)
		return 0

	return display_metainfo(ns)


if __name__ == "__main__":
	exit(main(sys.argv[1:]))
