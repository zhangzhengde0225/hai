#!/usr/bin/env python3
"""
高并发测试程序 - 支持stream和非stream模式
测试首次token返回时间和完成所有任务的时间
"""

import os
import sys
import asyncio
import time
import logging
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Optional
from argparse import ArgumentParser

# 添加项目路径
here = Path(__file__).parent
sys.path.insert(0, str(here.parent.parent.parent))

from dotenv import load_dotenv
load_dotenv(f'{here.parent.parent.parent.parent}/.env')

from hepai import HepAI, AsyncHepAI
from hepai.types import ChatCompletion, Stream, ChatCompletionChunk

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zhizz_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """单次测试结果"""
    duration: float
    first_token_time: Optional[float]
    token_count: int
    status: str
    reasoning_content: str = ""


class ZhizzConcurrencyTester:
    """Zhizz高并发测试器"""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.results: List[TestResult] = []
        
    def _make_sync_request(self, question: str, stream: bool = True) -> TestResult:
        """同步请求"""
        client = HepAI(base_url=self.base_url, api_key=self.api_key)
        start_time = time.perf_counter()
        first_token_time = None
        token_count = 0
        status = "success"
        reasoning_content = ""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": question}],
                stream=stream,
            )
            
            if stream:
                reasoning_flag = True
                for chunk in response:
                    chunk: ChatCompletionChunk = chunk
                    
                    if chunk is None:
                        continue
                        
                    # 记录首次token时间
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                    
                    # 处理reasoning内容
                    if reasoning_flag:
                        if not chunk.choices:
                            continue
                        reasoning_text = chunk.choices[0].delta.model_extra.get("reasoning_content", None)
                        if reasoning_text:
                            reasoning_content += reasoning_text
                            continue
                        if chunk.choices[0].delta.content == "\n\n":
                            reasoning_flag = False
                            continue
                    
                    # 处理正常内容
                    content = chunk.choices[0].delta.content
                    if content:
                        token_count += 1
            else:
                # 非stream模式
                result: ChatCompletion = response
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                token_count = len(result.choices[0].message.content.split()) if result.choices[0].message.content else 0
                
        except Exception as e:
            status = f"error: {str(e)}"
            logger.error(f"Request failed: {e}")
            
        end_time = time.perf_counter()
        duration = end_time - start_time
        ttft = first_token_time - start_time if first_token_time else None
        
        return TestResult(
            duration=duration,
            first_token_time=ttft,
            token_count=token_count,
            status=status,
            reasoning_content=reasoning_content[:100] + "..." if len(reasoning_content) > 100 else reasoning_content
        )
    
    async def _make_async_request(self, question: str, stream: bool = True) -> TestResult:
        """异步请求"""
        client = AsyncHepAI(base_url=self.base_url, api_key=self.api_key)
        start_time = time.perf_counter()
        first_token_time = None
        token_count = 0
        status = "success"
        reasoning_content = ""
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": question}],
                stream=stream,
            )
            
            if stream:
                reasoning_flag = True
                async for chunk in response:
                    chunk: ChatCompletionChunk = chunk
                    
                    if chunk is None:
                        continue
                        
                    # 记录首次token时间
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                    
                    # 处理reasoning内容
                    if reasoning_flag:
                        if not chunk.choices:
                            continue
                        reasoning_text = chunk.choices[0].delta.model_extra.get("reasoning_content", None)
                        if reasoning_text:
                            reasoning_content += reasoning_text
                            continue
                        if chunk.choices[0].delta.content == "\n\n":
                            reasoning_flag = False
                            continue
                    
                    # 处理正常内容
                    content = chunk.choices[0].delta.content
                    if content:
                        token_count += 1
            else:
                # 非stream模式
                result: ChatCompletion = response
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                token_count = len(result.choices[0].message.content.split()) if result.choices[0].message.content else 0
                
        except Exception as e:
            status = f"error: {str(e)}"
            logger.error(f"Async request failed: {e}")
        finally:
            await client.close()
            
        end_time = time.perf_counter()
        duration = end_time - start_time
        ttft = first_token_time - start_time if first_token_time else None
        
        return TestResult(
            duration=duration,
            first_token_time=ttft,
            token_count=token_count,
            status=status,
            reasoning_content=reasoning_content[:100] + "..." if len(reasoning_content) > 100 else reasoning_content
        )
    
    def run_sync_test(self, question: str, concurrency: int, total_requests: int, stream: bool = True):
        """同步模式测试"""
        logger.info(f"开始同步测试 - 并发数: {concurrency}, 请求数: {total_requests}, Stream: {stream}")
        
        start_time = time.perf_counter()
        results = []
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            # 提交所有任务
            futures = [executor.submit(self._make_sync_request, question, stream) 
                      for _ in range(total_requests)]
            
            # 收集结果
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Task failed: {e}")
        
        total_time = time.perf_counter() - start_time
        self.results = results
        self._print_results("Sync", concurrency, total_requests, total_time, stream)
    
    async def run_async_test(self, question: str, concurrency: int, total_requests: int, stream: bool = True):
        """异步模式测试"""
        logger.info(f"开始异步测试 - 并发数: {concurrency}, 请求数: {total_requests}, Stream: {stream}")
        
        start_time = time.perf_counter()
        semaphore = asyncio.Semaphore(concurrency)
        
        async def bounded_request():
            async with semaphore:
                return await self._make_async_request(question, stream)
        
        # 执行所有请求
        tasks = [bounded_request() for _ in range(total_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤异常结果
        valid_results = [r for r in results if isinstance(r, TestResult)]
        
        total_time = time.perf_counter() - start_time
        self.results = valid_results
        self._print_results("Async", concurrency, total_requests, total_time, stream)
    
    def _print_results(self, mode: str, concurrency: int, total_requests: int, total_time: float, stream: bool):
        """打印测试结果"""
        if not self.results:
            logger.error("没有有效的测试结果")
            return
            
        successful = [r for r in self.results if r.status == "success"]
        failed = len(self.results) - len(successful)
        
        if not successful:
            logger.error("所有请求都失败了")
            return
        
        # 计算统计数据
        durations = [r.duration for r in successful]
        first_token_times = [r.first_token_time for r in successful if r.first_token_time is not None]
        token_counts = [r.token_count for r in successful]
        
        # 延迟统计
        avg_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)  # P50
        p95_duration = statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations)
        p99_duration = statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else max(durations)
        
        # TTFT统计
        avg_ttft = statistics.mean(first_token_times) if first_token_times else 0
        median_ttft = statistics.median(first_token_times) if first_token_times else 0  # P50
        p95_ttft = statistics.quantiles(first_token_times, n=20)[18] if len(first_token_times) >= 20 else max(first_token_times) if first_token_times else 0
        p99_ttft = statistics.quantiles(first_token_times, n=100)[98] if len(first_token_times) >= 100 else max(first_token_times) if first_token_times else 0
        
        # Token统计
        avg_tokens = statistics.mean(token_counts) if token_counts else 0
        total_tokens = sum(token_counts)
        
        # 吞吐量和并发指标
        qps = len(successful) / total_time if total_time > 0 else 0  # 每秒请求数
        tps = total_tokens / total_time if total_time > 0 else 0  # 每秒Token数
        concurrent_qps = len(successful) * concurrency / total_time if total_time > 0 else 0  # 并发QPS
        
        # 错误率
        error_rate = (failed / total_requests) * 100 if total_requests > 0 else 0
        success_rate = (len(successful) / total_requests) * 100 if total_requests > 0 else 0
        
        # 打印详细报告
        report = f"""
========== 测试结果报告 ==========
模式: {mode} (Stream: {stream})
并发数: {concurrency}
总请求数: {total_requests}
成功请求数: {len(successful)}
失败请求数: {failed}
成功率: {success_rate:.2f}%
错误率: {error_rate:.2f}%
总耗时: {total_time:.2f}s

========== 吞吐量指标 ==========
QPS (每秒处理请求数): {qps:.2f}
TPS (每秒输出Token数): {tps:.2f}
并发有效QPS: {concurrent_qps:.2f}

========== 延迟统计 ==========
平均响应时间: {avg_duration:.3f}s
P50响应时间: {median_duration:.3f}s
P95响应时间: {p95_duration:.3f}s
P99响应时间: {p99_duration:.3f}s

========== 首次Token时间 (TTFT) ==========
平均TTFT: {avg_ttft:.3f}s
P50 TTFT: {median_ttft:.3f}s
P95 TTFT: {p95_ttft:.3f}s
P99 TTFT: {p99_ttft:.3f}s

========== Token统计 ==========
平均Token数: {avg_tokens:.1f}
总Token数: {total_tokens}
Token生成速率: {tps:.2f} tokens/s

========== Reasoning示例 =========="""
        
        # 显示一些reasoning内容示例
        reasoning_examples = [r.reasoning_content for r in successful[:3] if r.reasoning_content]
        for i, example in enumerate(reasoning_examples, 1):
            report += f"\n示例{i}: {example}"
        
        logger.info(report)


def main():
    parser = ArgumentParser(description="Zhizz高并发测试程序")
    parser.add_argument('--concurrency', type=int, default=24, help='并发数 (默认: 5)')
    parser.add_argument('--requests', type=int, default=24, help='总请求数 (默认: 20)')
    parser.add_argument('--model', type=str, default='deepseek-v3', help='模型名称')
    parser.add_argument('--base-url', type=str, default='https://api.zhizengzeng.com/v1', help='API基础URL')
    parser.add_argument('--api-key', type=str, help='API密钥 (可通过DDF_ZDZHANG_API_KEY环境变量设置)')
    # parser.add_argument('--question', type=str, default='解释一下量子纠缠的基本原理', help='测试问题')
    parser.add_argument('--question', type=str, default='Hello', help='测试问题')
    
    parser.add_argument('--mode', choices=['sync', 'async', 'both'], default='sync', help='测试模式')
    parser.add_argument('--no-stream', action='store_true', help='禁用流模式')
    parser.add_argument('--stream-only', action='store_true', help='仅测试流模式')
    
    args = parser.parse_args()
    
    # 获取API密钥
    api_key = args.api_key or os.getenv("ZHIZENGZENG_API_KEY")
    if not api_key:
        logger.error("请提供API密钥 (--api-key 或设置 ZHIZENGZENG_API_KEY 环境变量)")
        return
    
    # 创建测试器
    tester = ZhizzConcurrencyTester(
        base_url=args.base_url,
        api_key=api_key,
        model=args.model
    )
    
    # 决定测试的stream模式
    stream_modes = []
    if args.stream_only:
        stream_modes = [True]
    elif args.no_stream:
        stream_modes = [False]
    else:
        stream_modes = [True, False]
        
    # stream_modes = [False]
    stream_modes = [True]
    
    # 运行测试
    for stream in stream_modes:
        print(f"\n{'='*50}")
        print(f"测试配置: Stream={stream}")
        print(f"{'='*50}")
        
        if args.mode in ['sync', 'both']:
            tester.run_sync_test(
                question=args.question,
                concurrency=args.concurrency,
                total_requests=args.requests,
                stream=stream
            )
            time.sleep(2)  # 间隔一下
        
        if args.mode in ['async', 'both']:
            asyncio.run(tester.run_async_test(
                question=args.question,
                concurrency=args.concurrency,
                total_requests=args.requests,
                stream=stream
            ))
            time.sleep(2)  # 间隔一下


if __name__ == "__main__":
    main()