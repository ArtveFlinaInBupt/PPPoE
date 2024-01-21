from .projection import *

import unittest


class ProjectionTest(unittest.TestCase):
    def test_point3d_from_rad(self):
        p = Point3D.from_rad(0, 0)
        self.assertEqual(0, p.longitude)
        self.assertEqual(0, p.latitude)

        p = Point3D.from_rad(pi, pi / 2)
        self.assertEqual(pi, p.longitude)
        self.assertEqual(pi / 2, p.latitude)

        p = Point3D.from_rad(-pi, -pi / 2)
        self.assertEqual(-pi, p.longitude)
        self.assertEqual(-pi / 2, p.latitude)

    def test_point3d_from_deg(self):
        p = Point3D.from_deg(0, 0)
        self.assertEqual(0, p.longitude)
        self.assertEqual(0, p.latitude)

        p = Point3D.from_deg(180, 90)
        self.assertEqual(pi, p.longitude)
        self.assertEqual(pi / 2, p.latitude)

        p = Point3D.from_deg(-180, -90)
        self.assertEqual(-pi, p.longitude)
        self.assertEqual(-pi / 2, p.latitude)

        p = Point3D.from_deg(90, 45)
        self.assertEqual(pi / 2, p.longitude)
        self.assertEqual(pi / 4, p.latitude)

    def test_point2d_from_portion(self):
        p = Point2D.from_portion(0, 0)
        self.assertEqual(VERTICAL / 2, p.x)
        self.assertEqual(HORIZONTAL / 2, p.y)

        p = Point2D.from_portion(1, 1)
        self.assertEqual(0, p.x)
        self.assertEqual(HORIZONTAL * .75, p.y)

        p = Point2D.from_portion(-1, -1)
        self.assertEqual(VERTICAL - 1, p.x)
        self.assertEqual(HORIZONTAL * .25, p.y)

    def test_projection(self):
        # should copy from stdout and paste to a drawing tool such as https://www.desmos.com/calculator.
        # then you can see a complete meridian.
        for i in range(-90, 90 + 1, 1):
            p = project_(Point3D.from_deg(30, i))
            # uncomment the following line to see the result.
            print(f'({p.x}, {p.y})')


if __name__ == '__main__':
    unittest.main()
