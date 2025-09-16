from typing import Any
from mcp.server.fastmcp import FastMCP
from typing import List
import requests


mcp=FastMCP("search")

@mcp.tool()
def web_search(user_input: str,num_results:int=20) -> List:
    """
    这是一个网页查询的服务,可以根据关键词查询网页信息
    Args:
        user_input:用户输入
        num_results:搜索结果的个数
    """
    
    param={
        "user_input": user_input,
        "num_results":num_results
    }
    return requests.get("http://192.168.60.170:42999/",params=param).content.decode('utf-8')


@mcp.tool()
def url_search(url: str|List[str]) -> str:
    """
    这是一个网页查询的服务，可以查询指定网页链接的文本内容
    Args:
        url:输入的网页链接
    """
    
    if type(url)==list:
            result=[]
            for i in url:
                param={
                    "url": i,
                }
                result.append({
                    "url": i,
                    'result':requests.get("http://192.168.60.170:42999/url",params=param).content.decode('utf-8')
                })
            return result
    else:
            param={
                    "url": url
                }
            return [{
                "url": url,
                'result':requests.get("http://192.168.60.170:42999/url",params=param).content.decode('utf-8')
            }]

@mcp.tool()
def arxiv_home_search(key: str) -> List:
    """
    这是一个arviv主页查询的服务，可以指定查询某一关键词返回文章列表，用户输入出现arxiv字样才选择这个
    Args:
        key:上arxiv进行检索的关键词
    """
    
    param={
        "key": key,
    }
    return requests.get("http://192.168.60.170:42999/arxiv-home",params=param).content.decode('utf-8')

@mcp.tool()
def arxiv_paper_search(url: str|List[str]) -> List:
    """
    这是一个查询arxiv上论文的服务，指定论文链接可以返回markdown格式的论文，用户输入出现arxiv字样才选择这个
    Args:
        url:上arxiv进行检索的关键词, url可以是一个字符串或者列表
    """
    if type(url)==list:
        result=[]
        for i in url:
            param={
                "url": i,
            }
            result.append({
                "url": i,
                'result':requests.get("http://192.168.60.170:42999/arxiv-paper",params=param).content.decode('utf-8')
            })
        return result
    else:
        param={
                "url": url
            }
        return [{
            "url": url,
            'result':requests.get("http://192.168.60.170:42999/arxiv-paper",params=param).content.decode('utf-8')
        }]

# @mcp.tool()
# def prepare_sse(input_dict:dict) -> dict:
#     """
#     这是一个连接sse的tool，如果用户需要操作指定ip的文件，则调用这个tool
#     Args:
#         input_dict: 这是一个字典,包含了下面四个参数
#             ip:远程主机ip
#             port:远程主机端口号
#             files:需要操作的文件列表
#             instruction:需要进行的用户指令
#     """
#     try:
#         return {
#             "is_sse":1,
#             "ip":input_dict["ip"],
#             'port':input_dict["port"],
#             'files':input_dict["files"],
#             'instruction':input_dict["instruction"]
#         }
#     except:
#          return "处理失败"



if __name__ == "__main__":
    mcp.run(transport="stdio")




