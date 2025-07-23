# 使用 openai 官方客户端进行测试
import openai
from pathlib import Path
here = Path(__file__).parent
import os
api_key = os.getenv("DDF_ZDZHANG_API_KEY")
api_key = os.getenv("HEPAI_API_KEY")
api_key = "Hi-nIghqFDqJazCTrGExKbxrWDiUXfEwPCRhniMxGlUsqUfFci"


# 配置自定义 API base
base_url = "https://aiapi.ihep.ac.cn/apiv2"
base_url="http://localhost:42601/apiv2"
client = openai.OpenAI(
    # base_url="http://localhost:8000/apiv2",
    base_url=base_url,
    api_key=api_key,  # 只要不是空即可，mock服务不会校验
)

test_file = f"{here.parent.parent.parent}/assets/A-I-HEP图标.png"


def test_upload_file():
    print("1. 上传文件 (fine-tune)...")
    file_obj = client.files.create(
        file=open(test_file, "rb"),
        purpose="user_data"
        )
    print(f"Response:", file_obj)
    # 新增预览提示
    preview_url = f"{base_url}/files/{file_obj.id}/preview"
    print(f"可在浏览器访问预览该文件: {preview_url}")
    return file_obj

def test_list_files():
    print("2. 列举所有文件...")
    resp = client.files.list()
    print("Response:", resp)
    print(f"文件数量: {len(resp.data)}")
    return resp.data

def test_retrieve_file(file_id):
    print(f"3. 获取文件信息: {file_id}")
    resp = client.files.retrieve(file_id)
    print("Response:", resp)

def test_download_file_content(file_id, save_as="downloaded_file.jsonl"):
    print(f"4. 下载文件内容: {file_id}")
    content = client.files.content(file_id)
    with open(save_as, "wb") as f:
        f.write(content.read())
    print(f"文件已保存为: {save_as}")

def test_delete_file(file_id):
    print(f"5. 删除文件: {file_id}")
    resp = client.files.delete(file_id)
    print("Response:", resp)

if __name__ == "__main__":
    # 1. 上传文件
    file_obj = test_upload_file()
    file_id = file_obj.id
    # 2. 列举文件
    files = test_list_files()
    # 3. 获取文件信息
    if file_id:
        test_retrieve_file(file_id)
    # 4. 下载文件内容
    if file_id:
        test_download_file_content(file_id, save_as=file_obj.filename)
    # 5. 删除文件
    # if file_id:
    #     test_delete_file(file_id)
