import math as m


class RasterDrawing:
    def __init__(self):
        self.shapes = dict()
        self.shapeNames = list()

    def assignName(self):
        return f"shape{len(self.shapeNames)}"

    def addShape(self, shape, name=None):
        if name is None:
            name = self.assignName()
        self.shapes[name] = shape
        self.shapeNames.append(name)

    def removeShape(self, name):
        if name in self.shapes:
            del self.shapes[name]
            self.shapeNames.remove(name)

    def paint(self, canvas, **kargs):
        for name in self.shapeNames:
            shape = self.shapes[name]
            shape.paint(canvas, **kargs)

    def clear(self):
        self.shapes = dict()
        self.shapeNames = list()

    def save(self, fileName):
        with open(fileName, "w") as f:
            for name in self.shapeNames:
                shape = self.shapes[name]
                f.write(name + " = " + repr(shape) + "\n")

class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Empty canvas is a matrix with element being the "space" character
        self.data = [[' '] * width for i in range(height)]

    def set_pixel(self, row, col, char='*'):
        self.data[row][col] = char

    def get_pixel(self, row, col):
        return self.data[row][col]
    
    def clear_canvas(self):
        self.data = [[' '] * self.width for i in range(self.height)]
    
    def v_line(self, x, y, w, **kargs):
        for i in range(x,x+w):
            self.set_pixel(i,y, **kargs)

    def h_line(self, x, y, h, **kargs):
        for i in range(y,y+h):
            self.set_pixel(x,i, **kargs)
            
    def line(self, x1, y1, x2, y2, **kargs):
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.set_pixel(x1, y, **kargs)
        elif y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.set_pixel(x, y1, **kargs)
        else:
            slope = (y2 - y1) / (x2 - x1)
            for x in range(min(x1, x2), max(x1, x2) + 1):
                y = int(round(y1 + slope * (x - x1)))
                self.set_pixel(x, y, **kargs)
            
    def display(self):
        print("\n".join(["".join(row) for row in self.data]))


# shape
class shape:
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    def __repr__(self):
        raise NotImplementedError("Subclasses must implement __repr__()")

    def points(self):
        raise NotImplementedError
        
    def area(self):
        raise NotImplementedError

    def perimeter(self):
        raise NotImplementedError

    def isInside(self, x, y):
        raise NotImplementedError

    def overlaps(self, other):
        raise NotImplementedError

    def paint(self, canvas, **kargs):
        pts = self.points()
        for x, y in pts:
            x = int(round(x))
            y = int(round(y))
            if 0 <= x < canvas.height and 0 <= y < canvas.width:
                canvas.set_pixel(x, y, **kargs)

# Rect
class Rect(shape):
    def __init__(self, length, width, x=0, y=0):
        super().__init__(x, y)
        #self.__x = x
        #self.__y = y
        self._length = length
        self._width = width
        self._corner = (x, y)

    def __repr__(self):
        return f"Rect({repr(self._length)}, {repr(self._width)}, {repr(self._x)},{repr(self._y)})"


    def area(self):
        return (self._length * self._width)

    def perimeter(self):
        return (self._length * 2 + self._width * 2)

    def points(self, n=16):
        points = []
        p = self.perimeter()
        sides = [self._length, self._width, self._length, self._width]
        allLengths = [0]
        # we are walking around our perimeter and need to calc which side were on
        for s in sides:
            allLengths.append(allLengths[-1] + s)

        # now lets determine our dist and see if the points lies on our calced side
        # once this is done place point in list
        for i in range(n):
            dist = (i / n) * p
            if dist < allLengths[1]: # bottom
                x = self._x + dist
                y = self._y
            elif dist < allLengths[2]: # right
                x = self._x + self._length
                y = self._y + (dist - allLengths[1])
            elif dist < allLengths[3]: # top
                x = self._x + self._length - (dist - allLengths[2])
                y = self._y + self._width
            else: # left
                x = self._x
                y = self._y + self._width - (dist - allLengths[3])
            points.append((x, y))
        return points

    def isInside(self, x, y):
            return (self._x <= x <= self._x + self._length) and (self._y <= y <= self._y + self._width)

    def overlaps(self, other):
        if isinstance(other, Rect):
            return not (self._x + self._length < other._x or 
                        self._x > other._x + other._length or
                        self._y + self._width < other._y or
                        self._y > other._y + other._width)
        else:
            for (x, y) in self.points():
                if other.isInside(x, y):
                    return True
            for (x, y) in other.points():
                if self.isInside(x, y):
                    return True
            return False

    def paint(self, canvas, **kargs):
        pts = self.points()
        for x, y in pts:
            x = int(round(x))
            y = int(round(y))
            if 0 <= x < canvas.height and 0 <= y < canvas.width:
                canvas.set_pixel(x, y, **kargs)


# Circ
class Circ(shape):
    def __init__(self, radius, x=0, y=0):
        super().__init__(x, y)
        #self.__x = x
        #self.__y = y
        self._radius = radius
        self._center = (x, y)

    def __repr__(self):
        return f"Circ({repr(self._radius)}, {repr(self._x)}, {repr(self._y)})"

    def area(self):
        return (m.pi * (self._radius ** 2))

    def perimeter(self):
        return (2 * m.pi * self._radius)

    def points(self, n=16):
        points = []
        for i in range(n):
            theta = 2 * m.pi * i / n
            x = self._x + self._radius * m.cos(theta)
            y = self._y + self._radius * m.sin(theta)
            points.append((x,y))
        return points

    def isInside(self, x, y):
        dx = x - self._x
        dy = y - self._y
        distSquared = dx**2 + dy**2
        return distSquared <= self._radius**2 

    def overlaps(self, other):
        if isinstance(other, Circ):
            dx = self._x - other._x
            dy = self._y - other._y
            distSquared = dx**2 + dy**2
            radSum = self._radius + other._radius
            return distSquared <= radSum**2
        else:
            for (x, y) in self.points():
                if other.isInside(x, y):
                    return True
            for (x, y) in other.points():
                if self.isInside(x, y):
                    return True
            return False

    def paint(self, canvas, **kargs):
        pts = self.points()
        for x, y in pts:
            x = int(round(x))
            y = int(round(y))
            if 0 <= x < canvas.height and 0 <= y < canvas.width:
                canvas.set_pixel(x, y, **kargs)


# Triangle
class Triangle(shape):
    def __init__(self, side_1, side_2, side_3, x=0, y=0):
        super().__init__(x, y)
        self._side_1 = side_1
        self._side_2 = side_2
        self._side_3 = side_3
        self._corner = (x, y)
        self._A = (x, y)
        self._B = (x + side_1, y)
        self._C = (x + side_2/2, y + side_2)

    def __repr__(self):
        return f"Triangle({repr(self._side_1)}, {repr(self._side_2)}, {repr(self._side_3)},{repr(self._x)}, {repr(self._y)})"

    def area(self):
        s = (self._side_1 + self._side_2 + self._side_3) / 2
        return ((s * (s - self._side_1) * (s - self._side_2) * (s - self._side_3)) ** 0.5)
        
    def perimeter(self):
        return (self._side_1 + self._side_2 + self._side_3)

    def points(self, n=16):
        points = []
        A = (self._corner[0], self._corner[1])
        B = (self._corner[0], self._side_1, self._corner[1])
        C = (self._corner[0] + (self._side_2 / 2), self._corner[1] + (self._side_2))

        p = self.perimeter()
        sideLengths = [
            ((A, B), self._side_1),
            ((B, C), self._side_2),
            ((C, A), self._side_3)
        ]

        allLength = [0]
        for (_, length) in sideLengths:
            allLength.append(allLength[-1] + length)

        for i in range(n):
            dist = (i / n) * p
            if dist < allLength[1]:
                (p1, p2) = sideLengths[0][0]
                sideDist = (dist - allLength[0]) / sideLengths[0][1]
            elif dist < allLength[2]:
                (p1, p2) = sideLengths[1][0]
                sideDist = (dist - allLength[1]) / sideLengths[1][1]
            else:
                (p1, p2) = sideLengths[2][0]
                sideDist = (dist - allLength[2]) / sideLengths[2][1]

            x = p1[0] + (p2[0] - p1[0]) * sideDist
            y = p1[1] + (p2[1] - p1[1]) * sideDist
            points.append((x, y))
        return points

    def isInside(self, x, y):
        # area comparison
        def triArea(p1, p2, p3):
            return abs((p1[0]*(p2[1]-p3[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p1[1]-p2[1])) / 2)

        A = self._A
        B = self._B
        C = self._C
        fullArea = triArea(A, B, C)
        a1 = triArea((x, y), B, C)
        a2 = triArea(A, (x, y), C)
        a3 = triArea(A, B, (x, y))

        return abs(fullArea - (a1 + a2 + a3)) < 1e-6

    def overlaps(self, other):
        for (x, y) in self.points():
            if other.isInside(x, y):
                return True
        for (x, y) in other.points():
            if self.isInside(x, y):
                return True
        return False

    def paint(self, canvas, **kargs):
        pts = self.points()
        for x, y in pts:
            x = int(round(x))
            y = int(round(y))
            if 0 <= x < canvas.height and 0 <= y < canvas.width:
                canvas.set_pixel(x, y, **kargs)


def rasterLoad(fileName):
    drawing = RasterDrawing()
    with open(fileName, "r") as f:
        lines = f.readlines()
        for line in lines:
            exec(line)
            name = line.split('=')[0].strip()
            obj = eval(name)
            drawing.addShape(obj, name=name)
    return drawing








        


