"""
seyolov5模型的配置文件
"""

# 用来加载模型的
model = dict(  # 加载模型时的参数
    type='SEYOLOv5',
    device='0',  # GPU
    weights='~/weights/xsensing/yolov5x_3.0.pt',  # ~代表用户根目录
    half=True,  # 半精度浮点数
    augment=False,
    use_se=False,
    backnone=None,
    neck=None,
    head=None,
    names=[  # 所有类别
        'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
        'tennis racket', 'bottle',
        'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
        'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
        'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven',
        'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
        'hair drier', 'toothbrush'],
)

input_stream = dict(
    type='visible_input',
    enabled=False,
    source='~/datasets/xsensing/mm_data/slice_P4_1217/vis',  # 可以是文件夹、图像、list、rtsp
    img_size=640,  # 到这里值是定义了一个输入的流的源和resize的过程，加载到的是ndarray的数据，未归一化
)

post_process = dict(
    type='yolov5 post process',
    nms=dict(  # non max suppression
        conf_thres=0.25,  # 置信度阈值
        iou_thres=0.45,  # iou阈值
        agnostic_nms=False,
    ),
    filt_classes=dict(  # 仅指定的类别有效，不指定为None或为空列表
        enabled=True,
        valid_classes=[
            'person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck', 'chair', 'bed'],
    ),
)

output_stream = dict(
    type='uaii_yolov5_output',
    save_dir=None,  # 如果有路径，保存为检测后的图像为{save_dir}/{stem}.jpg
    save_txt=False,  # 如果为True且有保存路径，保存检测结果的txt到{save_dir}/{stem}.txt
    save_conf=False,  # 如果为True，.txt内除了类别和bbox，还保存置信度
    print_ret=False,  # 打印结果到控制台
    que=dict(
        enabled=True,
        maxlen=5,
        wait=True,
    ),  # 如果为True，检测结果push到队列里。
)

# 训练配置
train = dict(
    optimizer=dict(
        type='Adam',
    ),
    max_epoches=100,
    augment=True,

)
