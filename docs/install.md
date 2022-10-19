

## Install HAI
Installation of HEPAI

HEPAI is available on PyPI and can be installed using pip:
```bash
pip install hepai
conda install hepai  # alternative
```

or from source:
```bash
git clone https://github.com/zhangzhengde0225/hai.git
cd hai
python setup.py install
```
## Dependencies

```txt
damei
easydict
numpy
opencv-python
pillow
tqdm
wandb

# torch>=1.7.1 # for all features
```

You can install the dependencies using pip:
```bash
pip install -r requirements.txt
# or install one by one
pip install <package_name>
```