import re

INPUT_FILENAME = "2023summer\kansuke\ids.txt"
IDCS = "⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻"
WRONG = "[\"AGHJKMOSTUVX\[\]αℓ①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑲]"

sequences_dict = {}
visited = set()
leaves = set()

with open(INPUT_FILENAME, "r", encoding="utf-8") as input_file:
    for line in input_file:
        if line[0] == "#":
            continue

        line = line.strip().split()
        codepoint, character, sequences = line[0], line[1], line[2:]
        
        cleaned_sequences = [re.sub(WRONG, "", sequence) for sequence in sequences]
            
        sequences_dict[character] = cleaned_sequences


def visit_char(char):
    if char in visited:
        return

    visited.add(char)
    if char not in sequences_dict:
        leaves.add(char)
        return

    seqs = sequences_dict[char]
    for seq in seqs:
        if len(seq) == 1:
            leaves.add(char)
            continue 

        for child in seq:
            if child not in IDCS:
                visit_char(child)
            


for character in sequences_dict:
    visit_char(character)

leaves = sorted(list(leaves))

print("".join(leaves), len(leaves))