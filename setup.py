from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='xglove',
    version='0.3',
    description="Библиотека созданная для устройства XGlove",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'paramiko==3.5.1',
        'numpy==1.24.4',
        'pillow==10.4.0',
        'pyserial==3.5',
        'adafruit-circuitpython-ads1x15==2.4.4; platform_machine=="armv7l" or platform_machine=="aarch64"',
        'luma.oled==3.14.0; platform_machine=="armv7l" or platform_machine=="aarch64"',
        'smbus2==0.5.0; platform_machine=="armv7l" or platform_machine=="aarch64"',
        'Adafruit-Blinka==8.62.0; platform_machine=="armv7l" or platform_machine=="aarch64"',
        'RPi.GPIO==0.7.1; platform_machine=="armv7l" or platform_machine=="aarch64"',
    ],
    python_requires='>=3.8',
    include_package_data=True
)
