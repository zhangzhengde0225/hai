


## 如何通过hepai的API使用Segment Anything Model (SAM)

## 安装hepai
```
pip install hepai --upgrade
```
### 安装依赖包
```
pip install opencv-python
pip install pillow
pip install tqdm
```

### 配置API_KEY 

+ 获取HEPAI_API_KEY
  访问HepAI平台网站[https://ai.ihep.ac.cn](https://ai.ihep.ac.cn)获取。

+ Linux设置永久环境变量
    ```bash
    vi ~/.bashrc
    将下一行内容添加到文件末尾：
    export HEPAI_API_KEY=<your api key>
    保存后执行：source ~/.bashrc刷新环境变量
    ```

## 使用

python示例代码：
```python

import os, sys
import hai
import cv2

models = hai.Model.list()  # 列出所有可用模型
print(models)

img = 'test.jpg'
assert os.path.exists(img), f'file {img} not exists'

masks_list = hai.Models.inference(
        model='meta/segment_anything_model',  # 指定可用模型名字
        api_key=os.getenv("HEPAI_API_KEY"),  # 输入hepai_api_key
        img = img,  # 输入图片路径或cv2读取的图片
        input_points = input_points,  # 点提示，格式为[[x1,y1],[x2,y2],...] 
        input_labels = input_labels,  # 点提示对应的标签，0代表背景点，1代表前景点，格式为[0, 1, ...], 需要与input_points一一对应，如不提供默认全为前景点
        input_boxes = input_boxes,  # 框提示，格式为[[x1,y1,x2,y2],[x1,y1,x2,y2],...]
        stream=True,  # 是否流式输出
        timeout=60,  # 网络请求超时时间，单位秒
    )
"""
返回值为list，每个元素为一个dict，每个dict包含一个分割出的目标，包含以下字段：
segmentation: np.array, 与原图高宽(h, w)相同, 值为0或1, 0代表背景, 1代表前景(分割出的目标)
area: int, 该目标的像素面积
bbox: list, 该目标的bounding box, 格式为[x1, y1, x2, y2]
predicted_iou: float, 该目标的预测iou
points_coords: list, 分割出该目标的点的坐标
stability_score: float, 该目标的稳定性分数
crop_box: list, 该目标的crop box, 格式为[x1, y1, x2, y2]
"""

for mask in masks_list:
    segmentation = mask['segmentation']
    area = mask['area']
    bbox = mask['bbox']
    predicted_iou = mask['predicted_iou']
    points_coords = mask['points_coords']
    stability_score = mask['stability_score']
    crop_box = mask['crop_box']

    cv2.imshow('segmentation', segmentation)


def save_masks(masks, save_path):
    
    path = Path(save_path)
    save_dir = path.parent
    os.makedirs(f'{save_dir}', exist_ok=True)
    os.makedirs(f'{save_dir}/masks', exist_ok=True)
    
    
    for i, mask in enumerate(masks):
        m = mask.pop('segmentation')
        mask_save_path = f'{save_dir}/masks/{path.stem}_{i}.npz'
        np.savez_compressed(mask_save_path, m)
        
        relative_mask_save_path = f'masks/{path.stem}_{i}.npz'
        mask['segmentation_path'] = relative_mask_save_path
        
    with open(save_path, 'w') as f:
        
        json.dump(masks, f, indent=4)
    print(f'saved to {save_path}')

# 将分割结果保存为json文件，对应的mask保存在与json文件同目录下的masks文件夹中
save_masks(masks_list, 'test.json')

