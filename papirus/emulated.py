import io
import shutil

from PIL import Image

from papirus.panel import Panel


class EmulatedPanel(Panel):
    def __init__(self, out_path, width, height):
        super(EmulatedPanel, self).__init__(width, height)
        self.out_path = out_path
        self.max_frames = -1
        self._frame = 0
        self._buffer = None

        self.clear()

    def update(self):
        out_path = self.out_path.format(i=self._frame)
        with open(out_path, 'wb') as f:
            shutil.copyfileobj(self._buffer, f)

        self._frame += 1
        if self.max_frames != -1 and self._frame >= self.max_frames:
            self._frame = 0

    def clear(self):
        self._write(Image.new('1', self.size, self.WHITE))

    def _write(self, image):
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)

        self._buffer = buf
