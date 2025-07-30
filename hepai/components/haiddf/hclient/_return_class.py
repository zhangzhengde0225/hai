"""
客户端的返回值类
"""

from typing import Any, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from ._related_class import WorkerInfo, UserInfo, APIKeyInfo
from ._related_class import AgentInfo
from ._types import Stream
# from .oai_base_client._models import BaseModel


@dataclass    
class HListPage:
# class HListPage(BaseModel):
    """用户Client从服务器端获取到List类的消息后解析该对象"""

    object: str = 'list'
    data: List[Any] = field(default_factory=list, metadata={'description': 'List of data'})
    first_id: str = None
    last_id: str = None
    has_more: bool = False
    offset: int = field(default=None, metadata={'description': 'Offset for pagination'})
    total: int = field(default=None, metadata={'description': 'Total number of items'})
    page_number: int = field(default=None, metadata={'description': 'Page number'})

    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        return iter(self.data)
    
    def __getitem__(self, index):
        return self.data[index]
    

@dataclass
class HWorkerListPage(HListPage):

    """用户Client从服务器端获取到List类的消息后解析该对象"""
    # object: str = 'list'
    # first_id: str = None
    # last_id: str = None
    # has_more: bool = False
    data: List[WorkerInfo] = field(default_factory=List[WorkerInfo], metadata={'description': 'List of data'})
    # data: List[WorkerInfo] 

    def __post_init__(self):
        self.data = self.parse_worker_info(self.data)

    def parse_worker_info(self, data_list: List[dict]) -> List[WorkerInfo]:
        worker_infos = []
        for item in data_list:
            # Parse each item to populate WorkerInfo data class
            try:
                worker_info = WorkerInfo(**item)
                worker_infos.append(worker_info)
            except Exception as e:
                print(f"Failed to parse WorkerInfo: {e}")
                raise e
        return worker_infos
    
    def to_table(self):
        """转换为表格数据"""
        table_data = {
            "order": [],
            "id": [],
            "type": [],
            "worker_address": [],
            "model_names": [],
            "speed": [],
            "queue_length": [],
            "status": [],
            # "model_onwer": [],
            # "model_groups": [],
            # "model_users": [],
            "host_name": [],
            "last_heartbeat": [],
            # "model_functions": [],
            # "metadata": [],
        }
        for i, worker_info in enumerate(self.data):
            mress = worker_info.resource_info  # model resource 

            table_data["order"].append(i)
            table_data["id"].append(worker_info.id)
            table_data["type"].append(worker_info.type)
            table_data["worker_address"].append(worker_info.network_info.worker_address)
            table_data["model_names"].append([x.model_name for x in mress])
            table_data["speed"].append(worker_info.status_info.speed)
            table_data["queue_length"].append(worker_info.status_info.queue_length)
            table_data["status"].append(worker_info.status_info.status)
            # table_data["model_onwer"].append([x.model_onwer for x in mress])
            # table_data["model_groups"].append([x.model_groups for x in mress])
            # table_data["model_users"].append([x.model_users for x in mress])
            # table_data["model_functions"].append([x.model_functions for x in mress])
            table_data["host_name"].append(worker_info.network_info.host_name)
            
            last_heartbeat = worker_info.last_heartbeat
            formatted_last_heartbeat = datetime.fromtimestamp(last_heartbeat).strftime("%Y-%m-%d %H:%M:%S")
            table_data["last_heartbeat"].append(formatted_last_heartbeat)
            # table_data["metadata"].append(worker_info.metadata)
        return table_data
    
@dataclass
class HUserListPage(HListPage):
    """用户Client从服务器端获取到List类的消息后解析该对象"""
    data: List[UserInfo] = field(default_factory=List[UserInfo], metadata={'description': 'List of data'})
 
    def __post_init__(self):
        # 解析用户数据
        self.data = self.parse_user_info(self.data)

    def parse_user_info(self, data_list: List[dict]) -> List[dict]:
        user_infos = []
        for item in data_list:
            user_info = UserInfo(**item)
            user_infos.append(user_info)
        return user_infos
    
    def to_table(self):
        table_data = {
            "order": [],
            "username": [],
            "user_level": [],
            "expiration_time": [],
            "auth_type": [],
            "user_groups": [],
            "phone": [],
            "email": [],
            "create_time": [],
            "id": [],
            "umt_id": [],
            "cluster_uid": [],
            "remarks": [],
        }
        for i, user_info in enumerate(self.data):
            table_data["order"].append(i)
            table_data["id"].append(user_info.id)
            table_data["username"].append(user_info.username)
            table_data["user_level"].append(user_info.user_level.str())
            table_data["expiration_time"].append(user_info.user_level.expiration_time)
            table_data["user_groups"].append([x.name for x in user_info.user_groups if x.name])
            table_data["phone"].append(user_info.phone)
            table_data["email"].append(user_info.email)
            table_data["auth_type"].append(user_info.auth_type)
            table_data["create_time"].append(user_info.create_time)
            table_data["remarks"].append(user_info.remarks)
            table_data["umt_id"].append(user_info.umt_id)
            table_data["cluster_uid"].append(user_info.cluster_uid)
        return table_data
    

@dataclass
class HAPIKeyListPage(HListPage):
    """用户Client从服务器端获取到List类的消息后解析该对象"""
    data: List[APIKeyInfo] = field(default_factory=List[APIKeyInfo], metadata={'description': 'List of data'})

    def __post_init__(self):
        self.data = self.parse_api_key_info(self.data)

    def parse_api_key_info(self, data_list: List[dict]) -> List[APIKeyInfo]:
        """将API-KEY信息解析为APIKeyInfo对象"""
        api_key_infos = []
        for item in data_list:
            if isinstance(item, dict):
                item = APIKeyInfo(**item)
            api_key_infos.append(item)
        return api_key_infos
    
    def to_table(self):
        table_data = {
            "order": [],
            "alias": [],
            "api_key": [],
            "expiration_time": [],
            "user_id": [],
            "id": [],
            "create_time": [],
            "create_by": [],
            "update_time": [],
            "remarks": [],
        }
        for i, api_key_info in enumerate(self.data):
            table_data["order"].append(i)
            table_data["id"].append(api_key_info.id)
            table_data["alias"].append(api_key_info.alias)
            table_data["api_key"].append(api_key_info.api_key)
            table_data["expiration_time"].append(api_key_info.expiration_time)
            table_data["create_time"].append(api_key_info.create_time)
            table_data["create_by"].append(api_key_info.created_by)
            table_data["update_time"].append(api_key_info.update_time)
            table_data["remarks"].append(api_key_info.remarks)
            table_data["user_id"].append(api_key_info.user_id)
        return table_data

    
@dataclass
class HAgentListPage(HListPage):
    """用户Client从服务器端获取到List类的消息后解析该对象"""
    data: List[dict] = field(default_factory=list, metadata={'description': 'List of data'})

    def __post_init__(self):
        # 解析代理数据
        self.data = self.parse_agent_info(self.data)

    def parse_agent_info(self, data_list: List[dict]) -> List[dict]:
        agent_infos = []
        for item in data_list:
            agent_info = AgentInfo(**item)
            agent_infos.append(agent_info)
        return agent_infos
    
    