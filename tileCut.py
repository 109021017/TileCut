# coding=utf-8
import cv2
import numpy as np
import copy

# 整块砖的大小
PIECE_SIZE = (800, 800)
# 显示边距
DISPLAY_PADDING = 10

# 需要的尺寸, 每块的id 和 大小
data = [
    [1, 800, 800],
    [2, 800, 800],
    [3, 800, 800],
    [4, 800, 660],
    [5, 800, 660],
    [6, 800, 660],
    [7, 660, 160],
    [8, 530, 160],
    [9, 800, 300],
    [10, 800, 300],
    [11, 800, 300],
    [12, 800, 800],
    [13, 800, 800],
    [14, 800, 800],
    [15, 800, 600],
    [16, 481, 600],
    [17, 481, 600],
    [18, 400, 315],
    [19, 400, 315],
    [20, 400, 315],
    [21, 400, 315],
    [22, 400, 315],
    [23, 400, 170],
    [24, 400, 170],
    [25, 400, 170],
    [26, 200, 170],
    [27, 140, 400],
    [28, 140, 400],
    [29, 140, 400],
    [30, 140, 400],
    [31, 140, 400],
    [32, 90, 400],
    [33, 90, 400],
    [34, 90, 400],
    [35, 90, 400],
    [36, 90, 400],
    [37, 455, 400],
    [38, 455, 400],
    [39, 455, 400],
    [40, 455, 400],
    [41, 455, 400],
    [42, 105, 400],
    [43, 105, 400],
    [44, 105, 400],
    [45, 105, 400],
    [46, 105, 400],
    [47, 105, 400],
    [48, 800, 400],
    [49, 800, 400],
    [50, 800, 400],
    [51, 800, 400],
    [52, 800, 400],
    [53, 800, 400],
    [54, 360, 400],
    [55, 360, 400],
    [56, 360, 400],
    [57, 360, 400],
    [58, 360, 400],
    [59, 360, 400],
    [60, 335, 400],
    [61, 335, 400],
    [62, 335, 400],
    [63, 335, 400],
    [64, 335, 400],
    [65, 335, 400],
    [66, 280, 400],
    [67, 280, 400],
    [68, 280, 400],
    [69, 280, 400],
    [70, 280, 400],
    [71, 280, 400],
    [72, 160, 400],
    [73, 160, 400],
    [74, 160, 400],
    [75, 160, 400],
    [76, 160, 400],
    [77, 160, 400],
    [78, 500, 300],
    [79, 500, 300],
    [80, 800, 300],
    [81, 330, 400],
    [82, 330, 400],
    [83, 330, 400],
    [84, 330, 400],
    [85, 330, 400],
    [86, 330, 400],
    [87, 800, 400],
    [88, 800, 400],
    [89, 800, 400],
    [90, 800, 400],
    [91, 800, 400],
    [92, 800, 400],
    [93, 530, 400],
    [94, 530, 400],
    [95, 530, 400],
    [96, 530, 400],
    [97, 530, 400],
    [98, 530, 400],
    [99, 200, 400],
    [100, 200, 400],
    [101, 200, 400],
    [102, 200, 400],
    [103, 200, 400],
    [104, 200, 400],
    [105, 375, 400],
    [106, 375, 400],
    [107, 375, 400],
    [108, 375, 400],
    [109, 375, 400],
    [110, 265, 400],
    [111, 265, 400],
    [112, 265, 400],
    [113, 265, 400],
    [114, 265, 400],
    [115, 345, 400],
    [116, 345, 400],
    [117, 345, 400],
    [118, 345, 400],
    [119, 345, 400],
    [120, 100, 375],
    [121, 100, 265],
    [122, 100, 345]
]


class Slice:
    def __init__(self, idNum, width, height):
        self.idNum = idNum
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.rotation = 0
        self.used = False

    def __cmp__(self, other):
        return other.area() - self.area()

    def __str__(self):
        return str(self.idNum) + ", " + str(self.width) + ", " + str(self.height)

    def __repr__(self):
        return str(self.idNum) + ", " + str(self.width) + ", " + str(self.height)

    def area(self):
        return self.width * self.height

    def rotate(self):
        temp = self.width
        self.width = self.height
        self.height = temp
        self.rotation = 1 - self.rotation


class PieceCut:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.slice = None
        self.left = None
        self.right = None
        self.x = 0
        self.y = 0
        self.cutDirection = -1

    def area_used(self):
        area = 0
        if self.slice is not None:
            area += self.slice.area()
        if self.left is not None:
            area += self.left.area_used()
        if self.right is not None:
            area += self.right.area_used()
        return area

    def can_cut(self, slice):
        return (not slice.used) and self.width >= slice.width and self.height >= slice.height

    def cut(self, slice, flag, r):
        if r == 1:
            slice.rotate()
        if self.height == slice.height and self.width == slice.width:
            self.slice = slice
            slice.used = True
        if flag == 0 and self.height > slice.height and self.width >= slice.width:
            self.cutDirection = flag
            self.slice = slice
            slice.used = True
            if self.height > slice.height:
                self.left = PieceCut(self.width, self.height - slice.height)
                self.left.x = 0
                self.left.y = slice.height
            if self.width > slice.width:
                self.right = PieceCut(self.width - slice.width, slice.height)
                self.right.x = slice.width
                self.right.y = 0
        elif self.width > slice.width and self.height >= slice.height:
            self.cutDirection = flag
            self.slice = slice
            slice.used = True
            if self.width > slice.width:
                self.right = PieceCut(self.width - slice.width, self.height)
                self.right.x = slice.width
                self.right.y = 0
            if self.height > slice.height:
                self.left = PieceCut(slice.width, self.height - slice.height)
                self.left.x = 0
                self.left.y = slice.height


slices = []
for d in data:
    s = Slice(d[0], d[1], d[2])
    slices.append(s)

slices.sort()

pieces = []
cutNum = 0


def cut(p, list, depth):
    maxUse = 0
    maxPiece = None
    maxList = None
    s = None
    canFit = False
    for i in range(0, len(list)):
        s = list[i]
        if p.can_cut(s):
            canFit = True
            break
    if canFit:
        if depth != 0:
            pass
        for f in range(0, 2):
            for r in range(0, 2):
                if r == 1 and (s.width == s.height or p.width == p.height):
                    continue
                if n == 14:
                    pass
                listCopy = copy.deepcopy(list)
                sCopy = listCopy[i]
                pCopy = copy.copy(p)
                pCopy.cut(sCopy, f, r)
                if pCopy.left is not None:
                    pCopy.left, leftList = cut(pCopy.left, listCopy, depth + 1)
                    if leftList is not None:
                        listCopy = leftList
                if pCopy.right is not None:
                    pCopy.right, rightList = cut(pCopy.right, listCopy, depth + 1)
                    if rightList is not None:
                        listCopy = rightList

                used = pCopy.area_used()
                if used > maxUse:
                    maxUse = used
                    maxPiece = pCopy
                    maxList = listCopy
    return maxPiece, maxList


def markCut(list, p):
    s = p.slice
    if s is None:
        return
    for sl in list:
        if s.idNum == sl.idNum:
            global cutNum
            cutNum += 1
    if p.left is not None:
        markCut(list, p.left)
    if p.right is not None:
        markCut(list, p.right)


def drawPiece(img, p, offset):
    s = p.slice
    if s is None:
        # cv2.rectangle()
        return
    cv2.putText(img, str(s.idNum), (offset[0] + s.width/2, offset[1] + s.height/2), cv2.FONT_HERSHEY_SIMPLEX,  1, (255, 0, 0), 2)
    if p.cutDirection == 0:
        cv2.line(img, (offset[0], offset[1] + s.height), (offset[0] + p.width, offset[1] + s.height), (255, 0, 0), 1)
        cv2.line(img, (offset[0] + s.width, offset[1]), (offset[0] + s.width, offset[1]+s.height), (255, 0, 0), 1)
    elif p.cutDirection == 1:
        cv2.line(img, (offset[0], offset[1] + s.height), (offset[0] + s.width, offset[1] + s.height), (255, 0, 0), 1)
        cv2.line(img, (offset[0] + s.width, offset[1]), (offset[0] + s.width, offset[1]+p.height), (255, 0, 0), 1)
    if p.left is not None:
        drawPiece(img, p.left, (offset[0] + p.left.x, offset[1] + p.left.y))
    if p.right is not None:
        drawPiece(img, p.right, (offset[0] + p.right.x, offset[1] + p.right.y))


n = 1
img = np.zeros((PIECE_SIZE[0] + 2*DISPLAY_PADDING, PIECE_SIZE[1] + 2*DISPLAY_PADDING, 3), dtype=np.uint8)
while cutNum != len(slices):
    piece = PieceCut(PIECE_SIZE[0], PIECE_SIZE[1])
    img[:, :, :] = 255
    cv2.rectangle(img, (DISPLAY_PADDING, DISPLAY_PADDING), (PIECE_SIZE[0] + DISPLAY_PADDING, PIECE_SIZE[1] + DISPLAY_PADDING), (0, 0, 0), thickness=1)
    piece, slices = cut(piece, slices, 0)
    markCut(slices, piece)
    drawPiece(img, piece, (10, 10))
    cv2.imwrite("cuts/"+str(n)+".jpg", img)
    n += 1
