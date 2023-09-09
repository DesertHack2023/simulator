import random

L1 = [1, 2, 5, 3, 6, 7, -2, 6, 11, 5, 3, 9, 0]

x = len(L1)


def FindMin(ListLen, ListOfPoints):
    a = 0  # random.randint(0,ListLen)
    c = 100000
    while a >= 0 and a < ListLen:
        if c > ListOfPoints[a]:
            c = ListOfPoints[a]
            a += 1
        else:
            a += 1
            continue
    return c


print(FindMin(x, L1))
