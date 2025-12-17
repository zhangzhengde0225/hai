

from hepai import HepAI
import os

client = HepAI(
    api_key=os.environ.get("HEPAI_API_KEY"),
    base_url="https://aiapi.ihep.ac.cn/apiv2"
)
agents = client.agents.list()

for agent in agents:
    print(agent)
print(f"Total agents: {len(agents)}")

"""
输出示例：
AgentInfo(id='hepai/edge-agent-demo', object='agent', owner='zdzhang@ihep.ac.cn', description='This is a custom remote worker created by HepAI.', version='1.0', metadata={'limit_model_concurrency': 100, 'uptime': 4.673004150390625e-05, 'join_topics': ['besiii', 'csns']})
"""
