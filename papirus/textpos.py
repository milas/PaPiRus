import uuid

from PIL import Image, ImageDraw, ImageFont

from papirus import Papirus
from papirus.sprite import Sprite


WHITE = 1
BLACK = 0


class TextSprite(Sprite):
    """
    Holds details of text to be drawn on screen
    """
    def __init__(self, text, x, y, size, invert):
        super().__init__(x, y, size)
        self.text = text
        self.invert = invert


class PapirusTextPos(object):
    DEFAULT_FONT_PATH = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'

    def __init__(self, auto_update=True, rotation=0):
        # Set up the PaPirus and dictionary for text
        self.papirus = Papirus(rotation=rotation)
        self.text_cache = dict()
        self.image = Image.new('1', self.papirus.size, WHITE)
        self.auto_update = auto_update
        self.partial_updates = False

    def add_text(self, text, x=0, y=0, size=20, text_id=None, invert=False, font_path=None, max_lines=100):
        # Create a new Id if none is supplied
        if text_id is None:
            text_id = str(uuid.uuid4())

        # If the Id doesn't exist, add it  to the dictionary
        if text_id not in self.text_cache:
            self.text_cache[text_id] = TextSprite(text, x, y, size, invert)
            # add the text to the image
            self._add_text_to_image(text_id, font_path, max_lines)
            # Automatically show?
            if self.auto_update:
                self.write_all()

    def update_text(self, text_id, new_text, font_path=None, max_lines=100):
        # If the ID supplied is in the dictionary, update the text
        # Currently ONLY the text is update
        if text_id in self.text_cache:
            self.text_cache[text_id].text = new_text

            # Remove from the old text from the image (that doesn't use the actual text)
            self._remove_text_from_image(text_id)
            # Add the new text to the image
            self._add_text_to_image(text_id, font_path, max_lines)
            # Automatically show?
            if self.auto_update:
                self.write_all()

    def remove_text(self, text_id):
        # If the ID supplied is in the dictionary, remove it.
        if text_id in self.text_cache:
            self._remove_text_from_image(text_id)
            del self.text_cache[text_id]

            # Automatically show?
            if self.auto_update:
                self.write_all()

    def _remove_text_from_image(self, text_id):
        # prepare for drawing
        draw = ImageDraw.Draw(self.image)
        # Draw over the top of the text with a rectangle to cover it
        draw.rectangle([self.text_cache[text_id].x, self.text_cache[text_id].y,
                        self.text_cache[text_id].endx, self.text_cache[text_id].endy], fill="white")

    def _add_text_to_image(self, text_id, font_path=None, max_lines=100):
        # Break the text item back in to parts
        size = self.text_cache[text_id].size
        x = self.text_cache[text_id].x
        y = self.text_cache[text_id].y
        font_color = BLACK
        background_color = WHITE

        if self.text_cache[text_id].invert:
            font_color = WHITE
            background_color = BLACK

        # prepare for drawing
        draw = ImageDraw.Draw(self.image)

        # Grab the font to use, fixed at the moment
        font = ImageFont.truetype(font_path or self.DEFAULT_FONT_PATH, size)

        # Calculate the max number of char to fit on line
        # Taking in to account the X starting position
        line_width = self.papirus.width - x

        # Starting vars
        current_line = 0
        # Unicode by default
        text_lines = [u""]

        # Split the text by \n first
        to_process = self.text_cache[text_id].text.splitlines()

        # Go through the lines and add them
        for line in to_process:
            # Add in a line to add the words to
            text_lines.append(u"")
            current_line += 1
            # Compute each line
            for word in line.split():
                # Always add first word (even it is too long)
                if len(text_lines[current_line]) == 0:
                    text_lines[current_line] += word
                elif draw.textsize(text_lines[current_line] + " " + word, font=font)[0] < line_width:
                    text_lines[current_line] += " " + word
                else:
                    # No space left on line so move to next one
                    text_lines.append(u"")
                    if current_line < max_lines:
                        current_line += 1
                        text_lines[current_line] += word

        # Remove the first empty line
        if len(text_lines) > 1:
            del text_lines[0]

        # Go through all the lines as needed, drawing them on to the image

        # Reset the ending position of the text
        self.text_cache[text_id].endy = y
        self.text_cache[text_id].endx = x

        # Start at the beginning, calc all the end locations
        current_line = 0
        for l in text_lines:
            # Find out the size of the line to be drawn
            text_size = draw.textsize(l, font=font)
            # Adjust the x end point if needed
            if text_size[0] + x > self.text_cache[text_id].endx:
                self.text_cache[text_id].endx = text_size[0] + x
            # Add on the y end point
            self.text_cache[text_id].endy += size
            # If next line does not fit, quit
            current_line += 1
            if self.text_cache[text_id].endy > (self.papirus.height - size - 3):
                del text_lines[current_line:]
                break

        # Little adjustment to make sure the text gets covered
        self.text_cache[text_id].endy += 3

        # If the text is wanted inverted, put a rectangle down first
        if self.text_cache[text_id].invert:
            draw.rectangle([self.text_cache[text_id].x, self.text_cache[text_id].y,
                            self.text_cache[text_id].endx, self.text_cache[text_id].endy], fill=background_color)

        # Start at the beginning, add all the lines to the image
        current_line = 0
        for l in text_lines:
            # Draw the text to the image
            y_line = y + size * current_line
            draw.text((x, y_line), l, font=font, fill=font_color)
            current_line += 1

    def write_all(self, partial_update=False):
        # Push the image to the PaPiRus device, and update only what's needed
        # (unless asked to do a full update)
        self.papirus.display(self.image)
        if partial_update or self.partial_updates:
            self.papirus.partial_update()
        else:
            self.papirus.update()

    def clear(self):
        # clear the image, clear the text items, do a full update to the screen
        self.image = Image.new('1', self.papirus.size, WHITE)
        self.text_cache = dict()
        self.papirus.clear()
