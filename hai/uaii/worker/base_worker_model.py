


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
    
    @auto_stream
    def inference(self, **kwargs):
        """需要重写函数"""
        raise NotImplementedError("Please implement this method")
    
    def train(self, **kwargs):
        """需要重写函数"""
        raise NotImplementedError("Please implement this method")
    
    def evaluate(self, **kwargs):
        """需要重写函数"""
        raise NotImplementedError("Please implement this method")
    

    def get_misc(self, **kwargs):
        """需要重写函数"""
        misc = dict()
        misc['trainable'] = self.trainable
        misc['inferable'] = self.inferable
        return misc