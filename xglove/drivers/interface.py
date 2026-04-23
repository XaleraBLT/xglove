from __future__ import annotations

import math
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, Union, List


class Interface(object):

    def __init__(self, device: ssd1306, font: ImageFont):
        self._draw = None
        self._img = None
        self._device = device
        self._font = font

    def render_data(self,
                    angles: Union[Tuple[float | int, ...], List[float | int]],
                    fingers: Union[Tuple[float | int, ...], List[float | int]],
                    text_attributes: Optional[Tuple[str, ImageFont, bool]] = None,
                    image: Optional[Image.Image] = None) -> Image.Image:

        self._img = Image.new("1", (128, 64), 0)
        self._draw = ImageDraw.Draw(self._img)

        self.__draw_background()
        self.__fill_squares(fingers)
        self.__text_xyz(angles)

        if text_attributes:
            self.__draw_text(text_attributes)
        elif image:
            self.__draw_image(image)

        self._device.display(self._img)

        return self._img

    def __draw_background(self):
        self._draw.line((0, 10, 108, 10), fill=1)
        self._draw.line((108, 0, 108, 64), fill=1)

        self._draw.rectangle([(113, 5), (123, 15)], outline=1, fill=0)
        self._draw.rectangle([(113, 20), (123, 30)], outline=1, fill=0)
        self._draw.rectangle([(113, 35), (123, 45)], outline=1, fill=0)
        self._draw.rectangle([(113, 50), (123, 60)], outline=1, fill=0)

    def __fill_squares(self,
                       percents: List[float | int]):
        for square_num in range(4):
            percent = percents[square_num]
            y_down = (square_num + 1) * 15 - 1
            level = math.ceil(percent / (100 / 9))
            for line in range(level):
                self._draw.line((113, y_down - line, 123, y_down - line), fill=1)

    def __text_xyz(self,
                   angles: List[float | int]):

        x_str = f"{round(angles[0]):<3}"
        y_str = f"{round(angles[1]):<3}"
        z_str = f"{round(angles[2]):<3}"
        final_string = f"X: {x_str} Y: {y_str} Z: {z_str}"

        self._draw.text((3, -2), final_string, fill=1, font=self._font)

    def __draw_text(self,
                    text_attributes: Tuple[str, ImageFont, bool]):
        on_center = text_attributes[2]
        font = text_attributes[1]
        img_width, img_height = 108, 54

        if on_center:
            text = self.__wrap_text(text_attributes)
        else:
            text = text_attributes[0]

        bbox = self._draw.multiline_textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if text_width > img_width or text_height > img_height:
            raise ValueError("Text does not fit into 108x54 area")

        if on_center:
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2 + 5
        else:
            x, y = 0, 10

        self._draw.multiline_text((x, y), text, fill=1, font=font)

    def __draw_image(self,
                     image: Image.Image):
        if image.mode != "1":
            raise ValueError("The image must be 1-bit monochrome (mode '1')")

        img_width, img_height = 108, 54
        width, height = image.size

        if width > img_width or height > img_height:
            raise ValueError("Image does not fit into 108x54 area")

        x = (img_width - width) // 2
        y = (img_height - height) // 2

        self._img.paste(image, (x, y + 10))

    @staticmethod
    def __wrap_text(text_attributes: Tuple[str, ImageFont, bool]) -> str:
        text, font, _ = text_attributes
        _width = 108
        _img = Image.new("1", (_width, 44), 0)
        _draw = ImageDraw.Draw(_img)

        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = _draw.multiline_textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= _width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return "\n".join(lines)
