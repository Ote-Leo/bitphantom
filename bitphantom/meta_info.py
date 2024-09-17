import base64
import hashlib
import pathlib
import urllib.parse
from dataclasses import dataclass
from typing import Any, Iterator, NamedTuple, TypeAlias, Union

from . import bencode

CHUNK_SIZE: int = 20


TrackerTier: TypeAlias = list[list[urllib.parse.ParseResultBytes]]
PieceLength: TypeAlias = int
Pieces: TypeAlias = bytes
InfoHash: TypeAlias = bytes


class Content(NamedTuple):
	path: pathlib.Path
	size: int


@dataclass
class MetaInfo:
	trackers: TrackerTier
	name: str | None
	content: list[Content] | int
	piece_length: int
	pieces: Pieces
	info_hash: InfoHash

	def __str__(self) -> str:
		trackers = []
		for tier in self.trackers:
			backups = [url.geturl().decode() for url in tier]
			tier_line = "  ".join(backups)
			trackers.append("\t" + tier_line)

		name_line = self.name or "."
		if isinstance(self.content, int):
			content = "\t%s (%d)" % (name_line, self.content)
		else:
			content = ("\t%s/\n" % name_line) + "\n".join(preview_files(self.content, "\t"))

		tracker_section = "trackers:\n" + "\n".join(trackers)
		content_section = "content:\n" + content
		piece_length = "piece length: %d" % self.piece_length
		info_hash = "info hash: %s" % base64.b64encode(self.info_hash).decode()

		return "\n".join((tracker_section, content_section, piece_length, info_hash))


FileTree = dict[str, Union[int, "FileTree"]]


def file_tree(files: list[Content]) -> FileTree:
	ft: FileTree = {}

	for file in files:
		file_path = file.path
		path_parts = file_path.parts
		if len(path_parts) == 1:
			f = path_parts[0]
			ft[f] = file.size
			continue

		file_parents, path_file = path_parts[:-1], path_parts[-1]
		current_parent = ft
		for parent in file_parents:
			in_parent = current_parent.get(parent)
			if isinstance(in_parent, dict):
				current_parent = in_parent
				continue

			p = {}
			if in_parent is None:
				current_parent[parent] = p
			else:  # a file and a directory share the same name
				parent_dir = parent + "/"
				current_parent[parent_dir] = p
			current_parent = p
		else:
			current_parent[path_file] = file.size

	return ft


def preview_files(files: list[Content], prefix: str = "") -> list[str]:
	tree = file_tree(files)
	return preview_tree(tree, prefix)


def preview_tree_entry(key: str, val: int | FileTree, key_prefix: str, prefix: str, lines: list[str]):
	if isinstance(val, int):
		lines.append(f"{key_prefix}{key} ({val})")
		return

	postfix = ""
	if not key.endswith("/"):
		postfix = "/"

	lines.append(f"{key_prefix}{key}{postfix}")
	lines += preview_tree(val, prefix)


def preview_tree(tree: FileTree, prefix: str = "") -> list[str]:
	lines = []
	keys = sorted(tree.keys())
	ks, k_last = keys[:-1], keys[-1]
	for k in ks:
		v = tree[k]
		preview_tree_entry(k, v, "├─ ", "│  ", lines)
	else:
		v = tree[k_last]
		preview_tree_entry(k_last, v, "└─ ", "   ", lines)

	for i in range(len(lines)):
		current_line = lines[i]
		lines[i] = prefix + current_line

	return lines


def get_piece(pieces: bytes, idx: int, chunk_size: int = CHUNK_SIZE) -> bytes | None:
	i = chunk_size * idx
	if idx == -1:
		return pieces[i:] or None
	j = i + chunk_size
	return pieces[i:j] or None


def iterate_pieces(pieces: bytes, chunk_size: int = CHUNK_SIZE, reverse: bool = False) -> Iterator[bytes]:
	i, j = (-1, -1) if reverse else (0, 1)
	while True:
		chunk = get_piece(pieces, i, chunk_size)
		if chunk is None:
			break
		i += j
		yield chunk


def process_trackers(raw_trackers: Any) -> TrackerTier:
	if not isinstance(raw_trackers, list):
		raise ValueError("invalid tracker type")

	for tier in raw_trackers:
		if not isinstance(tier, list):
			raise ValueError("invalid tracker tier type")
		for i in range(len(tier)):
			tracker = tier[i]
			if not isinstance(tracker, bytes):
				raise ValueError("invalid tracker type")
			tier[i] = urllib.parse.urlparse(tracker)

	return raw_trackers


def process_files(raw_files: Any) -> list[Content]:
	content: list[Content] = []

	if not isinstance(raw_files, list):
		raise ValueError("files entry is not a list")

	for i, file_dict in enumerate(raw_files):
		if not isinstance(file_dict, dict):
			raise ValueError("file %d at files entry is not a dictionary" % i)

		length = file_dict.get("length")
		if not isinstance(length, int) or length <= 0:
			raise ValueError("length of file %d at files entry is not a natrual number" % i)

		paths = file_dict.get("path")
		if not isinstance(paths, list):
			raise ValueError("path of file %d at files entry is not of type list" % i)

		for j, path in enumerate(paths):
			if not isinstance(path, bytes):
				raise ValueError("path piece %d of file %d at files entry is not of type bytes" % (j, i))
		path_acc = b"/".join(paths)

		try:
			path = path_acc.decode()
		except UnicodeDecodeError as err:
			raise ValueError("path of file %d at files is not utf8 encoded" % i) from err

		content.append(Content(pathlib.Path(path), length))

	return content


def process_info(info: bencode.BenDictionary) -> tuple[str | None, list[Content] | int, PieceLength, Pieces, InfoHash]:
	name = info.get("name")
	if name is not None:
		if not isinstance(name, bytes):
			raise ValueError("name entry is not of type bytes")
		try:
			name = name.decode()
		except UnicodeDecodeError as err:
			raise ValueError("name entry is not utf8 encoded") from err

	length = info.get("length")
	raw_files = info.get("files")

	if length and raw_files:
		raise ValueError("length and files entries are present")

	if length is None:
		content = process_files(raw_files)
	else:
		if not isinstance(length, int) or length <= 0:
			raise ValueError("length entry is not a natural number")
		content = length

	piece_length = info.get("piece length")
	if piece_length is None or not isinstance(piece_length, int) or piece_length <= 0:
		raise ValueError("piece length entry is not a natural number")

	pieces = info.get("pieces")
	if not isinstance(pieces, bytes):
		raise ValueError("pieces entry is not of type bytes")
	if len(pieces) % CHUNK_SIZE != 0:
		raise ValueError("pieces entry length is not divisable by %d" % CHUNK_SIZE)

	info_bencode = bencode.encode(info)
	info_hash = hashlib.sha1(info_bencode).digest()

	return name, content, piece_length, pieces, info_hash


def load_metainfo(path: str | pathlib.Path) -> MetaInfo:
	with open(path, "rb") as file:
		raw_bencode = file.read()

	return loads_metainfo(raw_bencode)


def loads_metainfo(source: bytes) -> MetaInfo:
	if not (source and source[0] == ord(b"d")):
		raise ValueError("invalid torrent file")
	benval, _ = bencode.decode_dictionary(source[1:])

	raw_trackers = benval.get("announce-list")
	if raw_trackers is None:
		tracker = benval.get("announce")
		if tracker is None:
			raise ValueError("missing tarcker entries")
		raw_trackers = [[tracker]]
	trackers = process_trackers(raw_trackers)

	info = benval.get("info")
	if info is None or not isinstance(info, dict):
		raise ValueError("missing info entry")
	name, content, piece_length, pieces, info_hash = process_info(info)

	return MetaInfo(trackers, name, content, piece_length, pieces, info_hash)
