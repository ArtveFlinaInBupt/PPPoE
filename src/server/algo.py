import logging

from data_manip import DataManipulator
from projection import Point2D

from typing import List


class MinMax:
    def __init__(self, arg):
        self.min = arg
        self.max = arg

    def update(self, arg):
        self.min = min(self.min, arg)
        self.max = max(self.max, arg)

    def get(self):
        return self.min, self.max


class MinMaxDict:
    def __init__(self):
        self._dict = {}

    def update(self, key, value):
        if key not in self._dict:
            self._dict[key] = MinMax(value)
        else:
            self._dict[key].update(value)

    def get_dict(self):
        return self._dict

    def get(self, key):
        return self._dict[key].get()


def cross(lhs: Point2D, rhs: Point2D) -> float:
    """
    Calculate the cross product of two vectors.

    :param lhs: Vector lhs.
    :param rhs: Vector rhs.
    :return: Cross product of lhs and rhs.
    """
    return lhs.x * rhs.y - lhs.y * rhs.x


def calc_convex(p: List[Point2D]) -> List[Point2D]:
    """
    Calculate the convex hull of a list of points.

    :param p: List of points.
    :return: List of points consisted of the convex hull. In counter-clockwise
             order.
    """
    p.sort(key=lambda p: (p.x, p.y))
    used = [False] * len(p)

    stack = [0]
    # used[0] = True

    # 求下凸壳
    for i in range(1, len(p)):
        while len(stack) > 1 and cross(
                p[stack[-1]] - p[stack[-2]], p[i] - p[stack[-1]]
        ) <= 0:
            used[stack.pop()] = False
        stack.append(i)
        used[i] = True

    base = len(stack)
    # 求上凸壳
    for i in range(len(p) - 2, -1, -1):
        if used[i]:
            continue
        while len(stack) > base and cross(
                p[stack[-1]] - p[stack[-2]], p[i] - p[stack[-1]]
        ) <= 0:
            used[stack.pop()] = False
        stack.append(i)
        used[i] = True

    return [p[i] for i in stack]


def point_in_convex_linear(point: Point2D, convex: List[Point2D]) -> bool:
    """
    Check if a point is in a convex.

    :param point: Point to check.
    :param convex: Convex to check, in counter-clockwise order.
    :return: True if the point is in the convex, False otherwise.
    """
    for i in range(len(convex) - 1):
        if cross(convex[i] - point, convex[(i + 1) % len(convex)] - point) < 0:
            return False
    return True


def point_in_convex(point: Point2D, convex: List[Point2D]) -> bool:
    """
    Check if a point is in a convex.

    :param point: Point to check.
    :param convex: Convex to check, in counter-clockwise order.
    :return: True if the point is in the convex, False otherwise.
    """
    lb = 0
    rb = len(convex) - 1
    while rb - lb > 1:
        mid = (lb + rb) // 2
        if cross(convex[mid] - convex[0], point - convex[0]) >= 0:
            lb = mid
        else:
            rb = mid

    return cross(convex[lb] - point, convex[rb] - point) >= 0


class DataAccessor(DataManipulator):
    def __init__(self):
        super().__init__()
        self.load()

    def query_all_sum(self):
        return self._data_processed[21509, 43109]

    def query(self, row, starting_col, ending_col):
        if row >= 21600:
            return 0
        if ending_col >= 43200:
            ending_col = 43109

        ret = self._data_processed[row, ending_col] - (
            0
            if starting_col == 0 else
            self._data_processed[row, starting_col - 1]
        )
        return ret


def calc_whole_convex(convex, data_accessor):
    intersections = MinMaxDict()

    for i in range(0, len(convex) - 1):
        p1 = convex[i]
        p2 = convex[i + 1]
        x1 = min(p1.x, p2.x)
        y1 = min(p1.y, p2.y)
        x2 = max(p1.x, p2.x)
        y2 = max(p1.y, p2.y)
        if y1 == y2:
            for x in range(x1, x2 + 1):
                intersections.update(x, y1)
        elif x1 == x2:
            for y in range(y1, y2 + 1):
                intersections.update(x1, y)
        else:
            k = (y1 - y2) / (x1 - x2)
            b = y1 - k * x1
            for x in range(x1, x2 + 1):
                y = int(k * x + b)
                intersections.update(x, y)

    ans = 0
    for x in intersections.get_dict().keys():
        min_, max_ = intersections.get(x)
        ans += data_accessor.query(x, min_, max_)
    return ans
