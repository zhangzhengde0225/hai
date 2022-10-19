import time
from damei.nn.uaii.stream.base_queue import AbstractQue


class AbstractOutput(object):
    name = 'default name'
    status = 'stopped'
    description = 'default description'

    def __init__(self, maxlen=5, *args, **kwargs):
        self.que = AbstractQue(maxlen, *args, **kwargs)
        self.timeout = 5

    def __len__(self):
        return len(self.que)

    def __iter__(self):
        return self

    def __next__(self):
        return self.get_last()

    def push(self, data, que_wait=False):
        wait_time = que_wait if isinstance(que_wait, int) else 0.0001
        if que_wait:
            while True:
                if len(self.que) <= 3:
                    self.que.append(data)
                    break
                time.sleep(wait_time)
        else:
            self.que.append(data)
            time.sleep(wait_time)

    def pop(self, wait=True, timeout=None):
        """取出"""
        timeout = timeout if timeout else self.timeout
        if self.status == 'done':
            return 'done'
        if len(self.que):
            return self.que.pop()
        else:
            if wait:
                t0 = time.time()
                while True:
                    if len(self.que):
                        return self.que.pop()

                    if time.time() - t0 > timeout:
                        raise TimeoutError(f'Time out of {timeout}s while pop que.')
                    time.sleep(0.00001)
            else:
                return None

    def get_last(self, wait=True, timeout=None):
        """全部取出，只返回最后一个"""
        timeout = timeout if timeout else self.timeout
        if self.status == 'done':
            return 'done'
        data = None
        if len(self.que):
            while len(self.que):
                data = self.que.popleft()
            return data
        else:
            if wait:
                t0 = time.time()
                while True:
                    if len(self.que):
                        assert len(self.que) == 1
                        return self.que.pop()
                    if time.time() - t0 > timeout:
                        raise TimeoutError(f'Time out of {timeout}s while pop que.')
                    time.sleep(0.00001)
            else:
                return None

    def scan(self, last=False):
        """窥视"""
        if self.status == 'done':
            return 'done'
        if len(self.que):
            tmp = self.que[-1] if last else self.que[0]
            return tmp
        else:
            return None
