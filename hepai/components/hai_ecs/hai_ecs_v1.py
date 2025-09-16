import os
from pathlib import Path
import argparse
from dataclasses import dataclass
import random
import string
import subprocess
import time
import re


def parse_args():
    parser = argparse.ArgumentParser(description='HepAI ECS command line tool to run virtual machines.')
    parser.add_argument('--gres', type=str, default="vgpu:1", help='Generic resource, default is `vgpu:1`.')
    parser.add_argument('--kvm-name', type=str, default="almalinux9.5", help='Name of the KVM configuration, default is `almalinux9.5`.')
    parser.add_argument('--not-save-changes', action='store_true', help="Not save changes of the vitural machine if True, default is False.")
    parser.add_argument('--partition', type=str, default="vgpu", help="Partition to use, default is `vgpu`.")
    parser.add_argument('--kvm-param', type=str, default="auto", help="KVM parameters, format is `num_cores:num_memory`, default is auto.")
    parser.add_argument('-N', '--nodes', type=int, default=1, help="Number of nodes.")
    parser.add_argument('--chdir', type=str, help="Change to directory before running job.")
    parser.add_argument('--nodelist', type=str, help="Specifies the list of nodes to use.")
    parser.add_argument('--exclude', type=str, help="Specifies the list of nodes to exclude.")
    parser.add_argument('-J', '--job-name', type=str, default="auto", help="Name of the job.")
    parser.add_argument('-t', '--time', default="121m", help="Walltime of the machine, default is 120 minutes.")
    parser.add_argument('-d', '--daemon', action='store_true', help="Running in the background, only submitting task")
    parser.add_argument('-q', '--qos', type=str, default="normal", help="Set Quality of Service")

    args = parser.parse_args()

    return args


@dataclass
class NodeResource:
    num_cores: int = 64  # 64 CPU cores
    num_memory: int = 960*0.534  # 960GB
    num_cards: int = 8  # 8 GPUs


class HaiECS:

    def __init__(self, args):
        self.args = args
        self.nr = NodeResource()
        self.run_dir = f"{Path.home()}/VMSTORE"  # 这个决定slrun-xx.out的输出目录



    def check_kvm_name(self, name: str):
        """检查kvm_name对应的镜像是否存在，如果不存在就报错"""
        images_dir = f"{Path.home()}/IMAGES"
        tips = f"Image `{name}` not found, usually it is being configured, please wait or contact helpdesk.ihep.ac.cn."
        if not os.path.exists(images_dir):
            # raise ValueError(f"IMAGES directory not found in {images_dir}.")
            raise ValueError(tips)
        # 检查后缀为.qcow2的文件
        exist_images = [x[:-6] for x in os.listdir(images_dir) if x.endswith(".qcow2")]
        if name not in exist_images:
            # 自动申请创建镜像
            # raise ValueError(f"KVM image `{name}` not found in {images_dir}.")
            raise ValueError(tips)
        print(f"KVM image `{name}` found in {images_dir}.")

        pass

    def ensure_sleep_sh(self, time: str):
        """创建sleep.sh文件，用于指定多少时间后关闭虚拟机"""
        sh_content = """
#!/bin/bash

JOBID=
disk_id=$(ls -1 /dev/disk/by-id| grep -i "virtio-JOBID-" | head -n1)
if [[ $disk_id =~ virtio-JOBID-([0-9]+)_([0-9]+) ]]; then
        JOBID=${BASH_REMATCH[1]}
        MPI=${BASH_REMATCH[2]}
fi
echo "ECS is ready" > /mnt/VMSTORE/ok.finish.${JOBID}

"""
        sh_content += f"sleep {time}\n"


        home = Path.home()
        file_path = f'{home}/VMSTORE/sleep_{time}.sh'
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(sh_content)
            # chmod +x
            os.system(f"chmod +x {file_path}")
        return file_path

    def auto_num_cpu_and_memory(self, num_cards: int):
        """根据卡的数量自动设置cpu核数和memory数量"""
        if num_cards > 8:
            raise ValueError(f"Number of cards should be no more than 8, but got {num_cards}")
        assert isinstance(num_cards, int)

        ratio = num_cards / self.nr.num_cards
        n_cores = int(self.nr.num_cores * ratio)
        n_memory = int(self.nr.num_memory * ratio)
        return n_cores, n_memory
    
    
    def auto_job_name(self):
        """自动生成job_name"""
        job_name = f'ecs_'
        # 后面随机四个符号
        for _ in range(4):
            job_name += random.choice(string.ascii_letters).lower()
        return job_name

    def get_sbatch_vm_cmd(self):
        """从args中获取sbatch-vm的命令"""
        args = self.args
        cmd = "sbatch-vm"
        if args.kvm_name:
            self.check_kvm_name(args.kvm_name)  # 检查kvm镜像是否存在
            cmd += f" --kvm-name={args.kvm_name}"

        if args.not_save_changes:
            pass
        else:
            cmd += f" --kvm-edit"  # 需要保存是，设置--kvm-edit

        if args.gres:
            """转换slurm的gres为vslurm的gres"""
            card_type, num_cards = args.gres.split(":")
            if "gpu" in card_type:
                card_type = "vfiogpu"
            elif "dcu" in card_type:
                card_type = "vfiodcu"
            else:
                raise ValueError(f"Unknown gpu/duc card type: {card_type}")
            cmd += f" --gres={card_type}:{num_cards}"

            # 进一步根据卡的数量自动设置cpu核数和memory数量
            if args.kvm_param == "auto":
                num_cores, num_memory = self.auto_num_cpu_and_memory(int(num_cards))
            else:
                num_cores, num_memory = args.kvm_param.split(":")
            cmd += f" --kvm-param={num_cores}:{num_memory}"


        if args.partition:
            cmd += f" --partition={args.partition}"

        if args.nodes:
            cmd += f" --nodes={args.nodes}"

        if args.chdir:
            cmd += f" --chdir={args.chdir}"

        if args.nodelist:
            cmd += f" --nodelist={args.nodelist}"

        if args.exclude:
            cmd += f" --exclude={args.exclude}"

        if args.job_name:
            if args.job_name == "auto":
                args.job_name = self.auto_job_name()

            cmd += f" --job-name={args.job_name}"

        if args.time:
            sleep_file = self.ensure_sleep_sh(args.time)
            cmd += f" {sleep_file}"

        if args.qos:
            cmd += f" --qos={args.qos}"

        cmd += f" --account=ihepai"

        return cmd
    
    
    def run_command(self, command, verbose=True, ignore_error=False):
        try:
            # 通过 subprocess.run 执行命令并获取输出
            if verbose:
                print(f"Run command: {command}")
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            # result.stdout 包含命令的标准输出结果

            stdout = result.stdout

            # 可选：result.stderr 也可以获取标准错误输出
            if result.stderr:
                # print("Command Error:")
                # print(result.stderr)
                raise ValueError(f"An error occurred while executing the command: \n{result.stderr}")
            if verbose:
                print(stdout)
            return stdout

        except subprocess.CalledProcessError as e:
            ##在异常中同时打印 stdout 和 stderr
            if verbose:
                print(f"Failed to excute command: {command}")
                print("Standard Output:")
                print(e.stdout)  # 如果可能，还有成功部分的输出
                print("Standard Error:")
                print(e.stderr)  # 打印错误输出
                if "There is a task with '--kvm-edit' parameter" in str(e.stdout):
                    print(f'You already have another editable ECS running. Please use `scancel <job_id>` to terminate it before attempting to start a new ECS. Alternatively, you can set `--not-save-changes` to disable editable mode and run multiple ECS instances.')
            if ignore_error:  # 忽略错误时，不会退出
                return
            else:
                exit(1)  # 退出脚本以指示失败

    def extract_job_id(self, stdout):
        """
        从命令的输出中提取job_id
        如：Command Output:
currentpath=/aifs/user/home/zdzhang/scripts
userhome=/aifs/user/home/zdzhang
numberOfJob=0, maxNumberOfJob=3
sbatch --gres=vfiogpu:1,vfioeth:1 --kvm-param=8:120 --partition=vgpu --nodes=1 --job-name=ecs_uxra /aifs/user/home/zdzhang/VMSTORE/SBATCH/S26658
Submitted batch job 63
        """
        lines = stdout.split("\n")
        for line in lines:
            if "Submitted batch job" in line:
                job_id = line.split(" ")[-1]
                return job_id
        print("Job ID not found.")
        return None

    def get_hostnames_and_ips(self, job_id):
        showip_rst = self.run_command(f"showip {job_id}", verbose=False, ignore_error=True)

        if not showip_rst:
            return None, None

        # 从如下内容中提取ip
        """
        aigpu001, IP: (0, '10.5.6.122', '10.249.6.122', 'aa:0a:05:06:0b:02', 0)
        aigpu002, IP: (0, '10.5.6.130', '10.249.6.130', 'aa:0a:05:06:0c:00', 1)
        """
        # 仅仅提取出10.5.6.122和10.5.6.130
        # pattern = r"(\w+), IP: \(.*?'(10\.\d+\.\d+\.\d+)"
        pattern = r"(\w+), IP: \((.*?)\)"

        # 匹配结果
        matches = re.findall(pattern, showip_rst)

        # 如果找到了IP地址，即返回第一个匹配的IP地址
        if matches:
            hostnames = []
            ips = []
            for match in matches:
                hostname = match[0]
                _, ip, ip2, mac, id_ = eval(match[1])
                hostnames.append(f'{hostname}-{id_}')
                ips.append(ip)
            # print(f"showip_rst: {showip_rst}")
            # print(f"matches: {matches}")
            # print(f"hostnames: {hostnames}")
            # print(f"ips: {ips}")
            return hostnames, ips
        else:
            return None, None

    def check_ecs_is_ready(self, job_id: str):
        ok_file_path = f'{Path.home()}/VMSTORE/ok.finish.{job_id}'
        if os.path.exists(ok_file_path):
            return True
        return False
    
    def polling_result(self, job_id, t0):
        ips = None
        # ping_result = None

        actual_check_interval = 5  # 实际检查间隔
        last_check_time = time.time() - actual_check_interval - 2  # 上次检查时间
        timeout, noticed = 180, False  # 超时时间，等待时候过长时，提醒用户可以按Ctrl+C退出，并hai-ecs -d重新提交任务到后台
        while True:
            """改成每0.2s打印一次，但实际检查5秒一次"""
            if time.time() - last_check_time > actual_check_interval:
                hostnames, ips = self.get_hostnames_and_ips(job_id)
                # 已经有ip，还需要通过ping来判断是否已经启动
                is_ready = self.check_ecs_is_ready(job_id=job_id)
                # if ping_result:
                if is_ready:
                    print("\n")
                    break
                last_check_time = time.time()
            time.sleep(1)
            show_str = f'\rECS is starting up {time.time()-t0:.2f}s (about 1~3 minutes), ip={ips}.'
            print(show_str, end="")
            if time.time() - t0 > timeout and not noticed:
                print("\n")
                print(f"Notice: ECS creation is taking longer than expected. You can press Ctrl+C to exit and run `hai-ecs -d` to submit the task in the background.")
                noticed = True
        return hostnames, ips

    def __call__(self):
        cdir = os.getcwd()

        sbatch_vm_cmd = self.get_sbatch_vm_cmd()
        # 执行命令
        os.chdir(self.run_dir)
        stdout = self.run_command(sbatch_vm_cmd)
        job_id = self.extract_job_id(stdout)
        if self.args.daemon:
            lines = [f"ECS task is submitted."]
            lines += [f"    job_id: {job_id}."]
            lines += [f"    run `showip {job_id}` to get the ip address."]
            lines += [f"    run `scancel {job_id}` to cancel the job."]
            lines += [f"    run `squeue` to check all jobs."]
            lines += [f"    run `ssh root@<ip>` to connect to the ECS."]
            self.print_lines(lines)
            # print(f"Job {job_id} is submitted.")
            return
        if job_id:
            try:
                t0 = time.time()
                hostnames, ips = self.polling_result(job_id=job_id, t0=t0)
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt: ECS creation is interrupted.")
                #self.run_command(f"scancel {job_id}")
                print(f"You can run `squeue-vm` to show the task information or run `hai-ecs -d` to submit a task in the background.")
                exit(1)

        prt_data = {
            "job_id": job_id,
            "startup_time": f"{time.time()-t0:.2f}s",
            "max_walltime": self.args.time,
            "hostname": hostnames[0] if len(hostnames) == 1 else hostnames,
            "ip": ips[0] if len(ips) == 1 else ips,
        }

        max_key_len = max([len(k) for k in prt_data.keys()])

        lines = [f"ECS is ready! "]
        lines += [f"    {k:<{max_key_len}} : {v}" for k, v in prt_data.items()]
        # lines += [f"You can now connect to it via: `ssh root@{ip}`.",]
        for hostname, ip in zip(hostnames, ips):
            lines += [f"    run `ssh root@{ip}` to access `{hostname}`."]

        self.print_lines(lines)

    def print_lines(self, lines):
        max_len = max([len(line) for line in lines])
        print(f"#--{'-'*max_len}--#")
        for line in lines:
            print(f'#  {line:<{max_len}}  #')
        print(f"#--{'-'*max_len}--#")


if __name__ == '__main__':
    args = parse_args()
    # 执行创建或管理VM的逻辑
    hai_ecs = HaiECS(args)
    hai_ecs()