import os
from pathlib import Path
from typing import Union
import argparse
from dataclasses import dataclass
import requests
import random
import string
import subprocess
import time
import re
import pwd
import sys


@dataclass
class Config:
    gres: str 
    # not_save_changes: bool
    # partition: str
    # kvm_param: str
    nodes: int = 1
    chdir: str = None
    nodelist: str = None
    exclude: str = None
    job_name: str = "auto"
    time: str = "121m"
    daemon: bool = False
    qos: str = "normal"
    
    def __post_init__(self):
        self._convert_walltime()
        self._auto_job_name()
        
    def _auto_job_name(self):
        """自动生成job_name"""
        if self.job_name.lower() == "auto":
            job_name = f'ecs_'
            # 后面随机四个符号
            for _ in range(4):
                job_name += random.choice(string.ascii_letters).lower()
            self.job_name = job_name  
    
    def _convert_walltime(self):
        """如果time格式是121s, 121m, 121h, 121d, 则转换时间hh:mm:ss格式"""
        if isinstance(self.time, str):
            match = re.match(r'(\d+)([hmd])', self.time)
            if match:
                value, unit = match.groups()
                value = int(value)
                if unit == 'h':
                    # Convert hours to hh:mm:ss format
                    self.time = f"{value:02d}:00:00"
                elif unit == 'm':
                    hours = value // 60
                    minutes = value % 60
                    self.time = f"{hours:02d}:{minutes:02d}:00"
                elif unit == 'd':
                    self.time = f"{value * 24:02d}:00:00"

def parse_args() -> Config:
    parser = argparse.ArgumentParser(description='HepAI ECS command line tool to run virtual machines.')
    parser.add_argument('--gres', type=str, default="gpu:1", help='Generic resource, default is `gpu:1`.')
    parser.add_argument('-N', '--nodes', type=int, default=1, help="Number of nodes.")
    parser.add_argument('-q', '--qos', type=str, default="gpunormal", help="Set Quality of Service")
    parser.add_argument('-J', '--job-name', type=str, default="auto", help="Name of the job.")
    parser.add_argument('-t', '--time', default="121m", help="Walltime of the machine, default is 120 minutes.")
    
    
    # parser.add_argument('--partition', type=str, default="gpu", help="Partition to use, default is `gpu`.")
    # parser.add_argument('--not-save-changes', action='store_true', help="Not save changes of the vitural machine if True, default is False.")
    # parser.add_argument('--kvm-param', type=str, default="auto", help="KVM parameters, format is `num_cores:num_memory`, default is auto.")
    parser.add_argument('--chdir', type=str, help="Change to directory before running job.")
    
    # TODO：设置和排除nodelist
    parser.add_argument('--nodelist', type=str, help="Specifies the list of nodes to use.")
    parser.add_argument('--exclude', type=str, help="Specifies the list of nodes to exclude.")
    parser.add_argument('-d', '--daemon', action='store_true', help="Running in the background, only submitting task")
    

    args = parser.parse_args()
    
    return Config(**args.__dict__)


@dataclass
class NodeResource:
    num_cores: int = 64  # 64 CPU cores
    num_memory: int = 960*0.534  # 960GB
    num_cards: int = 8  # 8 GPUs
    
    
@dataclass
class SubmittedJobInfo:
    """提交作业后返回的信息"""
    jobId: str  #  872
    jobType: str  # enode
    jobPath: str  # '/.xx/Jobs/enode-20250616-211720'
    

@dataclass
class JobStatus:
    """查询后的作业状态"""
    clusterId: str  # slurm
    jobId: str  # 872
    jobStartTime: str  # '2025-06-16 21:17:20'
    jobStatus: str  # 'RUNNING'
    jobNodeList: str  # 'aigpu001'
    jobSubmitTime: str  # '2025-06-16 21:17:20'
    jobType: str  # 'enode'
    connect_sign: str  # 'True

    def __post_init__(self):
        # 将connect_sign转换为布尔值
        if self.connect_sign.lower() == 'true':
            self.connect_sign = True
        elif self.connect_sign.lower() == 'false':
            self.connect_sign = False
        else:
            raise ValueError(f"Invalid connect_sign value: {self.connect_sign}")    
    

@dataclass
class ConnectionInfo:
    """连接信息"""
    host: str
    gateway_port: int
    jobId: int

class AIEmailFetcher:
    
    @staticmethod
    def fetch_email(username: str) -> str:
        resp = requests.get(
            f"https://login.ihep.ac.cn/umt/api/APIafsToemail?afsAccount={username}",
            headers={
                "Content-Type": "application/json",
            }
        )
        try:
            resp.raise_for_status()  # 检查请求是否成功
            resp_json = resp.json()
        except Exception as e:
            raise RuntimeError(f"请求失败: {e}, \n{resp.text}")
        
        ret = resp_json.get("result", [])
        assert len(ret) == 1, f"Expected exactly one result, but got {len(ret)} for user `{username}`."
        
        email = ret[0].get("email", "")
        if not email:
            raise RuntimeError(f"Failed to fetch email for user `{username}`.")
        
        return email
        

class HaiECS:

    def __init__(self, config) -> None:
        self.cfg: Config = config
        
        self.nr = NodeResource()
        
        # 自动获取用户名
        self.username, self.uid = self._get_username()
        self.email = AIEmailFetcher.fetch_email(username=self.username)
        # print(f'Current user: {self.username}, uid: {self.uid}, email: {self.email}')
        
    def _get_username(self):
        """获取当前执行脚本的用户名"""
        user_info = pwd.getpwuid(os.getuid())
        username = user_info.pw_name
        uid = user_info.pw_uid
        if not username:
            raise RuntimeError("Failed to get the current username, please check your environment.")
        return username, uid
        
        
    def _auto_num_cpu_and_memory(self, num_cards: int):
        """根据卡的数量自动设置cpu核数和memory数量"""
        if num_cards > 8:
            raise ValueError(f"Number of cards should be no more than 8, but got {num_cards}")
        assert isinstance(num_cards, int)

        ratio = num_cards / self.nr.num_cards
        n_cores = int(self.nr.num_cores * ratio)
        n_memory = int(self.nr.num_memory * ratio)
        return n_cores, n_memory
        
        
    def poll_job_status(self, job_id: str, interval: int = 1, timeout: int = 10):
        """
        轮询查询作业状态，直到作业结束或超时
        :param job_id: 作业ID
        :param interval: 轮询间隔（秒）
        :param timeout: 超时时间（秒），默认10秒
        :return: 最终的JobStatus对象
        """
        start_time = time.time()
        
        ok_status = ['running']
        error_status = ['failed', 'cancelled', 'timeout']
        
        while True:
            try:
                job_status_list = self.query_user_jobs()
            except Exception as e:
                raise RuntimeError(f"查询作业状态失败: {e}，请联系管理员hepai@ihep.ac.cn")
            job_status = next((js for js in job_status_list if str(js.jobId) == str(job_id)), None)
            if job_status is None:
                # print(f"未找到作业 {job_id}，等待下次查询...")
                print(f"\rWaiting for the job to be running ... {time.time()-start_time:.2f}s.", end="")
            else:
                # print(f"作业 {job_id} 当前状态: {job_status.jobStatus}")
                print(f" Job (id=`{job_id}`) current status: {job_status.jobStatus}")
                if job_status.jobStatus.lower() in ok_status:
                    return job_status
                elif job_status.jobStatus.lower() in ['pending']:
                    pass  # 作业还在等待中，继续轮询
                elif job_status.jobStatus.lower() in error_status:
                    raise RuntimeError(f"作业 {job_id} 失败，状态: {job_status.jobStatus}，请联系管理员")
                else:
                    raise RuntimeError(f"作业 {job_id} 状态异常: {job_status.jobStatus}，请联系管理员")
            if time.time() - start_time > timeout:
                raise TimeoutError(f"轮询作业状态超时（{timeout}秒），作业ID: {job_id}，请联系管理员hepai@ihep.ac.cn")
            time.sleep(interval)

    
    
    def get_conection_info(self, job_id: Union[str, int]) -> ConnectionInfo:
        """
curl -X GET "http://aiweb02.ihep.ac.cn:8001/api/v1/connect-job?jobId=${1}&job_type=${2}&cluster_id=slurm" \
  -H "uid: 21628" \
  -H "email: guocq@ihep.ac.cn"
        """
        
        resp = requests.get(
            f"http://aiweb02.ihep.ac.cn:8001/api/v1/connect-job?jobId={job_id}&job_type=enode&cluster_id=slurm",
            headers={
                "uid": str(self.uid),  # 用户的uid
                "email": str(self.email)  # 用户的邮箱
            }
        )
        try:
            resp.raise_for_status()
            resp_json = resp.json()
        except Exception as e:
            raise RuntimeError(f"请求失败: {e}")
        data = resp_json.get("data", {})
        
        cinfo = ConnectionInfo(**data)
        return cinfo
    
    
    def query_user_jobs(self) -> list[JobStatus]:
        """
       curl -X GET "http://aiweb02.ihep.ac.cn:8001/api/v1/query-job?limit=10&page=1&job_type=all&cluster_id=slurm" \
  -H "Content-Type: application/json" \
  -H "uid: 21628" \
  -H "email: guocq@ihep.ac.cn"
        """
        
        resp = requests.get(
            f"http://aiweb02.ihep.ac.cn:8001/api/v1/query-job?limit=10&page=1&job_type=all&cluster_id=slurm",
            headers={
                "Content-Type": "application/json",
                "uid": str(self.uid),  # 用户的uid
                "email": str(self.email)  # 用户的邮箱
            }
        )
        
        try:
            resp.raise_for_status()
            resp_json = resp.json()
        except Exception as e:
            raise RuntimeError(f"请求失败: {e}, \n{resp.text}")
        data = resp_json.get("data", [])
        
        job_status_list = [JobStatus(**item) for item in data]
        return job_status_list
        
    
    
    def submit_enode_job(self):
        """
#!/bin/bash

curl -X POST "http://aiweb02.ihep.ac.cn:8001/api/v1/create-job?job_type=${1}&cluster_id=slurm" \
  -H "Content-Type: application/json" \
  -H "uid: 21628" \                  // 用户的uid
  -H "email: guocq@ihep.ac.cn" \     // 用户的邮箱
  -d '{
  "job_script": "",             // 空着不写
  "job_parameters": "",         // 空着不写
  "time": "00:30:00",           // 程序最大运行时间
  "partition": "gpu",           // 分区
  "nodes": "1",                 // 1个节点
  "ntasks": "1",                // 1个CPU核
  "mem": "1G",                  // 内存
  "account": "ihepai",          // 用户的组，固定为ihepai
  "qos": "gpunormal",           // QOS
  "gpu_name":"gpu",             // gpu or dcu
  "gpu_num": "1",               // gpu num
  "gpu_type": "",               // gpu 类型 a800 或者 l40 或者 k100ai
  "ntasks_per_node": 1,         // 这个不改
  "job_name": "test"
}'
        """
        
        partition, gpu_num = self.cfg.gres.split(":")
        ncores, n_memory = self._auto_num_cpu_and_memory(int(gpu_num))
        # job_name = self._auto_job_name()
        data = {
            "job_script": "",  # 空着不写
            "job_parameters": "",  # 空着不写
            "time": self.cfg.time,  # 程序最大运行时间
            "partition": partition,  # 分区
            "nodes": str(self.cfg.nodes),  # 节点数
            "ntasks": str(ncores),  # CPU核数
            "mem": f'{n_memory}G',  # 内存
            "account": "ihepai",  # 用户的组，固定为ihepai
            "qos": self.cfg.qos,  # QOS
            "gpu_name": partition,  # gpu or dcu
            "gpu_num": gpu_num,  # gpu num
            "gpu_type": "",  # gpu 类型 a800 或者 l40 或者 k100ai
            "ntasks_per_node": 1,  # 不改
            "job_name": self.cfg.job_name
        }
        
        print(f"""Applying Elastic Cloud Server (ECS) job with the following configuration:
    num_nodes: {self.cfg.nodes}
    cpu cores: {ncores}
    memory: {n_memory}G
    accerlerator_cards: {partition} * {gpu_num}
""")
        
        resp = requests.post(
            "http://aiweb02.ihep.ac.cn:8001/api/v1/create-job?job_type=enode&cluster_id=slurm",
            headers={
                "Content-Type": "application/json",
                "uid": str(self.uid),  # 用户的uid
                "email": str(self.email)  # 用户的邮箱
            },
            json=data
        )
        # 检查resp是否成功，失败报错
        try:
            resp.raise_for_status()
            resp_json = resp.json()
        except Exception as e:
            raise RuntimeError(f"请求失败: {e}")
        
        data = resp_json.get("data", {})
        job_info = SubmittedJobInfo(**data)
        
        print(f"Job submitted, job_id: `{job_info.jobId}`")
        return job_info
    
    
    def check_existing_job(self):
        """
        检查是已经有enode作业在运行，如果有则提示用户
        """
        user_jobs = self.query_user_jobs()
        enode_jobs = [job for job in user_jobs if job.jobType.lower() == 'enode']
        if len(enode_jobs) >= 1:
            task_or_tasks = "task" if len(enode_jobs) == 1 else "tasks"
            print(f"""You already have {len(enode_jobs)} ECS {task_or_tasks} running. 
Check command: 
    `squeue` to view, 
    `scancel <job_id>` to cancel.""")
            return enode_jobs
        return None
        
    def __call__(self):
        
        enode_jobs = self.check_existing_job()
        if enode_jobs is not None:
            # 筛选正在running的作业
            enode_jobs = [job for job in enode_jobs if job.jobStatus.lower() == 'running']
            connection_info = self.get_conection_info(job_id=enode_jobs[0].jobId)
            print(f"""
The running ECS job id is `{connection_info.jobId}`, jobNodelist: `{enode_jobs[0].jobNodeList}`.
ECS information:
    HostName: {connection_info.host}
    User: {self.username}
    Port: {connection_info.gateway_port}
    
    You can connect to it via: `ssh -o UserKnownHostsFile=/dev/null {self.username}@{connection_info.host} -p {connection_info.gateway_port}`""")
            exit(0)  # 如果有正在运行的作业，则直接退出
        
        job_info = self.submit_enode_job()
        # 轮询作业状态
        time.sleep(0.5)  
        final_status = self.poll_job_status(job_info.jobId)
        # if final_status.jobStatus.lower() != 'running':
        #     raise RuntimeError(f"作业 {job_info.jobId} 状态异常: {final_status.jobStatus}，请联系管理员")
        
        
        connection_info = self.get_conection_info(job_id=job_info.jobId)
        print(f"""
The ECS is ready!
    HostName: {connection_info.host}
    User: {self.username}
    Port: {connection_info.gateway_port}
    
    For more information, please visit: `https://ai.ihep.ac.cn/docs`
    You can connect to it via: `ssh -o UserKnownHostsFile=/dev/null {self.username}@{connection_info.host} -p {connection_info.gateway_port}`
    """)
        return connection_info
 
        


if __name__ == "__main__":
    args = parse_args()
    # 执行创建或管理VM的逻辑
    hai_ecs = HaiECS(args)
    
    hai_ecs()