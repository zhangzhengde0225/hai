import hai

uaii = xai.UAII(is_center=True)
print(uaii.ps())  # 接口所有信息
"""例如：
ID    TYPE    NAME                              STATUS   INCLUDE     DESCRIPTION             CONFIG
s01   stream  visible_detection_stream          stopped  [m01]       stream description      None
s02   stream  visible_tracking_stream           stopped  [m01][m03]  stream description      None
m01   module  seyolov5                          stopped  -           可见光目标检测算法         -
m02   module  radardet                          stopped  -           毫米波雷达聚类检测模块      -
m03   module  deepsort                          stopped  -           基于deepsort的目标跟踪算法 -
IO01  io      visible_dataloader_input_stream   stopped  -           可见光数据输入流           -
IO02  io      visible_dataloader_output_stream  stopped  -           可见光数据输出流           -
IO03  io      uaii_yolov5_output_stream         stopped  -           seyolov5 输出流          -
IO04  io      uaii_deepsort_output_stream       stopped  -           seyolov5 输出流          -
IO05  io      default name                      stopped  -           default description     -
"""

# print(uaii.stream_info(name='visible_tracking_stream'))  # 打印流的配置信息
result = uaii.run_stream(stream='visible_tracking_stream')
for i, data in enumerate(result):
    print(i, data)  # 连续运行流的输出结果
