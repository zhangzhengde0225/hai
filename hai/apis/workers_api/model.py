

import os
import requests



class HaiModel(object):

    @staticmethod
    def ensure_api_key(api_key):
        if api_key is None:
            api_key = os.environ.get("HEPAI_API_KEY", None)
        if api_key is None:
            raise ValueError(f"""            
The HepAI API-KEY is required. Please set the environment variable `HEPAI_API_KEY` via `export HEPAI_API_KEY=xxx`.
Alternatively, it can be provided by passing in the `api_key` parameter when calling the method.
""")
        return api_key

    @staticmethod
    def list(**kwargs):
        """List all models.

        :return: The list of models.
        """  
        url = kwargs.get("url", None)
        if not url:
            host = kwargs.get("host", "aiapi.ihep.ac.cn")
            port = kwargs.get("port", None)
            if port:
                url = f"http://{host}:{port}"
            else:
                url = f'https://{host}'
        assert url, f'url or (host and port) is required. For example: url="http://aiapi.ihep.ac.cn:42901"'

        ret = requests.post(
            f"{url}/list_models",
            )
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

    
if __name__ == '__main__':
    ret = HaiModel.list()
    print(ret)
