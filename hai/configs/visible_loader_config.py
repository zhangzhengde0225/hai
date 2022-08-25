# 可以是文件夹、图像、list、rtsp
source = '~/datasets/xsensing/mm_data/slice_P4_1217/vis'
# 到这里值是定义了一个输入的流的源和resize的过程，加载到的是ndarray的数据，未归一化
img_size = 640

input_stream = dict(
    type='visible_dataloader_input_stream',
    enabled=False,
    que=dict(),  # 输入只需要知道队列名字就可以
)

output_stream = dict(
    type='visible_dataloader_output_stream',
    enabled=True,
    que=dict(
        enabled=True,
        wait=False,
    ),
)
