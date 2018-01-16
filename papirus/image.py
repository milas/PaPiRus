from __future__ import division

from PIL import Image

WHITE = 1


class PapirusImage(object):
    def __init__(self, panel):
        self.panel = panel

    def write(self, imagefile):
        fileimg = Image.open(imagefile)

        w,h = fileimg.size

        rsimg = fileimg
        if w > self.panel.width or h > self.panel.height:
            rsimg.thumbnail(self.panel.size)

        xpadding = (self.panel.width - rsimg.size[0]) // 2
        ypadding = (self.panel.height - rsimg.size[1]) // 2

        image = Image.new('1', self.panel.size, WHITE)
        image.paste(rsimg, (xpadding, ypadding))

        self.panel.display(image)
        self.panel.update()
