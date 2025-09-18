

from hepai import HepAI, RemoteModel

model: RemoteModel = HepAI(base_url="http://localhost:42600/apiv2"
                           ).connect_to("hepai/simple-model")

print(model.worker_info)  # Get worker info.
print(model.functions)  # Get all remote callable functions.
print(model.function_details)  # Get all remote callable function details.

output = model.simple_method(a=1, b=2)
print(f"output: {output}")





