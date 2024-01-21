# -*- coding: utf-8 -*-

"""
Projection module.

Using Mollweide projection to project the world map.
"""
import logging
from dataclasses import dataclass
from math import pi, sin, cos, asin, sqrt

import numpy as np

CONSTANT = 10800
VERTICAL = CONSTANT * 2
HORIZONTAL = CONSTANT * 4


@dataclass
class Point2D:
    """
    Point in 2D space.
    """
    x: int  # range: [0, 10800 * 2)
    y: int  # range: [0, 10800 * 4)

    def __hash__(self):
        return self.x * HORIZONTAL + self.y

    @classmethod
    def from_portion(cls, x: float, y: float):
        """
        Create a Point2D object from portion.

        :param x: x portion, range: [-2, 2].
        :param y: y portion, range: [-1, 1].
        :return: Point2D object.
        """
        logging.debug(f'Point2D from portion x: {x}, y: {y}.')
        if x < -2 or x > 2:
            raise ValueError('x must be in [-2, 2]')
        if y < -1 or y > 1:
            raise ValueError('y must be in [-1, 1]')

        # y: [-1, 1] -> [0, 2] -> [0, 10800 * 2)
        # x: [-2, 2] -> [0, 4] -> [0, 10800 * 4)
        x, y = y, x
        x = int((-x + 1) * CONSTANT)
        y = int((y + 2) * CONSTANT)
        if x == VERTICAL:
            x -= 1
        if y == HORIZONTAL:
            y -= 1
        return cls(x, y)

    def __sub__(self, other):
        return Point2D(self.x - other.x, self.y - other.y)


@dataclass
class Point3D:
    """
    Point in 3D space. Latitude and longitude are in radians.
    """
    longitude: float  # range: [-pi, pi]
    latitude: float  # range: [-pi / 2, pi / 2]

    def __str__(self):
        return f'({np.rad2deg(self.longitude):.2f}, '\
               f'{np.rad2deg(self.latitude):.2f})'

    @classmethod
    def from_rad(cls, longitude: float, latitude: float):
        """
        Create a Point3D object from radians.

        :param longitude: Longitude in radians.
        :param latitude: Latitude in radians.
        :return: Point3D object.
        """
        logging.debug(
            f'Point3D from rad longitude: {longitude}, latitude: {latitude}.'
        )
        if longitude < -pi or longitude > pi:
            raise ValueError('longitude must be in [-pi, pi]')
        if latitude < -pi / 2 or latitude > pi / 2:
            raise ValueError('latitude must be in [-pi / 2, pi / 2]')

        return cls(longitude, latitude)

    @classmethod
    def from_deg(cls, longitude: float, latitude: float):
        """
        Create a Point3D object from degrees.

        :param longitude: Longitude in degrees.
        :param latitude: Latitude in degrees.
        :return: Point3D object.
        """
        logging.debug(
            f'Point3D from deg longitude: {longitude}, latitude: {latitude}.'
        )
        # if longitude < -180 or longitude > 180:
        #     raise ValueError('longitude must be in [-180, 180]')
        # if latitude < -90 or latitude > 90:
        #     raise ValueError('latitude must be in [-90, 90]')
        return cls.from_rad(np.deg2rad(longitude), np.deg2rad(latitude))


def project_(point: Point3D) -> Point2D:
    """
    Project a point on the world map.

    :param point: Point3D object.
    :return: Point2D object.
    """

    def get_theta_binary(phi: float) -> float:
        """
        Get theta, where 2theta + sin(2theta) = pi * sin(phi).
        :param phi:
        :return: desired theta
        """
        rhs = pi * sin(phi)  # range: [-pi, pi], strictly increasing

        # then 2theta is in range [-pi, pi]
        lb = -pi
        rb = pi
        while rb - lb > 1e-8:
            mid = (lb + rb) / 2
            if mid + sin(mid) < rhs:
                lb = mid
            else:
                rb = mid

        # now 2theta approx (lb + rb) / 2
        return (lb + rb) / 4

    def get_theta_newton(phi: float) -> float:
        """
        Get theta, where 2theta + sin(2theta) = pi * sin(phi).
        :param phi:
        :return: desired theta
        """
        theta_ = phi
        for _ in range(10):
            tmp = 2 * theta_
            theta_ -= ((tmp + sin(tmp) - pi * sin(phi)) / (2 + 2 * cos(tmp)))
        return theta_

    if abs(point.latitude) == pi / 2:
        return Point2D.from_portion(0, point.latitude / (pi / 2))

    # 2theta + sin(2theta) = pi * sin(latitude)
    theta = get_theta_newton(point.latitude)
    x = 2 / pi * point.longitude * cos(theta)
    y = sin(theta)
    return Point2D.from_portion(x, y)


def project(point: Point3D) -> Point2D:
    # map [-pi, pi] * [-pi / 2, pi / 2] to [-2, 2] * [-1, 1] linearly
    x = point.longitude / pi * 2
    y = point.latitude / pi * 2
    return Point2D.from_portion(x, y)


def inv_project(point: Point2D) -> Point3D:
    """
    Un-project a point on the world map.

    :param point: Point2D object.
    :return: Point3D object.
    """
    x = point.y / CONSTANT - 2
    y = point.x / CONSTANT - 1

    theta = asin(y)
    lon = pi * x / (2 * cos(theta))
    lat = asin((2 * theta + sin(2 * theta)) / pi)
    return Point3D.from_rad(lon, lat)
