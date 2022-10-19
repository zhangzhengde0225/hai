import os, sys
from pathlib import Path
pydir = Path(os.path.abspath(__file__)).parent

# from damei.nn.api import MODULES, SCRIPTS, IOS
# from damei.nn.api import Config
# from damei.nn.api import AbstractInput, AbstractOutput, AbstractModule
from hai import MODULES, SCRIPTS, IOS, Config
from hai import AbstractModule, AbstractInput, AbstractOutput, AbstractQue

from .dataloader import Dataloader


@IOS.register_module(name='ImagesLoader')
class VisLoader(AbstractInput):
    name = 'ImagesLoader'
    description = '图像数据加载器(支持：image, video, folds, rtsp, rtmp等) hai'
    module_path = f'{Path(os.path.abspath(__file__))}'

    def __init__(self, **kwargs):
        """
        Visible light data loader, such as image, video, folds, rtsp, rtmp etc.
        :param kwargs:
            source: data source, path or url
            img_size: image size, default is 640
        :return:
            4 element tuple of ecah entity: (img_path, img, raw_img, is_cap)
        example:
        >>> vis_loader = VisLoader(source='/path/to/data', img_size=640)
        >>> for i, (path, img, im0, is_cap) in enumerate(vis_loader.data):
        >>>     print(i, path, img.shape, im0.shape, is_cap)
        """
        super(VisLoader, self).__init__(**kwargs)

        source = kwargs.pop('source', None)
        img_size = kwargs.pop('img_size', 640)
        batch_size = kwargs.pop('batch_size', 1)

        if isinstance(source, str) and batch_size:
            source = [source]

        self.data = Dataloader(source=source, imgsz=img_size)


if __name__ == '__main__':
    visloader = VisLoader()
