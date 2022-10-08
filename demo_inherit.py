"""通过继承的方法实现推理"""

import hai
import hai.nn as nn
print(dir(nn))
# nn.UNet()
exit()  # TODO

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.unet = nn.UNet()
        self.unet_config = self.unet.config
        print(self.unet_config)
    
    def forward(self, x):
        return self.unet(x)


def run():
    model = MyModel()


    ret = model(x)


if __name__ == '__main__':
    run()