


from hepai import HepAI, RemoteModel

# model: RemoteModel = HepAI(base_url="http://localhost:42600/apiv2"
#                            ).connect_to("hepai/custom-model")

model: RemoteModel = HepAI(base_url="http://localhost:42601/apiv2"
                           ).connect_to("hepai/custom-model")

print(model.worker_info)  # Get worker info.
print(model.functions)  # Get all remote callable functions.
print(model.function_details)  # Get all remote callable function details.

# Call the `custom_method` of the remote model.
output = model.custom_method(a=1, b=2)
print(f"output: {output}")

# call the `get_stream` of the remote model.
stream = model.get_stream(stream=True)  # Note: You should set `stream=True` additionally.
print(f"Output of get_stream:")
for x in stream:
    print(f"{x}, type: {type(x)}", flush=True)



