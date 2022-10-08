# from distutils.log import info
import os
import numpy as np
from PIL import Image
import torch
from torch.utils.data import DataLoader, random_split

import hai
from hai import AbstractModule, AbstractInput, AbstractOutput, AbstractQue
from hai import MODULES, SCRIPTS, IOS, Config

src_path = 'hai/modules/segmentation/Pytorch_UNet'
cwd = os.getcwd()
# from hai.modules.segmentation.Pytorch_UNet import train_hai
from . import train_api
from . import Pytorch_UNet
from . import predict_api
from . import evaluate_api
from . import argparse_config
from . import CarvanaDataset


@MODULES.register()
class UNet(AbstractModule):
    name = 'UNet'
    description = '2015 Classic Segmentation Algorithm UNet'
    

    def __init__(self):
        super().__init__()
        # self.default_cfg = f"{hai.root_path}/hai/configs/UNet/UNet_default_cfg.py"
        # self.default_cfg = train.get_args()
        self.default_cfg = argparse_config.get_args()
        # self.default_cfg.exporter = 'ImagesExporter'

    def __call__(self, img, *args, **kwargs):
        ## 输入的x是ndarray，需要前处理
        if isinstance(img, np.ndarray):
            img = Image.fromarray(np.uint8(img))

        ret = predict_api.predict_img(
                net=self.model,
                full_img=img,
                device=self.device,
                scale_factor=self.cfg.scale,
                out_threshold=self.cfg.mask_threshold,
        )
        return ret

    def build_model(self, *args, **kwargs):
        device = self.device
        cfg = self.cfg
        model = Pytorch_UNet(n_channels=3, n_classes=cfg.classes, bilinear=cfg.bilinear)
        if self.cfg.weights:
            model.load_state_dict(torch.load(self.cfg.weights, map_location=device))
        model.to(device=device)
        return model

    def train(self, cfg=None, *args, **kwargs):
        cfg = cfg if cfg else self.cfg
        train_api.run(args=cfg)
        # print('train') 
        # print(self.config)

    def predict(self, cfg=None, *args, **kwargs):
        cfg = cfg if cfg else self.cfg
        predict_api.run(args=cfg)

    def evaluate(self, cfg=None, *args, **kwargs):
        cfg = cfg if cfg else self.cfg
        # evaluate_api.run(args=cfg)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = self.build_model()
        model.to(device=device)

        img_dir = f'{cfg.source}/imgs'
        mask_dir = f'{cfg.source}/masks'
        
        val_set = CarvanaDataset(img_dir, mask_dir, scale=cfg.scale)
        # train_set, val_set = random_split(val_set, [5000, 88], generator=torch.Generator().manual_seed(0))
        val_loader = DataLoader(val_set, 
            shuffle=False, drop_last=True, 
            batch_size=cfg.batch_size, num_workers=4, pin_memory=True)
        ret = evaluate_api.evaluate(
            net=model,
            dataloader=val_loader,
            device=device,
        )
        score = ret.detach().cpu().numpy()
        info = 'Score: {:.8f}'.format(score)
        # print(f'Evaluate score: {score}')
        return info


    
