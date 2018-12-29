"""
The :class:`GBTile` class represents a single GameBoy tile (8x8 pixels, 16
Bytes).

Creating a tile from scratch::

    from img2gb import GBTile

    tile = GBTile()
    tile.put_pixel(0, 0, 3)  # Put a black pixel at (0, 0)
    tile.data  # -> [128, 128, 0, 0, 0, ...]
    tile.to_hex_string()  # -> "80 80 00 00 00 ..."

Creating a tile from a PIL image::

    from img2gb import GBTile
    from PIL import Image

    image = Image.open("./my_tile.png")
    tile = GBTile.from_image(image)
"""


from .helpers import (
        to_pil_rgb_image,
        rgba_brightness,
        brightness_to_color_id)


class GBTile(object):
    """Stores and manipulates data of a single GameBoy tile (8x8 pixels).

    :var list data: Raw data of the tile (list of int).
    """

    @classmethod
    def from_image(Cls, pil_image, tile_x=0, tile_y=0):
        """Create a new GBTile from the given image.

        :param PIL.Image.Image pil_image: The input PIL (or Pillow) image.
        :param int tile_x: The x location of the tile in the image (default =
                           ``0``).
        :param int tile_y: The y location of the tile in the image (default =
                           ``0``).

        :rtype: GBTile
        """
        image = to_pil_rgb_image(pil_image)
        tile = Cls()

        for y in range(8):
            for x in range(8):
                pix_rgb = image.getpixel((tile_x + x, tile_y + y))
                pix_brightness = rgba_brightness(*pix_rgb)
                color_id = brightness_to_color_id(pix_brightness)
                tile.put_pixel(x, y, color_id)

        return tile

    def __init__(self):
        self.data = [0x00] * 16

    def put_pixel(self, x, y, color_id):
        """Set the color of one of the tile's pixels.

        :param int x: The x coordinate of the pixel to change (0-7).
        :param int y: The y coordinate of the pixel to change (0-7).
        :param int color_id: the color of the pixel (0-3).
        """
        mask = 0b00000001 << (7 - x)
        mask1 = mask if color_id & 0b01 else 0b00000000
        mask2 = mask if color_id & 0b10 else 0b00000000

        # Clear changing bits
        self.data[y*2+0] &= ~mask
        self.data[y*2+1] &= ~mask

        # Set bits
        self.data[y*2+0] |= mask1
        self.data[y*2+1] |= mask2

    def to_hex_string(self):
        """Returns the tile as an hexadecimal-encoded string.

        :rtype: str
        """
        return " ".join(["%02X" % b for b in self.data])

    def __eq__(self, other):
        if not isinstance(other, GBTile):
            return False
        return self.to_hex_string() == other.to_hex_string()
