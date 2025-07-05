
import os, sys
# import cv2  # delay import
import base64



def load_img(img_path):
    import cv2
    assert os.path.exists(img_path), f"图片{img_path}不存在"
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def sam_pre_process(data):
    import cv2
    import numpy as np  # delay import
    
    input_points = data.pop('input_points', None)
    input_labels = data.pop('input_labels', None)
    input_boxes = data.pop('input_boxes', None)
    
    img = data.pop('img', None)
    assert img is not None, "The img need to be provided."
    if isinstance(img, str):  # 路径，加载为图片
        assert os.path.exists(img), f"图片{img}不存在"
        if os.path.isfile(img):
            img = load_img(img)
    if isinstance(img, np.ndarray):  # 图片，转换为base64
        img = cv2.imencode('.jpg', img)[1]
        img = str(base64.b64encode(img))[2:-1]
        
    
    if (input_points is None) and (input_boxes is None):
        auto_mask = True
    else:
        auto_mask = False
    
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
    
    new_data = dict()
    new_data['model'] = data['model']
    new_data['messages'] = messages
    new_data.update(data)
    
    return new_data

def sam_post_process(data):
    import numpy as np  
    # return data
    if isinstance(data[0], dict):
        only_mask = False
    else:
        only_mask = True

    if only_mask:
        for mask_info in data:
            mask_info = np.array(mask_info, dtype=np.int32)
    else:
        for i, mask_info in enumerate(data):
            mask_info['segmentation'] = np.array(mask_info['segmentation'], dtype=np.int32)
        
    return data