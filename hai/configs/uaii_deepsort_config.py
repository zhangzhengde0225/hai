model = dict(
    type='deepsort',
    weights="~/weights/xsensing/deepsort_ckpt.t7",
    use_cuda=False,
    multi_tracker=1,  # 跟踪器数目
)

output_stream = dict(
    type='uaii_deepsort_output',
    que=dict(
        enabled=True,
        maxlen=5,
        wait=True
    ),
)
