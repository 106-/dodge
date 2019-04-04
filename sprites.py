
from gamelib import dx, to_strbuf
import os.path

class sprites:
    _instance = None
    graphic_dir = "graphix" 
    CAT_FILENAME = os.path.join(graphic_dir, "genba_cat.png")
    CAT = None

    def __init__(self):
        pass

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.CAT = dx.dx_LoadGraph(to_strbuf(cls.CAT_FILENAME))
        return cls._instance