"""
默认的uaii流的配置
"""

# streams命名规则：键名需包含字符串stream, 特殊键名type
# modules命名规则：键名必须包含type，指定模块名字，列表前后顺序表明模块的前后顺序
stream1 = dict(
    type='visible_detection_stream',  # 流的名字
    description='可见光目标检测流',  # 流的描述
    models=[  # 流包含的模型及其配置文件
        dict(type='seyolov5',
             cfg='xsensing_ai/config/uaii_seyolov5_config.py'),  # 或字符串指定到模块的配置文件xxx.py
    ])

stream2 = dict(
    type='visible_tracking_stream',
    description='可见光目标检测+跟踪流',
    models=[  # 目标检测+跟踪
        dict(type='seyolov5',
             cfg='xsensing_ai/config/uaii_seyolov5_config.py'),
        dict(type='deepsort',
             cfg='xsensing_ai/config/uaii_deepsort_config.py')
    ])

stream3 = dict(
    type='infrared_detection_stream',
    description='红外目标检测流',
    models=[  # 红外目标检测
        dict(type='irdet',
             cfg=None,
             ),
    ]
)

stream4 = dict(
    type='radar_tracking_stream',
    description='雷达检测+跟踪流',
    models=[
        dict(type='radardet',
             cfg=None,
             ),
        dict(type='radarsort',
             cfg=None,
             ),
    ]
)

# 这里包含的才会初始化
"""
streams = [
    stream1,
    stream2,
    stream3,
    stream4,
    ]
"""
streams = []
