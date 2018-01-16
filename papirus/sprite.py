# import abc


class Sprite(object):
    """
    Base class for object to be drawn on screen
    """
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.endx = 0
        self.endy = 0
