#!coding:utf-8

"""
Segment via HepAI based on SAM.
Author: JiaMeng Zhao, Zhengde Zhang
All rights reserved, 2023. 
This script is free for non-commercial use. Please contact zdzhang@ihep.ac.cn for commercial use.
"""

# from utils import *
# import cv2
import os, sys
from pathlib import Path
here = Path(__file__).parent
import damei as dm
import numpy as np
import base64
import requests
logger = dm.get_logger('seg_via_sam.py')


class SegmentViaSam():

    def __init__(self):
        # 加载模型
        self.url = "http://aiapi.ihep.ac.cn:42901/v1/inference"
        self.model_name = "meta/segment_anything_model"
        self.api_key = os.environ.get("HEPAI_API_KEY")
        # assert api_key is not None, "请设置环境变量HEPAI_API_KEY"
        
    def load_img(self, img_path):
        import cv2
        assert os.path.exists(img_path), f"图片{img_path}不存在"
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    def inference(self, img, **kwargs):
        logger.info(f"Inference ...")
        url = kwargs.get('url', self.url)
        model_name = kwargs.get('model_name', self.model_name)
        stream = kwargs.get('stream', False)
       
        input_points = kwargs.get('input_points', None)
        input_labels = kwargs.get('input_labels', None)
        input_boxes = kwargs.get('input_boxes', None)
         
        # auto_mask = kwargs.get('auto_mask', True)
        if (input_points is None) and (input_boxes is None):
            auto_mask = True
        else:
            auto_mask = False
        
        if isinstance(img, str):  # 路径，加载为图片
            if os.path.isfile(img):
                img = self.load_img(img)
        if isinstance(img, np.ndarray):  # 图片，转换为base64
            import cv2
            img = cv2.imencode('.jpg', img)[1]
            img = str(base64.b64encode(img))[2:-1]
            
        if isinstance(input_points, np.ndarray):
            input_points = input_points.tolist()
        if input_points is not None and input_labels is None:
            input_labels = [1] * len(input_points)
        if isinstance(input_labels, np.ndarray):
            input_labels = input_labels.tolist()
        if isinstance(input_boxes, np.ndarray):
            input_boxes = input_boxes.tolist()
            
        messages = dict()
        messages['img'] = img
        messages['input_points'] = input_points
        messages['input_labels'] = input_labels
        messages['input_boxes'] = input_boxes
        messages['auto_mask'] = auto_mask
        
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": model_name,
                "api_key": self.api_key,
                "stream": stream,
                "messages": messages,
            },
            timeout=60,
            stream=stream
        )
        if response.status_code != 200:
            raise Exception(f"Got status code {response.status_code} from server: {response.text}")
            # print(response.content)  # 只有非流式相应才能查看内容
        data = response.json()
        if data['status_code'] != 42901:
            error_info = f'Request error: {data}'
            logger.error(error_info)
            raise NameError(error_info)
            return error_info
        masks = data['message']
        if auto_mask:  # 全景分割
            return self.post_prosscess_of_panorama(masks, **kwargs)
        return masks

    def post_prosscess_of_panorama(self, masks, **kwargs):
        return_rich_masks = kwargs.get('return_rich_masks', True)
        if return_rich_masks:
            return masks


def seg_imgs(svs):
    img_dir = f'{here.parent.parent}/imgs/008_ImM1_cracks'
    
    imgs = sorted(os.listdir(img_dir))
    for img in imgs:
        img = f'{img_dir}/{img}'
        masks = svs.inference(img)
        print(masks)
        
    
        exit()
    

if __name__ == '__main__':
    svs = SegmentViaSam()
    
    seg_imgs(svs)
    exit()
   
    
    fold = f'xiaoshunao2_output'
    img = f'{here}/imgs/{fold}/raw.png'
    img = f'{here}/imgs/{fold}/thresh_img&img.png'  # 146
    # img = f'{here}/imgs/{fold}/equ_img&img.png'   # 17
    # img = f'{here}/imgs/{fold}/thresh&equ&img.png'  # 8
    img = svs.load_img(img_path=img)
    masks = svs.inference(
        img, 
        # input_points=[[100, 100]],
        )
    # for mask in masks:
    #     segmentation = mask['segmentation']
    #     mask = np.array(segmentation)
    #     print(masks)
    # maskss = np.array(masks)  # shape: (1, 922, 964, 4)
    # masks = maskss[0]
    # tmp = None
    # for i in range(maskss.shape[-1]):  # 4ci 
    #     mask = masks[:, :, i]
    #     cv2.imshow(f'mask{i}', mask)
    #     cv2.waitKey(0)
    #     if tmp is not None:
    #         differ = np.sum(mask-tmp)
    #         print(f'differ: {i} {differ}')
    #     tmp = mask
    # print(masks)
    

    plt.figure(figsize=(10, 10))
    plt.imshow(img)
    show_anns(masks, plt.gca())
    # show_bboxs(mask, plt.gca())
    plt.axis('off')
    plt.show()