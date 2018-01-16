import os

from abc import abstractmethod, ABCMeta

from PIL import Image
from PIL import ImageOps


class DisplayError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Panel(object):
    WHITE = 1
    BLACK = 0

    def __init__(self, width, height, rotation=0, auto_update=False):
        if width < 1 or height < 1:
            raise DisplayError('invalid panel dimensions')

        self._width = width
        self._height = height

        # rotation must be set after width/height
        self._rotation = 0
        self.rotation = rotation

        self.auto_update = auto_update

    def display(self, image):
        # attempt grayscale conversion, ath then to single bit
        # better to do this before calling this if the image is to
        # be displayed several times
        if image.mode != "1":
            image = ImageOps.grayscale(image).convert("1", dither=Image.FLOYDSTEINBERG)

        if image.mode != "1":
            raise DisplayError('only single bit images are supported')

        if image.size != self.size:
            raise DisplayError('image size mismatch')

        if self.rotation != 0:
            image = image.transpose(self.rotation_angle(self._rotation))

        self._write(image)

        if self.auto_update:
            self.update()

    @abstractmethod
    def update(self):
        pass

    def partial_update(self):
        pass

    def fast_update(self):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def _write(self, image):
        pass

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return self._width, self._height

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, rot):
        if rot != 0 and rot != 90 and rot != 180 and rot != 270:
            raise DisplayError('rotation can only be 0, 90, 180 or 270')
        if abs(self._rotation - rot) in (90, 270):
            # swap the width and height
            self._width, self._height = self._height, self._width
        self._rotation = rot

    @staticmethod
    def rotation_angle(rotation):
        if rotation == 90:
            return Image.ROTATE_90
        elif rotation == 180:
            return Image.ROTATE_180
        elif rotation == 270:
            return Image.ROTATE_270

        raise ValueError()
