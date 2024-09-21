

import torchvision

import haiparticle
import torchvision.datasets
from torchvision.transforms import ToTensor


training_data = torchvision.datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor(),
)

pass