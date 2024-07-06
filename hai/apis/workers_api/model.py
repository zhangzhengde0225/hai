#!coding:utf-8
"""
The Models API of HepAI Platform.
Author: Zhengde Zhang
All rights reserved, 2023. 
This script is free for non-commercial use. Please contact zdzhang@ihep.ac.cn for commercial use.
"""

import os, sys
import requests
from pathlib import Path
import damei as dm
here = Path(__file__).parent
try:
    import hai
except:
    sys.path.append(str(here.parent.parent.parent))
    import hai
import base64
from .sam.pre_process import sam_pre_process, sam_post_process
from .nougat.pdf_process import pdf_process

logger = dm.getLogger('model.py')

class PreProcessFunctions:
   
    @staticmethod
    def pre_process(model, data):
        """
        面向切面的编程，输入数据经过预处理函数，再传入模型，若未定义，则不进行预处理。
        """
        if model == "meta/segment_anything_model":
            data = sam_pre_process(data)
        elif model == "hepai/hainougat":
            data = pdf_process(data)
        return data

class PostProcessFunctions:
    @staticmethod
    def post_process(model, data):
        """面向切面的变成，输出结果经过后处理函数，再输出，若未定义，则不进行后处理"""
        if model == "meta/segment_anything_model":
            data = sam_post_process(data)
        return data
    

class HaiModel(object):

    @staticmethod
    def ensure_api_key(api_key):
        if api_key is None:
            api_key = os.environ.get("HEPAI_API_KEY", None)
        if api_key is None:
            raise ValueError(f"""            
The HepAI API-KEY is required. You can set it via `hai.api_key=xxx` in your code, or set the environment variable `HEPAI_API_KEY` via `export HEPAI_API_KEY=xxx`.
Alternatively, it can be provided by passing in the `api_key` parameter when calling the method.
""")
        return api_key
    

    @staticmethod
    def list_models(**kwargs):
        return HaiModel.list(**kwargs)

    @staticmethod
    def list(**kwargs):
        """
        List all models on HepAI Platform.
        :param refresh: Whether to refresh the model list, default is False.
        :param return_all_info: Whether to return all information of the models, default is False.
        :param api_key: Your HepAI api key, can be obtained in https://ai.ihep.ac.cn, only return public models if not provided.
        :return: The list of models.
        """  
        api_key = kwargs.pop("api_key", None) or hai.api_key
        api_key = HaiModel.ensure_api_key(api_key)
        
        url = kwargs.pop("url", None)
        if not url:
            host = kwargs.pop("host", "aiapi.ihep.ac.cn")
            port = kwargs.pop("port", None)  # 42901
            if port is None:
                url = f'https://{host}'  
            else:
                url = f"http://{host}:{port}"
        assert url, f'url or (host and port) is required. For example: url="http://aiapi.ihep.ac.cn:42901"'

        ret = requests.post(
            f"{url}/list_models",
            headers={"Authorization": f"Bearer {api_key}"},
            json=kwargs,
            )
        if ret.status_code != 200:
            raise ValueError(f"Hai Model connect url: {url} Error: \n{ret.status_code} {ret.reason} {ret.text}")
        return ret.json()
    
    @staticmethod
    def all_workers_info(**kwargs):
        models = HaiModel.list()
        api_key = kwargs.pop("api_key", None)
        api_key = HaiModel.ensure_api_key(api_key)
        host = kwargs.get("host", "chat.ihep.ac.cn")
        port = kwargs.get("port", None)
        assert api_key, f'api_key is required.'
        if port:
            url = f"http://{host}:{port}"
        else:
            url = f'https://{host}'
        headers={"Authorization": f"Bearer {api_key}"}
        all_info = dict()
        for model_name in models['models']:
            response = requests.post(
                f"{url}/get_worker_info",
                headers=headers,
                json={
                    "model": model_name,
                },
            )
            worker_info = response.json()['info']
            workers = worker_info[model_name]  # 一个模型可能有多个worker
            workers_info = dict()
            for one_worker in workers:
                address = one_worker.pop('address')
                
                workers_info[address] = one_worker
            # all_info.update(worker_info)
            all_info[model_name] = workers_info
            # print(res.json())
        return all_info
    
    
    @staticmethod
    def inference(model, **kwargs):
        """
        Call the model to execute inference.
        :param model: The model name.
        :param api_key: Your HepAI api key, can be obtained in https://ai.ihep.ac.cn.
        :param timeout：The timeout of the request, default is 60s.
        :param stream: Whether to stream the response, default is False.
        :param kwargs: The input data of the model, they are differ for each model, e.g. {"img": "https://xxx.jpg"}.
        """
        api_key = kwargs.pop("api_key", None)
        stream = kwargs.get("stream", False)
        timeout = kwargs.get("timeout", 60)
        pdfbin = kwargs.get('pdfbin', None)
        api_key = api_key or hai.api_key
        

        url = kwargs.pop("url", None)
        if not url:
            host = kwargs.pop("host", "aiapi.ihep.ac.cn")
            port = kwargs.pop("port", None)
            if port is not None:
                url = f"http://{host}:{port}"
            else:
                url = f"https://{host}"

        data = dict()
        data['model'] = model
        data.update(kwargs)

        assert api_key, """
The HepAI API-KEY is required. Please set the environment variable `HEPAI_API_KEY` via `export HEPAI_API_KEY=xxx`.
Alternatively, it can be provided by passing in the `api_key` parameter when calling the `chat` method.
"""

        if not pdfbin:
            data = PreProcessFunctions.pre_process(model=model, data=data)
        else:
            pdfbin= base64.b64encode(pdfbin).decode()
            data['pdfbin'] = pdfbin

        logger.info(f"Requesting {url} ...")
        # logger.info(f"Requesting data: {data}")
        session = requests.Session()
        response = session.post(
        # response = requests.post(
            f'{url}/v1/inference',
            headers={"Authorization": f"Bearer {api_key}"},
            json=data,
            timeout=timeout,
            stream=stream
        )
        
        if response.status_code != 200:
            raise Exception(f"Got status code {response.status_code} from server: {response.text}")
            # print(response.content)  # 只有非流式相应才能查看内容
        try:
            data = response.json()
            status_code = data.pop('status_code', 42901)
            if status_code != 42901:
                error_info = f'Request error: {data}'
                logger.error(error_info)
                raise Exception(error_info)
        except:
            pass
        
        if not stream:            
            data = response.json()
            data = data['message']
        else: 
            data = response.content.decode('utf-8', errors='ignore')
            data = data.replace('[DONE]', "")
        data = PostProcessFunctions.post_process(model=model, data=data)
        return data
        
    @staticmethod
    def sam(**kwargs):
        """
        Segmeng an image via Segment Anything Model.
        :param img: The image path or image array.
        :param input_points: The input points prompt, e.g. [[x1,y1], [x2,y2], ...], defualt is None.
        :param input_labels: The input labels corresponding to the points prompt, 0 represents the background point, 1 represents the front attraction, and the format is [0, 1,...], which needs to be combined with the input points correspond one by one, if not provided, default to all previous attractions.
        :param input_boxes: The input boxes prompt, e.g. [[x1,y1,x2,y2], [x1,y1,x2,y2], ...], defualt is None.
        :return: The segmentation result. if no prompt is provided, the result is the segmentation of the entire image by front attraction grid points.
        """
        model = "meta/segment_anything_model"
        model2 = kwargs.pop("model", None)
        assert model2 is None or model2 == model, f"model={model2} is not supported, only support model={model}"
        return HaiModel.inference(model=model, **kwargs)
    
    @classmethod
    def dalle3(cls, **kwargs):
        print(cls, kwargs)
        return None
    

if __name__ == '__main__':
    ret = HaiModel.list(
        url="http://aiapi.ihep.ac.cn:42901",
    )
    print(len(ret))
    print(ret)
