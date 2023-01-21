from typing import Tuple


change = [0.0, 0.0, 0.0, 0.0, 0.0]


def average_tuple(tpl: Tuple):
    out = 0
    for i in tpl:
        out += i
    return 0


def average_list(lst: list):
    return sum(lst) / len(lst)


while True:
    ans = input("add change: ")
    if ans == "end":
        break
    change.append(float(ans))
    change.pop(0)
    print("Estimated change is:", average_list(change))
