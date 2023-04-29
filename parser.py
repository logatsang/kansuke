"""This module parses something."""     # TODO: proper docstring

import re
from collections import Counter
from dataclasses import dataclass

DEBUG = True

IDS_FILE = "ids.txt"
TAG_FILE = "tags.txt"
IDCS = "⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻"
WRONG = "[\"AGHJKMOSTUVX[]]"

visited = set()
leaves = Counter()


def is_unencoded(char: str) -> bool:
    """Return whether a character represents an unencoded component."""
    return 9312 <= ord(char) <= 9330


@dataclass
class Character:
    """Class to represent a tagged character."""
    char: str
    hor: int = 0
    ver: int = 0
    oth: int = 0

    def __add__(self, other: 'Character'):
        return Character(
            self.char,
            self.hor+other.hor,
            self.ver+other.ver,
            self.oth+other.oth
        )


def read_ids(filename: str) -> dict:
    """Read Ideographic Description Sequences from a specified file."""
    sequences_dict = {}
    with open(filename, "r", encoding="utf-8") as input_file:
        for line in input_file:
            if line[0] == "#":
                continue

            line = line.strip().split()
            _codepoint, character, sequences = line[0], line[1], line[2:]

            cleaned_sequences = [re.sub(WRONG, "", sequence) for sequence in sequences]
            sequences_dict[character] = cleaned_sequences

    return sequences_dict


def read_tags(filename: str) -> dict:
    """Read primitive tag data from a specified file."""
    tags = {}
    with open(filename, "r", encoding="utf-8") as input_file:
        for line in input_file:
            try:
                char, code, *_raw = line.split()
                hor, ver, oth = (int(x) for x in code.split("-"))
                tags[char] = Character(char, hor, ver, oth)
            except ValueError:
                continue

    return tags


def visit_char(ids_data: dict, char: str):
    """Find all primitives contained in a character."""
    if char in visited:
        if char in leaves:
            leaves[char] += 1
        return

    visited.add(char)
    if char not in ids_data:
        leaves[char] += 1
        return

    seqs = ids_data[char]
    debug_seqs = []

    for seq in seqs:
        if len(seq) == 1:
            leaves[char] += 1
            continue

        if DEBUG and any(is_unencoded(child) for child in seq):
            debug_seqs.append(seq)

        for child in seq:
            if child not in IDCS and not is_unencoded(child):
                visit_char(ids_data, child)

    if DEBUG and debug_seqs:
        seqs_out = "\t".join(debug_seqs)
        with open("missing", "a", encoding="utf-8") as debug_file:
            debug_file.write(f"U+{ord(char):X}\t{char}\t{seqs_out}\n")


def tag_char(char: str, tagged: dict, ids_data: dict):
    """Recursively tag a character and all of its components."""
    if char in visited:
        return

    visited.add(char)

    if char in tagged or len(ids_data[char]) == 1:
        return

    for seq in ids_data[char]:
        if any(is_unencoded(x) for x in seq):
            continue

        for child in seq:
            tag_char(child, tagged, ids_data)

        if all(child in tagged for child in seq):
            tagged[char] = Character(char)
            for child in seq:
                tagged[char] += tagged[child]
            return  # TODO: allow multiple tags


def main():
    """Main function"""
    # Read data
    ids_data = read_ids(IDS_FILE)
    tag_data = read_tags(TAG_FILE)

    # Find leaves
    visited.clear()
    for character in ids_data:
        visit_char(ids_data, character)

    # Generate tags
    for idc in IDCS:
        tag_data[idc] = Character(idc)

    visited.clear()
    for character in ids_data:
        tag_char(character, tag_data, ids_data)


if __name__ == "__main__":
    main()
