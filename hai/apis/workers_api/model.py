

import requests



class HaiModel(object):

    @staticmethod
    def list(**kwargs):
        """List all models.

        :return: The list of models.
        """  
        host = kwargs.get("host", "192.168.68.22")
        port = kwargs.get("port", 42901)
        url = f"http://{host}:{port}"

        ret = requests.post(
            f"{url}/list_models",
            )
        return ret.json()

