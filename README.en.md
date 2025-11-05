> Для просмотра README на русском, нажмите [сюда](README.md)

# XGlove

XGlove is a Python library designed to work with controller glove *X.Glove*.
It allows to read data from strain gauge and inertial sensor and also display it on OLED-display.

## Features

- Read roll, pitch and yaw from inertial sensor.
  - Get finger bend ratio in percentage.
  - Get output resistance from strain gauge on every finger.
  - Display data on monochrome 128x64 OLED-display via `luma.oled`.
  - Easy integration in Python projects.

## Installation
```shell
pip install xglove
```
```shell
pip install git+https://github.com/XaleraBLT/xglove.git
```

## Functions

### Physical device

#### Device initialization
```python
import xglove
glove = xglove.Glove()
```
#### Read data from strain gauge
<details><summary>Finder indicies (finger_num):</summary>
<li>0 - thumb
<li>1 - inder
<li>2 - middle
<li>3 - ring
</details>

`glove.get_finger_percent(0)` - get finger bend ratio

`glove.get_finger_voltage(0)` - get output resistance from strain gauge

`glove.get_finger_raw(0)` - get raw bend value from 0 to 65536

#### Get data from inertial sensors
<details><summary>Angles (*angles):</summary>
<li>roll is x
<li>pitch is y
<li>yaw is z
</details>

`glove.get_angles("roll", "pitch", "yaw")` - get angles of palm rotation (0-360)

#### Display data:

<details><summary>Attributes description:</summary>
<li>angles = (roll, pitch, yaw) - rotation angles (0-360)
<li>fingers = (100, 100, 100, 100) - bend ratio of each finger (0-100)
<li>text_attributes = (text, font) - write text on a display (optional, max. resolution is 108x44)
<li>image - image (optional, max resolution is 108x44)
</details>

`glove.render_data(angles, fingers)` - display data

### Data exchange between devices

#### Via cable
*On your device:*
```python
import xglove
glove = xglove.Glove()
xglove.connectors.host.Serial_connector(glove)
```
*On receiving device:*
```python
import xglove
con = xglove.connectors.client.Serial_connector(port="COM1") # Regarding of port in device manager
```
#### Via hotspot
*On your device:*
```python
import xglove
glove = xglove.Glove()
xglove.connectors.host.Socket_connector(glove)
```
*On receiving device:*
```python
import xglove
con = xglove.connectors.client.Socket_connector()
```
<details><summary><h4>Connector attributs</h4></summary>
<li><code>con.fingers_percent</code> - returns dict with keys from 0 to 3 with bend rations of each finger
<li><code>con.fingers_voltage</code> - returns dict with keys from 0 to 3 with strain gauge values from each finger
<li><code>con.fingers_raw</code> - returns dict with raw data ranging from 0 to 65536
<li><code>con.x // con.y // con.z</code> - returns angle value from 0 to 360
</details>

#### Upload python file on device (only through hotspot)
```python
import xglove
xglove.utils.update_code("/path/to/your/code.py")
```

## Device scheme

<img alt="X.Glove device scheme" src="docs/xglove_v0.3.png" width="800"/>
