import os, sys
import time
import damei as dm
import cv2
import shutil

from ..utils.config_loader import PyConfigLoader
from ..registry import MODULES, SCRIPTS, IOS
from .dataloader import Dataloader

logger = dm.getLogger('uaii loaders')


# @MODULES.register_module(name='visible_loader')
class VisibleLoader(Dataloader):
    name = 'visible_loader'
    status = 'stopped'
    description = '可见光数据加载器'
    default_cfg = None
    tag = 'cloud'

    def __init__(self, cfg=None):
        if isinstance(cfg, str) and cfg:
            cfg = PyConfigLoader(cfg)
        self.cfg = cfg
        source = cfg.get('source', None)
        imgsz = cfg.get('img_size', 640)
        assert source
        super(VisibleLoader, self).__init__(source=source, imgsz=imgsz)
        self.mi = None
        self.mo = None
        self.que_wait = self.cfg.output_stream.que.get('wait', True)

    def __call__(self, *args, **kwargs):
        """不断加载数据，存到que中"""
        wait = kwargs.pop('wait', self.que_wait)  # 等待有后面的东西拿掉再推

        for img_idx, data in enumerate(self.dataset):
            paths, imgs, im0s, vid_cap = data
            if wait:
                while True:
                    if len(self.mo.que) == 0:
                        self.mo.push([paths, imgs, im0s, vid_cap])
                        break
                    time.sleep(0.0001)
            else:
                self.mo.push([paths, imgs, im0s, vid_cap])
                time.sleep(0.0001)  # 0.1 ms
            # print(imgs.shape)
        # print(self.mo)


class XsensingLoader(object):
    """Xsensing传感器加载数据"""

    def __init__(self, ip, port, imgsz=640):
        self.ip = ip
        self.port = port
        self.imgsz = imgsz
        self.dataloader = None

    def __call__(self, show=True, raw=True, scale=1):
        ip = self.ip
        port = self.port
        imgsz = self.imgsz
        rtsp = f"rtsp://{ip}:{port}/live/stream"
        dataloader = Dataloader(source=rtsp, imgsz=imgsz)

        for i, (path, img, im0, cap) in enumerate(dataloader.dataset):
            # print(i, path, img.shape, type(img), cap)

            raw_img = im0[0]
            if raw_img is None:
                continue
            # print(raw_img.shape)
            resized_img = img[0].transpose(1, 2, 0)
            # print(resized_img, resized_img.shape)
            if show:
                show_img = raw_img if raw else resized_img
                h, w, c = show_img.shape
                show_img = cv2.resize(show_img, (int(w * scale), int(h * scale))) if scale else show_img
                cv2.imshow('img', show_img)
                if cv2.waitKey(5) == ord('q'):  # q to quit
                    raise StopIteration

    def show(self, show=True, raw=True, scale=1):
        self.__call__(show=show, raw=raw, scale=scale)

    def record(self, dir, seconds=60):
        """
        :param dir: saved directory
        :param seconds: record time, default 60s
        :return:
        """
        dir = os.path.abspath(dir)
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)

        save_log = []

        rtsp = f"rtsp://{self.ip}:{self.port}/live/stream"  # 目前只支持1个流
        dataloader = Dataloader(source=rtsp, imgsz=self.imgsz)
        save_log.append(f'Source: {rtsp}\n')
        et = dm.plus_time(seconds=seconds)

        for idx, (path, img, im0, cap) in enumerate(dataloader.dataset):
            raw_img = im0[0]
            if raw_img is None:
                continue
            ct = dm.current_time()
            if not dm.within_time(et, ct):
                break

            file_path = f'{dir}/{idx:0>8}.jpg'
            logger.info(f'Saving img: {file_path}')
            cv2.imwrite(filename=file_path, img=raw_img)
            info = f'[{ct}] {dir}/{idx:0>8}.jpg {raw_img.shape}\n'
            save_log.append(info)

        with open(f'{dir}/record.log', 'w') as f:
            f.writelines(save_log)
