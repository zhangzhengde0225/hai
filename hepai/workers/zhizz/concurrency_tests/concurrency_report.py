#!/usr/bin/env python3
"""
并发性能报告生成器
支持多种并发量测试、真实负载模拟、弹性测试
"""

import os
import sys
import asyncio
import time
import json
import random
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
from datetime import datetime

here = Path(__file__).parent
sys.path.insert(0, str(here))

from concurrency_tester import ZhizzConcurrencyTester, TestResult


@dataclass
class ConcurrencyTestConfig:
    """并发测试配置"""
    concurrency: int
    total_requests: int
    stream: bool = True
    mode: str = "async"  # sync, async


@dataclass
class LoadTestResult:
    """负载测试结果"""
    config: ConcurrencyTestConfig
    results: List[TestResult]
    total_time: float
    qps: float
    success_rate: float
    avg_response_time: float
    p95_response_time: float
    avg_ttft: float
    p95_ttft: float
    error_count: int
    timestamp: str


class ConcurrencyReportGenerator:
    """并发报告生成器"""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.tester = ZhizzConcurrencyTester(base_url, api_key, model)
        self.test_results: List[LoadTestResult] = []
        
    def _generate_realistic_questions(self) -> List[str]:
        """生成不同复杂度的问题，模拟真实负载"""
        questions = [
            # 短问题 (预期输出 50-100 tokens)
            "Hello",
            "What is 2+2?",
            "Define AI in one sentence.",
            "Name three colors.",
            "What day is today?",
            
            # 中等问题 (预期输出 100-300 tokens)
            "Explain the concept of machine learning in simple terms.",
            "What are the advantages and disadvantages of renewable energy?",
            "Describe the process of photosynthesis.",
            "Compare Python and JavaScript programming languages.",
            "What is the difference between AI and ML?",
            
            # 长问题 (预期输出 300-600 tokens)
            "Explain quantum computing, its principles, current applications, and potential future impact on technology and society.",
            "Analyze the economic implications of artificial intelligence on job markets, including both positive and negative effects.",
            "Describe the history and evolution of the internet from its inception to modern times, including key milestones.",
            "Compare different machine learning algorithms (supervised, unsupervised, reinforcement learning) with examples.",
            "Explain climate change causes, effects, and potential solutions from both technological and policy perspectives.",
            
            # 复杂问题 (预期输出 500+ tokens)
            "Design a comprehensive strategy for a startup to enter the competitive e-commerce market, including market analysis, technology stack, marketing approach, and financial projections.",
            "Analyze the ethical implications of AI in healthcare, including privacy concerns, bias in algorithms, decision-making transparency, and regulatory challenges.",
            "Create a detailed plan for transitioning a traditional company to digital transformation, covering technology, culture, processes, and change management.",
            "Explain the principles of distributed systems, including consensus algorithms, fault tolerance, scalability patterns, and trade-offs in CAP theorem.",
        ]
        return questions
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * percentile / 100
        f = int(k)
        c = k - f
        if f == len(sorted_values) - 1:
            return sorted_values[f]
        return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c
    
    async def run_single_test(self, config: ConcurrencyTestConfig, question: str) -> LoadTestResult:
        """运行单次测试"""
        print(f"Running test: concurrency={config.concurrency}, requests={config.total_requests}, stream={config.stream}")
        
        start_time = time.perf_counter()
        
        if config.mode == "async":
            await self.tester.run_async_test(question, config.concurrency, config.total_requests, config.stream)
        else:
            self.tester.run_sync_test(question, config.concurrency, config.total_requests, config.stream)
            
        total_time = time.perf_counter() - start_time
        results = self.tester.results
        
        # 计算统计指标
        successful = [r for r in results if r.status == "success"]
        error_count = len(results) - len(successful)
        success_rate = len(successful) / len(results) * 100 if results else 0
        qps = len(successful) / total_time if total_time > 0 else 0
        
        if successful:
            durations = [r.duration for r in successful]
            ttfts = [r.first_token_time for r in successful if r.first_token_time is not None]
            
            avg_response_time = sum(durations) / len(durations)
            p95_response_time = self._calculate_percentile(durations, 95)
            avg_ttft = sum(ttfts) / len(ttfts) if ttfts else 0
            p95_ttft = self._calculate_percentile(ttfts, 95)
        else:
            avg_response_time = p95_response_time = avg_ttft = p95_ttft = 0
            
        return LoadTestResult(
            config=config,
            results=results,
            total_time=total_time,
            qps=qps,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            avg_ttft=avg_ttft,
            p95_ttft=p95_ttft,
            error_count=error_count,
            timestamp=datetime.now().isoformat()
        )
    
    async def run_predefined_concurrency_tests(self) -> List[LoadTestResult]:
        """运行预定义的并发量测试 (10, 50, 100, 200)"""
        concurrency_levels = [10, 50, 100, 200]
        questions = self._generate_realistic_questions()
        results = []
        
        print(f"Starting predefined concurrency tests with levels: {concurrency_levels}")
        
        for concurrency in concurrency_levels:
            # 根据并发量调整请求数，保持合理的测试时间
            total_requests = max(concurrency * 2, 20)  # 至少20个请求
            
            # 随机选择问题类型以模拟真实负载
            question = random.choice(questions)
            
            config = ConcurrencyTestConfig(
                concurrency=concurrency,
                total_requests=total_requests,
                stream=True,
                mode="async"
            )
            
            try:
                result = await self.run_single_test(config, question)
                results.append(result)
                self.test_results.append(result)
                
                print(f"✓ Completed concurrency {concurrency}: QPS={result.qps:.2f}, Success Rate={result.success_rate:.1f}%")
                
                # 休息一下避免服务器过载
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"✗ Failed concurrency {concurrency}: {e}")
                
        return results
    
    async def run_elastic_test(self, start_concurrency: int = 5, max_concurrency: int = 300, 
                              step_size: int = 10, success_threshold: float = 95.0,
                              max_response_time: float = 30.0) -> List[LoadTestResult]:
        """弹性测试 - 逐步提升并发直到系统瓶颈"""
        print(f"Starting elastic test: {start_concurrency} -> {max_concurrency} (step: {step_size})")
        
        results = []
        current_concurrency = start_concurrency
        questions = self._generate_realistic_questions()
        
        while current_concurrency <= max_concurrency:
            # 随机选择中等复杂度的问题
            medium_questions = questions[5:10]  # 中等问题
            question = random.choice(medium_questions)
            
            total_requests = max(current_concurrency * 2, 20)
            config = ConcurrencyTestConfig(
                concurrency=current_concurrency,
                total_requests=total_requests,
                stream=True,
                mode="async"
            )
            
            try:
                result = await self.run_single_test(config, question)
                results.append(result)
                self.test_results.append(result)
                
                print(f"Concurrency {current_concurrency}: QPS={result.qps:.2f}, "
                      f"Success={result.success_rate:.1f}%, "
                      f"P95 Response={result.p95_response_time:.2f}s")
                
                # 检查是否达到瓶颈
                bottleneck_detected = False
                
                if result.success_rate < success_threshold:
                    print(f"⚠ Bottleneck detected: Success rate ({result.success_rate:.1f}%) below threshold ({success_threshold}%)")
                    bottleneck_detected = True
                    
                if result.p95_response_time > max_response_time:
                    print(f"⚠ Bottleneck detected: P95 response time ({result.p95_response_time:.2f}s) exceeds threshold ({max_response_time}s)")
                    bottleneck_detected = True
                
                if bottleneck_detected:
                    print(f"🚨 System bottleneck reached at concurrency {current_concurrency}")
                    break
                    
            except Exception as e:
                print(f"✗ Failed at concurrency {current_concurrency}: {e}")
                break
                
            current_concurrency += step_size
            await asyncio.sleep(3)  # 更长的休息时间
            
        return results
    
    async def run_load_variation_test(self) -> List[LoadTestResult]:
        """负载变化测试 - 测试不同输入输出长度下的性能"""
        print("Starting load variation test...")
        
        questions = self._generate_realistic_questions()
        question_types = [
            ("short", questions[:5], "短问题"),
            ("medium", questions[5:10], "中等问题"), 
            ("long", questions[10:15], "长问题"),
            ("complex", questions[15:], "复杂问题")
        ]
        
        results = []
        fixed_concurrency = 50  # 固定并发量
        
        for q_type, q_list, description in question_types:
            print(f"\nTesting {description} ({q_type})...")
            
            for question in q_list[:2]:  # 每类测试2个问题
                config = ConcurrencyTestConfig(
                    concurrency=fixed_concurrency,
                    total_requests=fixed_concurrency * 2,
                    stream=True,
                    mode="async"
                )
                
                try:
                    result = await self.run_single_test(config, question[:50] + "...")  # 截断显示
                    results.append(result)
                    self.test_results.append(result)
                    
                    avg_tokens = sum(r.token_count for r in result.results if r.status == "success") / len([r for r in result.results if r.status == "success"]) if any(r.status == "success" for r in result.results) else 0
                    print(f"  {description}: QPS={result.qps:.2f}, Avg Tokens={avg_tokens:.1f}")
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"✗ Failed {description}: {e}")
                    
        return results
    
    def generate_report(self, output_file: str = "concurrency_report.json"):
        """生成完整的测试报告"""
        if not self.test_results:
            print("No test results to report")
            return
            
        # 准备报告数据
        report_data = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "test_timestamp": datetime.now().isoformat(),
                "model": self.model,
                "base_url": self.base_url
            },
            "performance_summary": {
                "max_qps": max((r.qps for r in self.test_results), default=0),
                "best_concurrency": None,
                "bottleneck_concurrency": None,
                "avg_success_rate": sum(r.success_rate for r in self.test_results) / len(self.test_results)
            },
            "detailed_results": [asdict(result) for result in self.test_results]
        }
        
        # 找出最佳并发量 (QPS最高且成功率>95%)
        good_results = [r for r in self.test_results if r.success_rate >= 95.0]
        if good_results:
            best_result = max(good_results, key=lambda x: x.qps)
            report_data["performance_summary"]["best_concurrency"] = best_result.config.concurrency
            
        # 保存到JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        # 打印摘要报告
        self._print_summary_report(report_data)
        
        print(f"\n📊 详细报告已保存到: {output_file}")
    
    def _print_summary_report(self, report_data: Dict):
        """打印摘要报告"""
        summary = report_data["performance_summary"]
        
        report = f"""
{'='*60}
                    并发性能测试报告
{'='*60}
测试模型: {self.model}
测试时间: {report_data["test_summary"]["test_timestamp"]}
总测试数: {report_data["test_summary"]["total_tests"]}

🎯 性能摘要:
  最高QPS: {summary["max_qps"]:.2f}
  推荐并发量: {summary["best_concurrency"] or "未确定"}
  平均成功率: {summary["avg_success_rate"]:.1f}%

📊 测试结果详情:"""

        # 按并发量排序显示结果
        sorted_results = sorted(self.test_results, key=lambda x: x.config.concurrency)
        
        for result in sorted_results:
            status_icon = "✅" if result.success_rate >= 95 else "⚠️" if result.success_rate >= 90 else "❌"
            report += f"""
  {status_icon} 并发{result.config.concurrency:3d}: QPS={result.qps:6.2f} | 成功率={result.success_rate:5.1f}% | P95延迟={result.p95_response_time:5.2f}s | TTFT={result.avg_ttft:5.3f}s"""
        
        report += f"\n{'='*60}"
        print(report)


async def main():
    # 配置参数
    base_url = os.getenv("ZHIZENGZENG_BASE_URL", "https://api.zhizengzeng.com/v1")
    api_key = os.getenv("ZHIZENGZENG_API_KEY")
    model = os.getenv("ZHIZENGZENG_MODEL", "deepseek-v3")
    
    if not api_key:
        print("❌ 请设置 ZHIZENGZENG_API_KEY 环境变量")
        return
        
    print(f"🚀 启动并发性能测试")
    print(f"   模型: {model}")
    print(f"   API: {base_url}")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # 创建报告生成器
    reporter = ConcurrencyReportGenerator(base_url, api_key, model)
    
    try:
        # 1. 预定义并发量测试
        print("\n🔧 1. 运行预定义并发量测试 (10, 50, 100, 200)...")
        await reporter.run_predefined_concurrency_tests()
        
        # 2. 负载变化测试
        print("\n📈 2. 运行负载变化测试...")
        await reporter.run_load_variation_test()
        
        # 3. 弹性测试
        print("\n🔍 3. 运行弹性测试...")
        await reporter.run_elastic_test(
            start_concurrency=10,
            max_concurrency=250,
            step_size=20,
            success_threshold=95.0,
            max_response_time=20.0
        )
        
        # 生成报告
        print("\n📋 生成测试报告...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"concurrency_report_{timestamp}.json"
        reporter.generate_report(report_file)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        reporter.generate_report("concurrency_report_interrupted.json")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        reporter.generate_report("concurrency_report_error.json")


if __name__ == "__main__":
    asyncio.run(main())