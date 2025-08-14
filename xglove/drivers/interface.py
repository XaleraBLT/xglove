from __future__ import annotations

import math
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, Union, List


class Interface(object):
    """
        Класс Interface отвечает за отрисовку данных на OLED-дисплее SSD1306
        с использованием библиотеки Pillow.

        Возможности:
        - Отрисовка сетки фона и разделителей
        - Отображение текущих значений углов X, Y, Z
        - Заполнение индикаторов (4 вертикальных прямоугольника) по процентам
        - Вывод текста с автоматическим переносом по ширине
        - Отображение монохромных изображений

        Параметры конструктора:
            device (ssd1306): Экземпляр OLED-дисплея.
            font (ImageFont): Экземпляр шрифта для отрисовки текста (встроен).

    """

    def __init__(self, device: ssd1306, font: ImageFont):
        self._draw = None
        self._img = None
        self._device = device
        self._font = font

    def render_data(self,
                    angles: Union[Tuple[float | int, ...], List[float | int]],
                    fingers: Union[Tuple[float | int, ...], List[float | int]],
                    text_attributes: Optional[Tuple[str, ImageFont]] = None,
                    image: Optional[Image.Image] = None) -> Image.Image:
        """
            Отрисовывает текущий кадр на OLED-дисплее на основе переданных данных
            о положении и состоянии сенсоров.

            Параметры:
                angles (tuple[float, float, float]):
                    Кортеж с углами ориентации устройства.
                    Формат: (pitch, roll, yaw)
                    pitch (x) — наклон вперёд/назад (градусы, диапазон -180..180)
                    roll (y) — наклон влево/вправо (градусы, диапазон -180..180)
                    yaw (z)  — поворот вокруг оси Z (градусы, диапазон -180..180)

                fingers (tuple[int | float, int | float, int | float, int | float]):
                    Кортеж или список с процентом сгиба для каждого из 4 тензодатчиков.
                    Формат: (f1, f2, f3, f4)
                    Значения — дробные и(или) целые числа 0–100 (%), где 0 = полностью разогнут,
                    100 = максимально согнут.

                text_attributes (tuple[str, ImageFont], optional):
                    Необязательный параметр для вывода текста.
                    Формат: (текст, шрифт)
                    текст — строка, поддерживаются пробелы и перенос строк.
                    шрифт — объект PIL.ImageFont, с заранее определённым размером шрифта\
                    Суммарный размер строк должен соответствовать разрешению выведенному окну дисплея (108x44)

                image (PIL.Image.Image, optional):
                    Необязательный монохромный рисунок для отображения на экране.
                    Размер должен соответствовать разрешению выведенному окну дисплея (108x44)
            Возвращает:
                Полученное изображение, которое было выведено на экран
        """

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
        for square_num in range(1, 5):
            percent = percents[square_num - 1]
            y_down = square_num * 15 - 1
            level = math.ceil(percent / (100 / 9))
            for line in range(level):
                self._draw.line((113, y_down - line, 123, y_down - line), fill=1)

    def __text_xyz(self,
                   angles: List[float | int]):

        x_str = f"{round(angles[0]):<3}"
        y_str = f"{round(angles[1]):<3}"
        z_str = f"{round(angles[2]):<3}"
        final_string = f"X:{x_str} Y:{y_str} Z:{z_str}"

        self._draw.text((3, -2), final_string, fill=1, font=self._font)

    def __draw_text(self,
                    text_attributes: Tuple[str, ImageFont]):
        wrapped_text = self.__wrap_text(text_attributes)
        font = text_attributes[1]
        img_width, img_height = 108, 44

        bbox = self._draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if text_width > img_width or text_height > img_height:
            raise ValueError("Text does not fit into 108x44 area")

        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2

        self._draw.multiline_text((x, y + 10), wrapped_text, fill=1, font=font)

    def __draw_image(self,
                     image: Image.Image):
        if image.mode != "1":
            raise ValueError("The image must be 1-bit monochrome (mode '1')")

        _width, _height = 108, 44
        width, height = image.size

        if width > _width or height > _height:
            raise ValueError("Image does not fit into 108x44 area")

        x = (_width - width) // 2
        y = (_height - height) // 2

        self._img.paste(image, (x, y + 10), image)

    @staticmethod
    def __wrap_text(text_attributes: Tuple[str, ImageFont]) -> str:
        text, font = text_attributes
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
