# XGlove

XGlove — Python-библиотека для работы с перчаткой-контролёром X.Glove. 
Позволяет считывать данные с тензорезисторов и инерциального датчика, а также выводить их на OLED-дисплей.

## Возможности

- Считывание углов наклона (roll, pitch, yaw) с инерциального датчика.
- Получение процентного соотношения сгиба пальцев.
- Получение выходного напряжения с тензорезистора каждого пальца.
- Отображение данных на монохромном OLED-дисплее 128x64 через `luma.oled`. 
- Простая интеграция в Python-проекты.

## Установка
```bash
pip install xglove
```
```bash
pip install git+https://github.com/XaleraBLT/xglove.git
```

## Функции

### Физическое устройство  

#### Инициализация устройства
```python
import xglove
glove = xglove.Glove()
```
#### Считывание данных с тензорезисторов


<details><summary>Индексы пальцев (finger_num):</summary>
<li>0 - большой
<li>1 - указательный
<li>2 - средний
<li>3 - безымянный
</details>

`glove.get_finger_percent(0)` - получение процентного отношения сгиба пальца

`glove.get_finger_voltage(0)` - получение выходного напряжения с пальца

`glove.get_finger_raw(0)` - получение сырого значения изгиба от 0 до 65536

#### Считывание данных с инерциональных датчиков
<details><summary>Обозначение углов (*angles):</summary>
<li>roll или x - крен
<li>pitch или y - тангаж
<li>yaw или z - рыскание
</details>

`glove.get_angles("roll", "pitch", "yaw")` - получение углов поворота ладони (0-360)

#### Вывод данных на дисплей:

<details><summary>Описание аттрибутов:</summary>
<li>angles = (roll, pitch, yaw) - углы поворота (0-360)
<li>fingers = (100, 100, 100, 100) - процентное соотношение изгиба для каждого пальца (0-100)
<li>text_attributes = (текст, шрифт) - отображение текста на дисплее (необязательно, максимальное разрешение 108x44)
<li>image - изображение (необязательно, максимальное разрешение 108x44)
</details>

`glove.render_data(angles, fingers)` - вывод данных на дисплей

### Обмен данных между устройствами

#### Через провод
*На устройстве:*
```python
import xglove
glove = xglove.Glove()
xglove.connectors.host.Serial_connector(glove)
```
*На приёмной машине:*
```python
import xglove
con = xglove.connectors.client.Serial_connector(port="COM1") # В зависимости от порта в диспетчере устройств
```
#### Через точку доступа
*На устройстве:*
```python
import xglove
glove = xglove.Glove()
xglove.connectors.host.Socket_connector(glove)
```
*На приёмной машине:*
```python
import xglove
con = xglove.connectors.client.Socket_connector()
```
<details><summary><h4>Аттрибуты коннектора</h4></summary>
<li><code>con.fingers_percent</code> - возвращает словарь с ключами от 0 до 3, значениями которого являются процентные отношения сгибов пальцев
<li><code>con.fingers_voltage</code> - возвращает словарь с ключами от 0 до 3, значениями которого являются выходные напряжения с пальцев
<li><code>con.fingers_raw</code> - возвращает словарь с ключами от 0 до 3, значениями которого являются сырые данные от 0 до 65536
<li><code>con.x // con.y // con.z</code> - возвращает значение угла от 0 до 360
</details>

#### Загрузка python-файла на устройство (только через точку доступа)
```python
import xglove
xglove.utils.update_code("путь_к_коду.py")
```