from . import connectors
from . import utils

try:
    from .glove import *
except ImportError:
    class Glove:
        def __init__(self, *args, **kwargs):
            raise AttributeError("Аппаратная часть XGlove не поддерживается на данном устройстве. Используется "
                                 "заглушка.")

        def __str__(self):
            return "Аппаратная часть XGlove не поддерживается на данном устройстве. Используется заглушка."
