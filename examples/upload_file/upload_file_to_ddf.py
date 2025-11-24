


from hepai import HepAI

file_path = "data/sample.txt"

client = HepAI()
file_obj = client.files.create(
    file=open(file_path, "rb"),
    purpose="ddf",
)

