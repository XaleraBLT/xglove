from setuptools import setup, find_packages
from pathlib import Path
here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name='xglove',
    version='0.2.1.3',
    description="Библиотека созданная для устройства XGlove",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'adafruit-circuitpython-ads1x15==2.4.4',
        'luma.oled==3.14.0',
        'pillow==10.4.0',
        'smbus2==0.5.0',
        'numpy==1.24.4',
        'Adafruit-Blinka==8.62.0',
        'RPi.GPIO==0.7.1'
    ],
    python_requires='>=3.8',
    include_package_data=True
)
