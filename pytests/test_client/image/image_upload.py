
from hepai import HepAI
from pathlib import Path
here = Path(__file__).parent.resolve()
# from openai import OpenAI12client = OpenAI()

img_file = f'{here.parent.parent.parent}/assets/A-I-HEP.png'
# img = open(img_file, "rb").read()
img = open(img_file, "rb")

client = HepAI(
    
)
response =client.images.create_variation(
    image=img,
    n=2,
    size="1024x1024"
    )
    
print(response)





