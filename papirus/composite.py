import uuid

from PIL import Image
from PIL import ImageOps

from papirus import PapirusTextPos
from papirus.sprite import Sprite


WHITE = 1
BLACK = 0


class RasterSprite(Sprite):
    """
    A raster image (e.g. PNG, JPG, BMP) object to be drawn on screen
    """
    def __init__(self, file_path, x, y, size):
        super().__init__(x, y, size)
        self.path = file_path


class PapirusComposite(PapirusTextPos):
    def __init__(self, panel, auto_update=True):
        super(PapirusComposite, self).__init__(panel, auto_update)
        self.image_cache = dict()
        self.image = Image.new('1', self.panel.size, WHITE)

    def add_raster_sprite(self, file_path, x=0, y=0, size=(10, 10), sprite_id=None):
        # Create a new Id if none is supplied
        if sprite_id is None:
            sprite_id = str(uuid.uuid4())

        file_path = Image.open(file_path)
        file_path = ImageOps.grayscale(file_path)
        file_path = file_path.resize(size)
        file_path = file_path.convert("1", dither=Image.FLOYDSTEINBERG)

        # If the Id doesn't exist, add it  to the dictionary
        if sprite_id not in self.image_cache:
            self.image_cache[sprite_id] = RasterSprite(file_path, x, y, size)
            # add the img to the image
            self.draw_sprite_from_cache(sprite_id)
            # Automatically show?
            if self.auto_update:
                self.write_all()

    def update_sprite(self, sprite_id, image):
        # If the ID supplied is in the dictionary, update the img
        # Currently ONLY the img is update
        if sprite_id in self.image_cache:
            image = Image.open(image)
            image = ImageOps.grayscale(image)
            image = image.resize(self.image_cache[sprite_id].size)
            image = image.convert("1", dither=Image.FLOYDSTEINBERG)

            self.image_cache[sprite_id].image = image

            # Remove from the old img from the image (that doesn't use the actual img)
            self.erase_sprite_from_image(sprite_id)
            # Add the new img to the image
            self.draw_sprite_from_cache(sprite_id)
            # Automatically show?
            if self.auto_update:
                self.write_all()

    def remove_sprite(self, sprite_id):
        # If the ID supplied is in the dictionary, remove it.
        if sprite_id in self.image_cache:
            self.erase_sprite_from_image(sprite_id)
            del self.image_cache[sprite_id]

            # Automatically show?
            if self.auto_update:
                self.write_all()

    def erase_sprite_from_image(self, sprite_id):
        # prepare for drawing
        filler = Image.new('1', self.image_cache[sprite_id].size, WHITE)
        # Draw over the top of the img with a rectangle to cover it
        x = self.image_cache[sprite_id].x
        y = self.image_cache[sprite_id].y
        self.image.paste(filler, (x, y))

    def draw_sprite_from_cache(self, sprite_id):
        x = self.image_cache[sprite_id].x
        y = self.image_cache[sprite_id].y

        self.image.paste(self.image_cache[sprite_id].image, (x, y))
