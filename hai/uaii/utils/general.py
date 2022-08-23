"""
uaii general
"""
import damei as dm
import numpy as np


def single_plot(result, orig_img, target_names):
    """
    把检测结果绘制到原始图像上。
    :param result: ndarray [n, 6] 或者 [n, 9],
    :param orig_img:
    :param target_names: 目标类别list
    :return:
    """
    if result is None or len(result.shape) == 1:
        return orig_img
    else:
        out_img = np.copy(orig_img)
        # result  [num_obj, 10]，10: xyxy cls tid trace keypoints kp_score proposal_score
        # print('')
        # print(result.shape)
        shape = result.shape
        # print(shape)
        if shape[1] == 6:
            format = 'seyolov5'
        else:
            raise NotImplementedError(f'仅支持seyolov5的输出格式，{shape}')

        for i, target in enumerate(result):
            if format == 'seyolov5':
                bbox_xyxy = target[:4]

                target_cls = target[5]
                confidence = target[4]
                target_name = target_names[int(target_cls)]
                label = f"{target_name} {confidence:.2f}"
                trace = None
                status = None
                keypoints = None
                kp_score = None
            else:
                bbox_xyxy = target[:4]
                target_cls = target[4]
                tid = target[5]
                trace = target[6]
                keypoints = target[7]
                kp_score = target[8]
                pro_socre = target[9]

                status_idx = target[10]
                status_name = target[11]
                status_score = target[12]

                status_topx = 2
                if status_idx is None:
                    status = None
                else:
                    status = [f'{status_score[k]:.2f} {x}' for k, x in enumerate(status_name[:status_topx:])]

                target_name = target_names[target_cls]
                status = status if target_name == 'person' else None

                # print(
                # 	f'\nobj_idx: {i} target: {target_name} tracking_id: {tid}\nidx  : {status_idx} '
                # 	f'\nname : {status_name} \nscore: {status_score}')

                first_status = status_name[0] if status_name is not None else ''
                label = f"{tid:<2} {target_name} {first_status}"
            # exit()
            # status = person[11] if person[11] is not None else 'unk'
            out_img = dm.general.plot_one_box_trace_pose_status(
                bbox_xyxy, out_img,
                label=label, color=None, trace=trace, status=status,
                line_thickness=4, keypoints=keypoints, kp_score=kp_score)
        return out_img
