

import os
from hepai import HepAI
from hepai import RemoteModel
    
def connect(
    name: str = "hepai/markitdown",
    base_url: str = "https://aiapi.ihep.ac.cn/apiv2",
    api_key: str = os.getenv("HEPAI_API_KEY"),
    **kwargs,
):
    """
    Connect to hepai resources. such as remote model, llm, etc.
    Args:
        name (str): The name of the resource to connect to.
        base_url (str): The base URL of the resource.
    """
    client = HepAI(
        base_url=base_url,
        api_key=api_key,
        **kwargs,
        )
    
    model: RemoteModel = client.get_remote_model(model_name=name)
    
    return model
