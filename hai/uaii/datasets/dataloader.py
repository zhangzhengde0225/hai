import os
import cv2
from pathlib import Path
import numpy as np
import damei as dm
from copy import deepcopy

try:
    import torch.backends.cudnn as cudnn
    from .datasets import LoadStreams, LoadImages
except ImportError as e:
    pass
    # dm.EXCEPTION(ImportError, e, info='You may need to install "torch" for full functionality', mute=True)


class Dataloader(object):
    def __init__(self, source=None, imgsz=None):
        self.video_suffix = ['.mp4', '.avi', '.wmv']
        self.imgsz = imgsz

        if isinstance(source, str):
            self.dataset = self.get_dataset(source)
        elif isinstance(source, list):
            datasets = [None] * len(source)
            for i, s in enumerate(source):
                datasets[i] = self.get_dataset(s)
            self.dataset = MultiDatasets(datasets)
        else:
            raise NotImplementedError

    def get_dataset(self, source):
        imgsz = self.imgsz
        video_suffix = self.video_suffix
        webcam = source.isnumeric() or source.startswith(('rtsp://', 'rtmp://', 'http://')) or source.endswith('.txt')
        if webcam:
            cudnn.benchmark = True  # set True to speed up constant image size inference
            dataset = LoadStreams(source, img_size=imgsz, flip=False)
            dataset.is_camera = True
            dataset.is_video = False
        else:
            dataset = LoadImages(source, img_size=imgsz)
            dataset.is_camera = False
            dataset.is_video = True if Path(source).suffix in video_suffix else False
        return dataset


class MultiDatasets(object):

    def __init__(self, datasets):
        self.datasets = datasets
        # print(f'multi {self.datasets}')
        self.is_camera = False
        self.is_video = False
        self.count = -1

    def __len__(self):
        datasets = self.datasets
        return int(np.mean([len(x) for x in datasets]))

    def __iter__(self):
        return self

    def __next__(self):
        datasets = self.datasets
        num = len(self.datasets)
        self.count += 1
        imgs = [None] * num
        im0s = [None] * num
        paths = [None] * num
        vid_caps = [None] * num
        for i, dset in enumerate(datasets):
            # 不同的数据集长度不一样呀可能会报错
            path, imgs[i], im0s[i], vid_caps[i] = next(dset)
            if dset.is_camera:
                im0s = im0s[0]
                path = f'{path[0]}/{self.count:0>6}.jpg'
            elif dset.is_video:
                path = f'{path}/{self.count:0>6}.jpg'
            else:
                pass
            paths[i] = path
        # print('\nxx', path)
        imgs = np.array(imgs)
        im0s = np.array(im0s)
        # print('xxx', imgs.shape, im0s.shape)
        return paths, imgs, im0s, vid_caps


def load_single_img(file, img_sz=640, return_list=False):
    if not os.path.exists(file):
        return
    im0 = cv2.imread(file)
    img, ratio, (dw, dh), recover = dm.general.letterbox(deepcopy(im0), new_shape=img_sz)
    img = img[:, :, ::-1].transpose(2, 0, 1)
    img = np.ascontiguousarray(img)

    if return_list:
        return [file], img[np.newaxis, :], [im0]
    else:
        return file, img, im0
