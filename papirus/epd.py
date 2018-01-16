# qCopyright 2013-2015 Pervasive Displays, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.


import os
import re

from PIL import Image
from PIL import ImageOps

from papirus import LM75B
from papirus.panel import Panel, DisplayError


class EPDError(DisplayError):
    pass


class EPD(Panel):
    """
    EPD E-Ink interface

    to use:
      from EPD import EPD

      epd = EPD([path='/path/to/epd'], [auto_update=boolean], [rotation = 0|90|180|270])

      image = Image.new('1', epd.size, 0)
      # draw on image
      epd.clear()         # clear the panel
      epd.display(image)  # transfer image data
      epd.update()        # refresh the panel image - not needed if auto_update is True
    """

    PANEL_RE = re.compile('^([A-Za-z]+)\s+(\d+\.\d+)\s+(\d+)x(\d+)\s+COG\s+(\d+)\s+FILM\s+(\d+)\s*$', flags=0)

    def __init__(self, epd_path='/dev/epd', rotation=0, auto_update=False):
        self._epd_path = epd_path
        self._panel = 'EPD 2.0'
        self._cog = 0
        self._film = 0

        self.use_temp_sensor = True
        self._lm75b = LM75B()

        with open(os.path.join(self._epd_path, 'version')) as f:
            self._version = f.readline().rstrip('\n')

        width, height = 0, 0
        with open(os.path.join(self._epd_path, 'panel')) as f:
            m = self.PANEL_RE.match(f.readline().rstrip('\n'))
            if not m:
                raise EPDError('invalid panel string')
            self._panel = m.group(1) + ' ' + m.group(2)
            width = int(m.group(3))
            height = int(m.group(4))
            self._cog = int(m.group(5))
            self._film = int(m.group(6))

        super(EPD, self).__init__(width=width, height=height, rotation=rotation, auto_update=auto_update)

    @property
    def panel(self):
        return self._panel

    @property
    def version(self):
        return self._version

    @property
    def cog(self):
        return self._cog

    @property
    def film(self):
        return self._film

    def error_status(self):
        with open(os.path.join(self._epd_path, 'error'), 'r') as f:
            return f.readline().rstrip('\n')

    def _write(self, image):
        with open(os.path.join(self._epd_path, 'LE', 'display_inverse'), 'r+b') as f:
            f.write(image.tobytes())

    def update(self):
        self._command('U')

    def partial_update(self):
        self._command('P')

    def fast_update(self):
        self._command('F')

    def clear(self):
        self._command('C')

    def _command(self, c):
        if self.use_temp_sensor:
            with open(os.path.join(self._epd_path, 'temperature'), 'wb') as f:
                f.write(str(self._lm75b.getTempC()).encode(encoding='ascii'))
        with open(os.path.join(self._epd_path, 'command'), 'wb') as f:
            f.write(c)
