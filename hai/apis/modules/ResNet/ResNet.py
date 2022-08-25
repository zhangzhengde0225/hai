import hai


@hai.MODULES.register_module(name='ResNet')
class ResNet(hai.AbstractModule):
    name = 'ResNet'
    description = 'ResNet网络'

    def __init__(self, *args, **kwargs):
        super(ResNet, self).__init__(*args, **kwargs)
        self._init()

    def _init(self):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def single_plot(self, img, preds, names):
        """
        单张图片绘制
        :param img:
        :param bboxes:
        :param scores:
        :param classes:
        :return:
        """
        # print('bb', bboxes)
        # print(f'scores: {scores}')
        # print(f'classes: {classes}')
        bboxes = preds[:, :4]
        scores = preds[:, 4]
        classes_idx = [int(x) for x in preds[:, 5]]
        classes = [names[int(x)] for x in classes_idx]
        colors = [(204, 0, 0), (0, 130, 255), (0, 204, 0), (0, 0, 204), (255, 130, 0)]

        for i, bbox in enumerate(bboxes):
            score = scores[i]
            cls_idx = classes_idx[i]
            cls = names[cls_idx]