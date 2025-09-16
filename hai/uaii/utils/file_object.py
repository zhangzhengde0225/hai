
from typing import Any, Dict, List, Tuple, Union
from dataclasses import dataclass
from io import BytesIO


@dataclass
class HaiFile:
    """
    a file object for parsing the file content
    """
    type_: str
    data: Any
    filename: str = None

    def __post_init__(self):
        if self.type_ == 'image':
            from PIL import Image
            import numpy as np

            self.data = BytesIO(self.data)
            img = Image.open(self.data)
            self.data = np.array(img)
        # elif self.type_ == 'txt':
        #     self.data = self.data.read().decode('utf-8')

    @property
    def type(self):
        return self.type_

    def read(self):
        return self.data
    
    def save(self, file_path: str=None, save_dir: str = None, debug=False):
        if file_path is None:
            if save_dir is None:
                file_path = self.filename
            else:
                file_path = f'{save_dir}/{self.filename}'
        if not file_path:
            raise ValueError("Please specify the file path, or the save_dir and filename.")
        if self.type_ == 'image':
            from PIL import Image
            img = Image.fromarray(self.data)
            img.save(file_path)
        else:
            with open(file_path, 'wb') as f:
                f.write(self.data)
        if debug:
            print(f"Save file to {file_path}")

    




