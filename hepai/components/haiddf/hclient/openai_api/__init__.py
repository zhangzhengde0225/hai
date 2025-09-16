



# try:
    
# except:
#     raise ImportError("openai not found, please install openai first, `pip intall openai>=1.55.0`")


# from openai._base_client import SyncAPIClient, AsyncAPIClient
# from openai._constants import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
# from openai._types import NOT_GIVEN, Omit
# from openai._qs import Querystring
# from openai._streaming import Stream
# from openai._exceptions import APIStatusError, OpenAIError
# from .adapted_openai.version import __version__ as __openai_version__
# from .adapted_openai._base_client import SyncAPIClient, AsyncAPIClient
# from .adapted_openai._constants import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
# from .adapted_openai._types import NOT_GIVEN, Omit
# from .adapted_openai._qs import Querystring
# from .adapted_openai._streaming import Stream, AsyncStream
# from .adapted_openai._exceptions import APIStatusError, OpenAIError
# from .adapted_openai import resources
# from .adapted_openai.types.chat import *



# __all__ = ["SyncAPIClient", "AsyncAPIClient", "DEFAULT_MAX_RETRIES", "DEFAULT_TIMEOUT", 
#            "NOT_GIVEN", "Omit", "Querystring", "Stream", "AsyncStream", "APIStatusError", "OpenAIError",
#            "resources", "ChatCompletion", "ChatCompletionChunk",
#            ]




from openai.version import __version__ as __openai_version__

# from openai._base_client import SyncAPIClient, AsyncAPIClient
from openai._constants import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT
from openai._types import NOT_GIVEN, Omit
from openai._qs import Querystring
from openai._streaming import Stream, AsyncStream
from openai._exceptions import APIStatusError, OpenAIError
from openai import resources
from openai.types.chat import *

from .bridge import HAsyncAPIClient as AsyncAPIClient
from .bridge import HSyncAPIClient as SyncAPIClient


