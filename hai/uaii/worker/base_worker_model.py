
from typing import List, Dict, Any
from pathlib import Path
here = Path(__file__).parent


class BaseWorkerModel:
    """
    用于被控制工人模型的基类，提供了面向切片的自动流式输出等功能
    Usage:
        class MyWorker(WorkerBaseModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
            
            @WorkerBaseModel.auto_stream  # 自动流式输出
            def inference(self, **kwargs):
                “”“重写推理函数”“”
                return "output"
            
        worker = MyWorker()
        worker.start()
    """
    def __init__(self, **kwargs) -> None:
        self.name = kwargs.pop('name', "hepai/worker-base-model")
        self.trainable = kwargs.pop('trainable', False)
        self.inferable = kwargs.pop('inferable', False)
        self.allowd_functions = ['inference', 'train', 'evaluate', "chat_completions"]

    @staticmethod
    def convert(ret):
        for x in ret:
            yield x

    @staticmethod
    def auto_stream(func):
        """
        自动流式输出
        """
        def warpper(*args, **kwargs):
            stream = kwargs.get('stream', False)    
            output = func(*args, **kwargs)
            if stream:
                is_generator =  type(output) == type((i for i in range(10)))
                if isinstance(output, str):
                    return BaseWorkerModel.convert(output)
                elif is_generator:
                    return output
                else:
                    raise TypeError(f"Output type {type(output)} is supported in stream mode, please use 'str' type.")
            else:
                return output
        return warpper
    
    def inference(self, **kwargs):
        """需要重写函数"""
        raise NotImplementedError(f"The `inference` method of `{self.name}` is not implemented.")
    
    def train(self, **kwargs):
        """需要重写函数"""
        raise NotImplementedError(f"The `train` method of `{self.name}` is not implemented.")
    
    def evaluate(self, **kwargs):
        """需要重写函数"""
        raise NotImplementedError(f"The `evaluate` method of `{self.name}` is not implemented.")
    
    def get_misc(self, **kwargs):
        """需要重写函数"""
        misc = dict()
        misc['trainable'] = self.trainable
        misc['inferable'] = self.inferable
        return misc
    
    def chat_completions(self, **kwargs):
        raise NotImplementedError(f'The `chat_completions` method of `{self.name}` is not implemented.')
    
    def get_int(self, **kwargs):
        return 1
    
    def get_float(self, **kwargs):
        return 1.0
    
    def get_bool(self, **kwargs):
        return True
    
    def get_str(self, **kwargs):
        return "string"
    
    def get_list(self, **kwargs):
        return [1, 2, 3]
    
    def get_dict(self, **kwargs):
        return {"key": "value"}
    
    def get_image(self, **kwargs):
        return Path(f"{here}/assets/demo.png")
    
    def get_pdf(self, **kwargs):
        return Path(f"{here}/assets/demo.pdf")

    def get_txt(self, **kwargs):
        return Path(f"{here}/assets/demo.txt")

    def get_stream(self, **kwargs):
        range_num = kwargs.get('range_num', 10)
        out = [i for i in range(range_num)]
        for i in out:
            yield f'data: {i}\n\n'
