import hai

uaii = hai.UAII(is_center=True)
print(uaii.ps())  # 接口所有信息
# print(uaii.get_module('IO01'))


# model = hai.hub.load('')
model = hai.model.load('YOLOv5_v6')
print(model)


exit()
# print(uaii.stream_info(name='visible_tracking_stream'))  # 打印流的配置信息
result = uaii.run_stream(stream='visible_tracking_stream')
for i, data in enumerate(result):
    print(i, data)  # 连续运行流的输出结果
