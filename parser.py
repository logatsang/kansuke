import re
from collections import Counter
from dataclasses import dataclass

IDS_FILE = "ids.txt"
TAG_FILE = "tags.txt"
IDCS = "⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻"
WRONG = "[\"AGHJKMOSTUVX\[\]αℓ①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑲]"

sequences_dict = {}
visited = set()
leaves = Counter()

@dataclass
class Character:
    char: str
    hor: int = 0
    ver: int = 0
    oth: int = 0

    def __add__(self, other):
        return Character(self.char,
                         self.hor+other.hor,
                         self.ver+other.ver,
                         self.oth+other.oth)

with open(IDS_FILE, "r", encoding="utf-8") as input_file:
    for line in input_file:
        if line[0] == "#":
            continue

        line = line.strip().split()
        codepoint, character, sequences = line[0], line[1], line[2:]

        cleaned_sequences = [re.sub(WRONG, "", sequence) for sequence in sequences]

        sequences_dict[character] = cleaned_sequences


def visit_char(char):
    if char in visited:
        if char in leaves:
            leaves[char] += 1
        return

    visited.add(char)
    if char not in sequences_dict:
        leaves[char] += 1
        return

    seqs = sequences_dict[char]
    for seq in seqs:
        if len(seq) == 1:
            leaves[char] += 1
            continue 

        for child in seq:
            if child not in IDCS:
                visit_char(child)


for character in sequences_dict:
    visit_char(character)


tagged = {}
visited.clear()
with open(TAG_FILE, "r", encoding="utf-8") as input_file:
    for line in input_file:
        char, code, *raw = line.split()
        hor, ver, oth = (int(x) for x in code.split("-"))
        tagged[char] = Character(char, hor, ver, oth)


for idc in IDCS:
    tagged[idc] = Character(idc)


def tag_char(char):
    if char in tagged or len(sequences_dict[char]) == 1:
        return
    
    for seq in sequences_dict[char]:
        if any(9312 >= ord(x) >= 9330 for x in seq):
            continue

        for child in seq:
            tag_char(child)
        
        if all(child in tagged for child in seq):
            tagged[char] = Character(char)
            for child in seq:
                tagged[char] += tagged[child]
            return  # TODO: allow multiple tags
        

for character in sequences_dict:
    tag_char(character)

print(tagged, len(tagged))

# print(leaves.most_common(), len(leaves))
