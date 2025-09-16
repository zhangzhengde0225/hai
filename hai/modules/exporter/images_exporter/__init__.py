import os, sys
from pathlib import Path
pydir = Path(os.path.abspath(__file__)).parent

import shutil
import json


import damei as dm
# from damei.nn.api import MODULES, SCRIPTS, IOS
# from damei.nn.api import Config
# from damei.nn.api import AbstractInput, AbstractOutput, AbstractModule

from hai import MODULES, SCRIPTS, IOS, Config
from hai import AbstractModule, AbstractInput, AbstractOutput, AbstractQue

# print('visexporter')

@IOS.register_module(name='ImagesExporter')
class VisExporter(AbstractOutput):
    name = 'ImagesExporter'
    description = '图像结果输出器'

    def __init__(self, save_dir=None):
        super(VisExporter, self).__init__()
        self.save_dir = save_dir
        self._init()

    def _init(self):
        if self.save_dir is not None:
            if os.path.exists(self.save_dir):
                empty = len(os.listdir(self.save_dir)) == 0
                if empty:
                    shutil.rmtree(self.save_dir)
                else:  # 非空
                    ipt = input(f'Save dir "{self.save_dir}" not empty, remove all? [YES/no] ')
                    if ipt in ['y', 'Y', 'Yes', 'YES', '']:
                        shutil.rmtree(self.save_dir)
                    else:
                        pass
            os.makedirs(self.save_dir)

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

            label = f'{cls} {score:.2f}'
            color = colors[cls_idx]

            trace = None
            status = None
            keypoints = None
            kp_score = None

            img = dm.general.plot_one_box_trace_pose_status(
                bbox, img,
                label=label, color=color, trace=trace, status=status,
                line_thickness=10, keypoints=keypoints, kp_score=kp_score,
                # skeleton_thickness=3, kp_radius=8, other_kp_radius=4,
        )
        return img

    def save_img(self, save_name, img):
        """
        保存图像
        """
        import cv2
        save_dir = self.save_dir if self.save_dir else '.'
        cv2.imwrite(f'{save_dir}/{save_name}', img)

    def save_json(self, path, img, pred, names):
        import numpy as np

        h, w, c = img.shape

        data = dict()
        data['version'] = 'predict'
        data['flags'] = {}
        data['imagePath'] = path
        data['imageData'] = None
        data['imageHeight'] = h
        data['imageWidth'] = w

        shapes = []
        for i, target in enumerate(pred):
            bbox = target[:4]
            score = target[4]
            cls_idx = target[5]
            cls = names[int(cls_idx)]

            shape = dict()
            shape['label'] = cls
            shape['shape_type'] = 'rectangle'
            shape['group_id'] = None
            shape['flags'] = {}

            # points = [[bbox[0], bbox[1]], [bbox[2], [bbox[3]]]]  # [x1y1x2y2] to [[x1,y1],[x2,y2]]
            points = np.array(bbox, dtype=np.int32).reshape(-1, 2).tolist()
            shape['points'] = points
            shapes.append(shape)
        data['shapes'] = shapes

        save_dir = self.save_dir if self.save_dir else '.'
        save_path = f'{save_dir}/{Path(path).stem}.json'
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=4)

    def analyse_and_print_ret(self, ret, names):
        """
        ret: list, [bs]个元素，每个元素是(num_obj, 13), 13=10+3, 2: status_idx, status_name, status_score
        """
        print(f'{"-":-<30} {"Print Detection Results":^25} {"-":-<30}')
        head = ['Batch', 'Target', 'Bounding_box', 'Conf', 'Class', 'Class']
        if True:
            ptn_list = [head]
            single_ret = ret  # 单图像的
            if single_ret is None:
                ptn_list.append([0, None, None, None, None])
            else:
                sp = single_ret.shape  # shape
                num_targets = sp[0]
                for j, target in enumerate(single_ret):
                    bbox_xyxy = target[:4]
                    conf = target[4]
                    target_cls = target[5]

                    tmp = [0 + 1,
                           f'{j + 1}/{num_targets}',
                           ' '.join([str(int(x)) for x in bbox_xyxy]),
                           float(conf),
                           int(target_cls),
                           names[int(target_cls)],
                           ]

                    ptn_list.append(tmp)

            format_str = dm.misc.list2table(ptn_list, alignment="<")
            print(format_str)

        print(f'{"-":-<30} {"End Print":^25} {"-":-<30}')

