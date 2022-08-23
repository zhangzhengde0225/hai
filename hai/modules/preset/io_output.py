"""
模块的io，模块有输入流和输入流，每个流都有队列
"""
import os, sys
import time
import damei as dm
import time
# from ..registry import MODULES, SCRIPTS, IOS
from damei.nn.api.registry import MODULES, SCRIPTS, IOS
from damei.nn.uaii.stream.base_output import AbstractOutput


# @IOS.register_module(name='uaii_output')
class UaiiOutput(AbstractOutput):
    name = 'uaii_output'
    status = 'stopped'
    description = 'defualt uaii output'

    def __init__(self, m_cfg, *args, **kwargs):
        maxlen = kwargs.get('maxlen', 5)
        super(UaiiOutput, self).__init__(maxlen=maxlen, *args, **kwargs)


# @IOS.register_module(name='uaii_yolov5_output')
class SEYOLOv5OutStream(AbstractOutput):
    name = 'uaii_yolov5_output'
    status = 'stopped'
    description = 'seyolov5输出流'

    def __init__(self, m_cfg, *args, **kwargs):
        print(f'mcfg: {m_cfg}')
        self.m_cfg = m_cfg  # m_cfg是所有该模块的config，输出流只是该模块的一部分
        self.cfg = self.m_cfg['output_stream']
        # print(self.cfg, self.cfg.keys())
        maxlen = self.cfg['que'].get('maxlen', 5)
        super(SEYOLOv5OutStream, self).__init__(maxlen=maxlen, *args, **kwargs)
        self.save_dir = self.cfg.get('save_dir', None)
        self.save_txt = self.cfg.get('save_txt', False)
        self.save_conf = self.cfg.get('save_conf', False)
        self.print_ret = self.cfg.get('print_ret', True)
        self.que_wait = self.cfg['que'].get('wait', True)
        self.status = 'ready'

    def __repr__(self):
        format_str = f'<class "{self.__class__.__name__}"> ' \
                     f'(name="{self.name}", status="{self.status}", description="{self.description}")'
        return format_str

    def __call__(self, idx, ret, paths, imgs, im0s, *args, **kwargs):
        self.status = 'running'

        # 1.保存
        if self.save_dir:
            # TODO: 保存检测后的图像
            if self.save_txt:
                pass
                if self.save_conf:
                    pass
            raise NotImplementedError('save not implemented')

        # 2.打印结果
        if self.print_ret:
            self.analyse_and_print_ret(ret, names=self.m_cfg.model.names)

        # 3.输出到队列
        # TODO wait，现在是不wait
        if self.cfg['que']['enabled']:
            # self.status = ''
            self.push([idx, ret, paths, imgs, im0s], que_wait=self.que_wait)

    def analyse_and_print_ret(self, ret, names=None):
        """
        ret: list, [bs]个元素，每个元素是(num_obj, 13), 13=10+3, 2: status_idx, status_name, status_score
        """
        print(f'{"-":-<30} {"Print Detection Results":^25} {"-":-<30}')
        names = names if names else self.m_cfg.model.names
        head = ['Batch', 'Target', 'Bounding_box', 'Conf', 'Class', 'Class']
        for i in range(len(ret)):
            ptn_list = [[head]]
            single_ret = ret[i]  # 单图像的
            if single_ret is None:
                ptn_list.append([i, None, None, None, None])
            else:
                sp = single_ret.shape  # shape
                num_targets = sp[0]
                for j, target in enumerate(single_ret):
                    bbox_xyxy = target[:4]
                    conf = target[4]
                    target_cls = target[5]

                    tmp = [i + 1,
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


# @IOS.register_module(name='uaii_deepsort_output')
class DeepSortOutStream(AbstractOutput):
    name = 'uaii_deepsort_output'
    status = 'stopped'
    description = 'deepsort输出流'

    def __init__(self, m_cfg, *args, **kwargs):
        self.m_cfg = m_cfg  # m_cfg是所有该模块的config，输出流只是该模块的一部分
        self.cfg = self.m_cfg.output_stream
        # print(self.cfg, self.cfg.keys())
        maxlen = self.cfg.que.get('maxlen', 5)
        super(DeepSortOutStream, self).__init__(maxlen=maxlen, *args, **kwargs)
        self.que_wait = self.cfg.que.get('wait', True)

    def __repr__(self):
        format_str = f'{self.__class__.__name__}' \
                     f'(name="{self.name}")'
        return format_str

    def __call__(self, data, *args, **kwargs):
        if self.cfg.que.enabled:
            self.push(data, que_wait=self.que_wait)
