import cv2
import numpy as np
import math

import pygame


def get_borders(image):
    img = cv2.imread(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
    threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    return contours_to_array(contours)

def contours_to_array(contours):
    # Converting to less nested array - faster execution
    cnt = contours
    cntOuter = cnt[1]
    cntInner = cnt[2]

    arrSize = math.floor(cntOuter.size / 2)
    cntOuter2 = np.zeros(shape=(arrSize, 2), dtype=int)

    arrSize = math.floor(cntInner.size / 2)
    cntInner2 = np.zeros(shape=(arrSize, 2), dtype=int)

    i = 0
    for coor in cntOuter:
        for pair in coor:
            cntOuter2[i] = pair
        i = i + 1

    j = 0
    for coor in cntInner:
        for pair in coor:
            cntInner2[j] = pair
        j = j + 1

    return cntOuter2, cntInner2

def get_pos():
    pos = pygame.mouse.get_pos()
    print(pos)
    return (pos)


