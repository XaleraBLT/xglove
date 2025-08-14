# XGlove

XGlove — Python-библиотека для работы с перчаткой-контролёром X.Glove. 
Позволяет считывать данные с тензорезисторов и акселерометра, а также визуализировать их на OLED-дисплее.

## Возможности

- Считывание углов наклона (pitch, roll, yaw) с акселерометра.
- Получение процентов сгиба каждого пальца.
- Получение выходного напряжения с датчика каждого пальца
- Отображение данных на монохромном OLED-дисплее 128x64 через `luma.oled`. 
- Простая интеграция в Python-проекты.

## Установка

Через pip:

```bash
pip install xglove
```
```bash
pip install git+https://github.com/XaleraBLT/xglove.git
```

## Функции
```python
import xglove
from PIL import ImageFont, Image
import random

glove = xglove.Glove() # инициализация объекта перчатки

finger_percent = glove.get_finger_percent(0) # Получение процента сгиба пальца 0
finger_voltage = glove.get_finger_voltage(3) # Получение выходного напряжения из пальца 3

pitch, roll, yaw = glove.get_angle("pitch", "roll", "yaw") 
# Получение углов: pitch <--> x; roll <--> y; yaw <--> z

font = ImageFont.truetype("font.ttf", size=10)
text = "Hello World!"

frame = glove.render_data(angles=(pitch, roll, yaw), 
                  fingers=[glove.get_finger_percent(p) for p in range(4)],
                  text_attributes=(text, font)) # Вывод данных + текста (необязательно)
# Возвращает кадр

img = Image.new("1", (104, 44))
pixels = img.load()
for x in range(104):
    for y in range(44):
        pixels[x, y] = random.randint(0, 1) # генерация случайного изображения 104x44

glove.render_data(angles=(pitch, roll, yaw), 
                  fingers=[glove.get_finger_percent(p) for p in range(4)],
                  image=img) # Вывод данных + изображения (необязательно)
```