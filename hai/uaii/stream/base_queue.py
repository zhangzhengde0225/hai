"""
抽象的队列
"""

import os, sys

from collections import deque


class AbstractQue(deque):

    def __init__(self, maxlen=5, *args, **kwargs):
        super(AbstractQue, self).__init__(maxlen=maxlen, *args, **kwargs)

    def get_last(self):
        item = self.popleft()
        while self:
            item = self.popleft()
        return item
