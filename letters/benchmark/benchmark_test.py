#!python3
# -*- coding: UTF-8 -*-
                







ori = [[[[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]],
        [[69, 127]]
        ],
        [
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]],
        [[62, 127]]
        ],
        [
        [[50, 127]],
        [[50, 127]],
        [[50, 127]],
        [[50, 127]],
        [[50, 127]],
        [[50, 127]],
        [[50, 127]],
        [[50, 127]],
        [[50, 127]],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        []]]

out = [ [[1, 74, 127], [9, 62, 127]],
        [[1, 74, 127], [9, 62, 127]],
        [[1, 74, 127], [9, 62, 127]],
        [[1, 74, 127], [9, 62, 127]],
        [[1, 74, 127], [9, 62, 127]],
        [[1, 74, 127], [9, 2, 127]],
        [[1, 74, 127], [3, 9, 127]],
        [[1, 74, 127], [3, 9, 127]],
        [[1, 74, 127], [3, 9, 127]],
        [[1, 74, 127], [3, 9, 127]],
        [[1, 74, 127], [3, 9, 127]],
        [[1, 74, 127], [3, 9, 127]],
        [[1, 74, 127], [3, 9, 127]],
        [[1, 74, 127], [3, 9, 127], [8, 30, 127]],
        [[1, 74, 127], [3, 9, 127]],
        [[1, 74, 127]],
        [[1, 74, 127], [3, 9, 127]],
        [[1, 74, 127], [9, 62, 127]]
        ]


"""

ori [[1, 69, 127], [9, 62, 127]]
out [[1, 74, 127], [3, 9, 127], [8, 30, 127]]

ori [[1, 69, 127], [9, 62, 127]]
out [[1, 74, 127], [3, 9, 127]]

ori [[1, 69, 127], [9, 62, 127]]
out [[1, 74, 127]]

"""

font_table = [1, 9, 3]

def flattenNestedList(nestedList):
    """Converts a nested list to a flat list."""
    
    flatList = []

    for elem_0 in nestedList:
        for elem_1 in elem_0:
            if isinstance(elem_1, list):
                if len(elem_1) > 0:
                    if len(elem_1[0]) == 2:
                        flatList.append(elem_1)

    return flatList
    
# Nombre de notes total en entrée
flat_ori = flattenNestedList(ori)
notes_nbr = len(flat_ori)

# Score des notes justes
score_good = 0
for k in range(18):
    
    targets = []
    for i in range(3):
        try:
            targets.append([font_table[i], ori[i][k][0][0], ori[i][k][0][1]])
        except:
            pass
            
    print("target", targets)
    print("out   ", out[k])
    print()

    for target in targets:
        if target in out[k]:
            score_good += 1

print("Nombre total de notes =", notes_nbr)
print("Nombre de notes ok    =", score_good)

note_sur_1 = (score_good / notes_nbr)
print(round(note_sur_1, 3))
