from dataclasses import dataclass, field, asdict
from typing import Optional, List, Union, Dict
from datetime import datetime
import uuid


@dataclass
class UserGroupInfo:
    name: str = field(default=None, metadata={'description': 'Name of the user group.'})
    id: Optional[str] = field(default_factory=str, metadata={'description': 'Unique identifier for the user group, typically a UUID.'})
    description: Optional[str] = field(default=None, metadata={'description': 'Description of the user group.'})
    create_time: Optional[datetime] = field(default=None, metadata={'description': 'Timestamp when the user group was created.'})
    created_by: Optional[str] = field(default=None, metadata={'description': 'Identifier for the creator of the user group record.'})
    update_time: Optional[datetime] = field(default=None, metadata={'description': 'Timestamp when the user group record was last updated.'})
    updated_by: Optional[str] = field(default=None, metadata={'description': 'Identifier for who last updated the user group record.'})
    remarks: Optional[str] = field(default=None, metadata={'description': 'Additional remarks or notes about the user group.'})
    del_flag: bool = field(default=False, metadata={'description': 'Flag indicating if the user group is deleted.'})

    def to_dict(self) -> dict:
        return asdict(self)
    

    
@dataclass
class UserLevelInfo:
    user_level: str = field(default='free', metadata={'description': 'User level or role, e.g., admin, user.'})
    id: Optional[int] = field(default=None, metadata={'description': 'Unique identifier for the user level, typically an integer.'})
    expiration_time: Optional[datetime] = field(default=None, metadata={'description': 'Timestamp when the user level expires.'})
    create_time: Optional[datetime] = field(default=None, metadata={'description': 'Timestamp when the user level was created.'})
    created_by: Optional[str] = field(default=None, metadata={'description': 'Identifier for the creator of the user level record.'})
    update_time: Optional[datetime] = field(default=None, metadata={'description': 'Timestamp when the user level record was last updated.'})
    updated_by: Optional[str] = field(default=None, metadata={'description': 'Identifier for who last updated the user level record.'})
    remarks: Optional[str] = field(default=None, metadata={'description': 'Additional remarks or notes about the user level.'})
    del_flag: bool = field(default=False, metadata={'description': 'Flag indicating if the user level is deleted.'})

    def __post_init__(self):
        # 如果没有传入expiration_time，自动设置PLUS用户的过期时间为1个月
        if self.expiration_time is None and self.user_level == 'plus':
            from dateutil.relativedelta import relativedelta
            self.expiration_time = datetime.now() + relativedelta(months=1)
        pass

    @classmethod
    def allowed_user_levels(cls) -> List[str]:
        return ['public', 'free', 'member', 'plus', 'app_admin', 'admin']

    def to_dict(self) -> dict:
        return asdict(self)
    
    def str2int(self) -> dict:
        mapping = {k: v for v, k in enumerate(self.allowed_user_levels())}
        return mapping.get(self.user_level, 0)
    
    @classmethod
    def get_mapping(cls) -> dict:
        return {k: v for v, k in enumerate(cls.allowed_user_levels())}
    
    def to_str(self) -> str:
        return self.user_level.lower()
    
    def str(self) -> str:
        return self.user_level.lower()
    

    @classmethod
    def int2str(cls, user_level: int = 1) -> str:
        allowed_user_levels = UserLevelInfo.allowed_user_levels()
        assert user_level in range(len(allowed_user_levels)), f"Invalid user_level: {user_level}"
        return allowed_user_levels[user_level]
    
    def __str__(self) -> str:
        return str(self.user_level)
    
    def __int__(self) -> int:
        return self.str2int()
    
    def __repr__(self) -> str:
        return f"UserLevelInfo(user_level={self.user_level!r}, id={self.id!r}, expiration_time={self.expiration_time!r}."


@dataclass
class UserInfo:
    id: str = field(default_factory=str, metadata={'description': 'Unique identifier for the user, typically a UUID.'})
    username: Optional[str] = field(default=None, metadata={'description': 'Username of the user.'})
    password: Optional[str] = field(default=None, metadata={'description': 'Password of the user, typically hashed.'})
    user_level: Optional[UserLevelInfo] = field(default=None, metadata={'description': 'User level or role, e.g., admin, user.'})
    user_groups: Optional[List[UserGroupInfo]] = field(default=None, metadata={'description': 'List of user groups that the user belongs to.'})
    phone: Optional[str] = field(default=None, metadata={'description': 'Phone number of the user.'})
    auth_type: Optional[str] = field(default="local", metadata={'description': 'Authentication type for the user, e.g., OAuth, SSO.'})
    create_time: Optional[datetime] = field(default=None, metadata={'description': 'Timestamp when the user was created.'})
    created_by: Optional[str] = field(default=None, metadata={'description': 'Identifier for the creator of the user record.'})
    update_time: Optional[datetime] = field(default=None, metadata={'description': 'Timestamp when the user record was last updated.'})
    updated_by: Optional[str] = field(default=None, metadata={'description': 'Identifier for who last updated the user record.'})
    remarks: Optional[str] = field(default=None, metadata={'description': 'Additional remarks or notes about the user.'})
    del_flag: bool = field(default=False, metadata={'description': 'Flag indicating if the user is deleted.'})
    umt_id: Optional[int] = field(default=None, metadata={'description': 'Foreign key or reference ID for external systems.'})
    email: Optional[str] = field(default=None, metadata={'description': 'Email address of the user.'})
    cluster_uid: Optional[int] = field(default=None, metadata={'description': 'Cluster unique identifier, possibly used in multi-tenant systems.'})
    balance: Optional[float] = field(default=0.0, metadata={'description': 'User balance, possibly for billing or credits.'})

    def __post_init__(self):
        if isinstance(self.id, uuid.UUID):  # 如果id是uuid4类型，转换为str
            self.id = str(self.id)
        # 允许传入user_level为None或str, None时默认为free
        if self.user_level is None:
            self.user_level = 'free'
        if isinstance(self.user_level, str):
            if self.user_level not in UserLevelInfo.allowed_user_levels():
                raise ValueError(f"Invalid user_level: {self.user_level}")
            self.user_level = UserLevelInfo(user_level=self.user_level)
        elif isinstance(self.user_level, dict):
            self.user_level = UserLevelInfo(**self.user_level)
        # 如果未传入，自动设置group为default
        if self.user_groups is None:
            self.user_groups = [UserGroupInfo(name="default")]
        elif isinstance(self.user_groups, list):
            if isinstance(self.user_groups[0], dict):
                self.user_groups = [UserGroupInfo(**group) for group in self.user_groups]
                
            

    def __repr__(self) -> str:
        return f"UserInfo(id={self.id!r}, username={self.username!r}, phone={self.phone!r}, email={self.email!r}, del_flag={self.del_flag!r})"

    def to_dict(self) -> dict:
        return asdict(self)
    
    def group_ids(self) -> List[str]:
        return [group.id for group in self.user_groups]
    
    def group_names(self) -> List[str]:
        return [group.name for group in self.user_groups]
    

@dataclass
class UserDeletedInfo:
    id: str = field(default_factory=str, metadata={'description': 'Unique identifier for the user, typically a UUID.'})
    username: Optional[str] = field(default=None, metadata={'description': 'Username of the user.'})
    deleted: bool = field(default=False, metadata={'description': 'Flag indicating if the user is deleted.'})


@dataclass
class APIKeyInfo:
    id: str = field(default_factory=str, metadata={'description': 'Unique identifier for the API key, typically a UUID.'})
    api_key: str = field(default_factory=str, metadata={'description': 'Value of the API key.'})
    alias: Optional[str] = field(default=None, metadata={'description': 'Alias name for the API key.'})
    user_id: Optional[str] = field(default=None, metadata={'description': 'User ID that the API key belongs to.'})
    username: Optional[str] = field(default=None, metadata={'description': 'Username that the API key belongs to.'})
    expiration_time: Optional[datetime] = field(default=None, metadata={'description': 'Timestamp when the API key expires.'})
    usage_description: Optional[str] = field(default=None, metadata={'description': 'Description of the API key usage.'})
    create_time: Optional[datetime] = field(default=None, metadata={'description': 'Timestamp when the API key was created.'})
    created_by: Optional[str] = field(default=None, metadata={'description': 'Identifier for the creator of the API key record.'})
    update_time: Optional[datetime] = field(default=None, metadata={'description': 'Timestamp when the API key record was last updated.'})
    updated_by: Optional[str] = field(default=None, metadata={'description': 'Identifier for who last updated the API key record.'})
    allowed_models: Optional[Union[str, Dict]] = field(default="all", metadata={'description': 'Allowed models for the API key.'})
    remarks: Optional[str] = field(default=None, metadata={'description': 'Additional remarks or notes about the API key.'})
    app_group: Optional[str] = field(default=None, metadata={'description': 'App group that the API key belongs to.'})
    del_flag: bool = field(default=False, metadata={'description': 'Flag indicating if the API key is deleted.'})
    

    def __post_init__(self):
        if isinstance(self.id, uuid.UUID):
            self.id = str(self.id)

    
    def __repr__(self) -> str:
        return f"APIKeyInfo(id={self.id!r}, alias={self.alias!r}, api_key={self.api_key!r}, user_id={self.user_id!r}, expiration_time={self.expiration_time!r})"

    def to_str(self) -> str:
        return self.api_key

    def to_dict(self) -> dict:
        return asdict(self)
    
@dataclass
class APIKeyDeletedInfo:
    id: str = field(default_factory=str, metadata={'description': 'Unique identifier for the API key, typically a UUID.'})
    api_key: str = field(default_factory=str, metadata={'description': 'Value of the API key.'})
    deleted: bool = field(default=False, metadata={'description': 'Flag indicating if the API key is deleted.'})
    
    def __str__(self) -> str:
        return str(self.api_key)
    
    def __repr__(self) -> str:
        return f"APIKeyDeletedInfo(id={self.id!r}, api_key={self.api_key!r}, deleted={self.deleted!r})"
                
    
    def to_dict(self) -> dict:
        return asdict(self)