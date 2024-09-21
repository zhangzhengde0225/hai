


from torchvision.models import resnet50
from haiparticle.models import particletransformer, ParticleTransformer_Weights

# Load the model without weights
model = particletransformer(weights=None)
# Load the model with pre-trained weights
# model = particletransformer(weights="JETCLASS_V1")

print(model)
pass