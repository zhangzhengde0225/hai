#!/usr/bin/env python3
"""
TTFT (Time To First Token) 专项测试报告
测试不同并发量下的首次token延迟分布并生成可视化图表
"""

import os
import sys
import asyncio
import time
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics

here = Path(__file__).parent
sys.path.insert(0, str(here))

from concurrency_tester import ZhizzConcurrencyTester, TestResult


@dataclass
class TTFTTestResult:
    """TTFT测试结果"""
    concurrency: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    ttft_values: List[float]  # 所有成功请求的TTFT值
    avg_ttft: float
    median_ttft: float
    p95_ttft: float
    p99_ttft: float
    min_ttft: float
    max_ttft: float
    std_ttft: float
    success_rate: float
    timestamp: str


class TTFTReportGenerator:
    """TTFT报告生成器"""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.tester = ZhizzConcurrencyTester(base_url, api_key, model)
        self.test_results: List[TTFTTestResult] = []
        
        # 设置matplotlib中文字体和样式
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.size'] = 12  # 增大字体
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 11
        plt.rcParams['ytick.labelsize'] = 11
        plt.rcParams['legend.fontsize'] = 11
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        return np.percentile(values, percentile)
    
    async def run_ttft_test(self, concurrency: int, total_requests: int, question: str) -> TTFTTestResult:
        """运行单次TTFT测试"""
        print(f"Testing TTFT: concurrency={concurrency}, requests={total_requests}")
        
        # 使用异步模式进行测试
        await self.tester.run_async_test(question, concurrency, total_requests, stream=True)
        results = self.tester.results
        
        # 提取TTFT数据
        successful_results = [r for r in results if r.status == "success" and r.first_token_time is not None]
        failed_requests = len(results) - len(successful_results)
        
        if not successful_results:
            return TTFTTestResult(
                concurrency=concurrency,
                total_requests=total_requests,
                successful_requests=0,
                failed_requests=failed_requests,
                ttft_values=[],
                avg_ttft=0,
                median_ttft=0,
                p95_ttft=0,
                p99_ttft=0,
                min_ttft=0,
                max_ttft=0,
                std_ttft=0,
                success_rate=0,
                timestamp=datetime.now().isoformat()
            )
        
        ttft_values = [r.first_token_time for r in successful_results]
        success_rate = len(successful_results) / total_requests * 100
        
        return TTFTTestResult(
            concurrency=concurrency,
            total_requests=total_requests,
            successful_requests=len(successful_results),
            failed_requests=failed_requests,
            ttft_values=ttft_values,
            avg_ttft=statistics.mean(ttft_values),
            median_ttft=statistics.median(ttft_values),
            p95_ttft=self._calculate_percentile(ttft_values, 95),
            p99_ttft=self._calculate_percentile(ttft_values, 99),
            min_ttft=min(ttft_values),
            max_ttft=max(ttft_values),
            std_ttft=statistics.stdev(ttft_values) if len(ttft_values) > 1 else 0,
            success_rate=success_rate,
            timestamp=datetime.now().isoformat()
        )
    
    async def run_comprehensive_ttft_tests(self, concurrency_levels: List[int] = None, 
                                         test_question: str = "解释一下人工智能的基本原理和应用") -> List[TTFTTestResult]:
        """运行全面的TTFT测试"""
        if concurrency_levels is None:
            concurrency_levels = [1, 5, 10, 20, 30, 50, 75, 100, 150, 200]
        
        print(f"Starting comprehensive TTFT tests with concurrency levels: {concurrency_levels}")
        print(f"Test question: {test_question[:50]}...")
        print("-" * 80)
        
        results = []
        
        for concurrency in concurrency_levels:
            # 根据并发量调整请求数，确保足够的样本
            requests_count = max(concurrency * 3, 30)  # 至少30个请求
            
            try:
                result = await self.run_ttft_test(concurrency, requests_count, test_question)
                results.append(result)
                self.test_results.append(result)
                
                print(f"✓ Concurrency {concurrency:3d}: "
                      f"TTFT avg={result.avg_ttft:.3f}s, "
                      f"P95={result.p95_ttft:.3f}s, "
                      f"success={result.success_rate:.1f}%")
                
                # 休息避免过载
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"✗ Failed concurrency {concurrency}: {e}")
                
        return results
    
    def plot_ttft_distribution_histograms(self, output_dir: str = None):
        """绘制TTFT分布直方图"""
        if not self.test_results:
            print("No test results available for plotting")
            return
            
        # 设置默认输出目录
        if output_dir is None:
            output_dir = str(here / "ttft_plots")
            
        # 创建输出目录
        Path(output_dir).mkdir(exist_ok=True)
        
        # 1. 单独的直方图 - 每个并发量一个图
        self._plot_individual_histograms(output_dir)
        
        # 2. 组合直方图 - 所有并发量在一个图中
        self._plot_combined_histogram(output_dir)
        
        # 3. 箱线图 - 显示分布统计
        self._plot_boxplot(output_dir)
        
        # 4. 趋势图 - TTFT统计指标随并发量的变化
        self._plot_ttft_trends(output_dir)
        
        print(f"📊 All plots saved to: {output_dir}/")
    
    def _plot_individual_histograms(self, output_dir: str):
        """绘制每个并发量的单独直方图"""
        for result in self.test_results:
            if not result.ttft_values:
                continue
                
            plt.figure(figsize=(10, 6))
            
            # 绘制直方图
            plt.hist(result.ttft_values, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            
            # 添加统计线
            plt.axvline(result.avg_ttft, color='red', linestyle='--', 
                       label=f'Mean: {result.avg_ttft:.3f}s')
            plt.axvline(result.median_ttft, color='green', linestyle='--', 
                       label=f'Median: {result.median_ttft:.3f}s')
            plt.axvline(result.p95_ttft, color='orange', linestyle='--', 
                       label=f'P95: {result.p95_ttft:.3f}s')
            
            plt.xlabel('Time to First Token (seconds)')
            plt.ylabel('Frequency')
            plt.title(f'TTFT Distribution - Concurrency {result.concurrency}\n'
                     f'Samples: {result.successful_requests}, Success Rate: {result.success_rate:.1f}%')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # 保存图片
            filename = f"{output_dir}/ttft_histogram_concurrency_{result.concurrency}.png"
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
    
    def _plot_combined_histogram(self, output_dir: str):
        """绘制组合直方图"""
        plt.figure(figsize=(15, 10))
        
        # 选择一些代表性的并发量
        selected_results = [r for r in self.test_results if r.concurrency in [1, 10, 50, 100, 200]]
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(selected_results)))
        
        for i, result in enumerate(selected_results):
            if result.ttft_values:
                plt.hist(result.ttft_values, bins=20, alpha=0.6, 
                        color=colors[i], label=f'Concurrency {result.concurrency}',
                        density=True)
        
        plt.xlabel('Time to First Token (seconds)')
        plt.ylabel('Density')
        plt.title('TTFT Distribution Comparison Across Concurrency Levels')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        filename = f"{output_dir}/ttft_combined_histogram.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_boxplot(self, output_dir: str):
        """绘制箱线图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 准备数据
        concurrency_levels = [r.concurrency for r in self.test_results if r.ttft_values]
        ttft_data = [r.ttft_values for r in self.test_results if r.ttft_values]
        
        if not ttft_data:
            print("No data available for boxplot")
            return
        
        # 箱线图
        ax1.boxplot(ttft_data, labels=concurrency_levels)
        ax1.set_xlabel('Concurrency Level')
        ax1.set_ylabel('Time to First Token (seconds)')
        ax1.set_title('TTFT Distribution by Concurrency Level')
        ax1.grid(True, alpha=0.3)
        
        # 小提琴图
        parts = ax2.violinplot(ttft_data, positions=range(1, len(ttft_data) + 1))
        ax2.set_xticks(range(1, len(concurrency_levels) + 1))
        ax2.set_xticklabels(concurrency_levels)
        ax2.set_xlabel('Concurrency Level')
        ax2.set_ylabel('Time to First Token (seconds)')
        ax2.set_title('TTFT Distribution Density by Concurrency Level')
        ax2.grid(True, alpha=0.3)
        
        filename = f"{output_dir}/ttft_boxplot.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_ttft_trends(self, output_dir: str):
        """绘制TTFT趋势图"""
        concurrency_levels = [r.concurrency for r in self.test_results]
        avg_ttfts = [r.avg_ttft for r in self.test_results]
        median_ttfts = [r.median_ttft for r in self.test_results]
        p95_ttfts = [r.p95_ttft for r in self.test_results]
        p99_ttfts = [r.p99_ttft for r in self.test_results]
        success_rates = [r.success_rate for r in self.test_results]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # TTFT趋势
        ax1.plot(concurrency_levels, avg_ttfts, 'o-', label='Average TTFT', linewidth=2)
        ax1.plot(concurrency_levels, median_ttfts, 's-', label='Median TTFT', linewidth=2)
        ax1.plot(concurrency_levels, p95_ttfts, '^-', label='P95 TTFT', linewidth=2)
        ax1.plot(concurrency_levels, p99_ttfts, 'v-', label='P99 TTFT', linewidth=2)
        
        ax1.set_xlabel('Concurrency Level')
        ax1.set_ylabel('Time to First Token (seconds)')
        ax1.set_title('TTFT Metrics vs Concurrency Level')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 成功率趋势
        ax2.plot(concurrency_levels, success_rates, 'o-', color='green', linewidth=2)
        ax2.set_xlabel('Concurrency Level')
        ax2.set_ylabel('Success Rate (%)')
        ax2.set_title('Success Rate vs Concurrency Level')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 105)
        
        filename = f"{output_dir}/ttft_trends.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_report(self, output_file: str = "ttft_report.json"):
        """生成TTFT测试报告"""
        if not self.test_results:
            print("No test results to report")
            return
        
        output_dir = Path(output_file).parent
        output_dir.mkdir(parents=True, exist_ok=True)
            
        # 准备报告数据
        report_data = {
            "test_summary": {
                "total_concurrency_levels": len(self.test_results),
                "test_timestamp": datetime.now().isoformat(),
                "model": self.model,
                "base_url": self.base_url,
            },
            "ttft_summary": {
                "min_avg_ttft": min(r.avg_ttft for r in self.test_results),
                "max_avg_ttft": max(r.avg_ttft for r in self.test_results),
                "optimal_concurrency": None,
                "degradation_threshold": None
            },
            "detailed_results": [asdict(result) for result in self.test_results]
        }
        
        # 分析最优并发量（TTFT增长不超过50%的最高并发量）
        baseline_ttft = self.test_results[0].avg_ttft if self.test_results else 0
        optimal_concurrency = 1
        
        for result in self.test_results:
            if result.avg_ttft <= baseline_ttft * 1.5 and result.success_rate >= 95:
                optimal_concurrency = result.concurrency
            else:
                break
                
        report_data["ttft_summary"]["optimal_concurrency"] = optimal_concurrency
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        # 打印摘要
        self._print_ttft_summary(report_data)
        
        print(f"\n📊 详细报告已保存到: {output_file}")
    
    def _print_ttft_summary(self, report_data: Dict):
        """打印TTFT摘要"""
        summary = report_data["ttft_summary"]
        
        report = f"""
{'='*70}
                    TTFT 性能测试报告
{'='*70}
测试模型: {self.model}
测试时间: {report_data["test_summary"]["test_timestamp"]}
并发级别数: {report_data["test_summary"]["total_concurrency_levels"]}

🎯 TTFT 摘要:
  最低平均TTFT: {summary["min_avg_ttft"]:.3f}s
  最高平均TTFT: {summary["max_avg_ttft"]:.3f}s
  推荐并发量: {summary["optimal_concurrency"]}

📊 各并发级别详情:"""

        for result in self.test_results:
            status_icon = "✅" if result.success_rate >= 95 else "⚠️" if result.success_rate >= 90 else "❌"
            report += f"""
  {status_icon} 并发{result.concurrency:3d}: Avg={result.avg_ttft:.3f}s | P95={result.p95_ttft:.3f}s | P99={result.p99_ttft:.3f}s | 成功率={result.success_rate:5.1f}%"""
        
        report += f"\n{'='*70}"
        print(report)


async def main():
    # 配置参数
    base_url = os.getenv("ZHIZENGZENG_BASE_URL", "https://api.zhizengzeng.com/v1")
    api_key = os.getenv("ZHIZENGZENG_API_KEY")
    model = os.getenv("ZHIZENGZENG_MODEL", "deepseek-v3")
    
    api_key = "sk-lZvDMeNaRjKjGtrLArHsVOFtfCLbJuuHWxrBuTIREHsjDqT"
    base_url = "http://localhost:42602/apiv2"
    model = "deepseek-ai/deepseek-v3"
    
    if not api_key:
        print("❌ 请设置 ZHIZENGZENG_API_KEY 环境变量")
        return
        
    print(f"🚀 启动 TTFT 专项性能测试")
    print(f"   模型: {model}")
    print(f"   API: {base_url}")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 创建TTFT报告生成器
    ttft_reporter = TTFTReportGenerator(base_url, api_key, model)
    
    try:
        # 运行TTFT测试
        concurrency_levels = [1, 5, 10, 20, 30, 50, 75, 100, 150, 200]
        # concurrency_levels = [10, 20, 30, 50, 75, 100, 150, 200]
        # test_question = "请详细解释深度学习的基本原理，包括神经网络的结构、训练过程和主要应用领域。"
        test_question = "hello"
        
        print(f"🔍 测试并发级别: {concurrency_levels}")
        print(f"📝 测试问题: {test_question[:30]}...")
        print("-" * 80)
        
        await ttft_reporter.run_comprehensive_ttft_tests(
            concurrency_levels=concurrency_levels,
            test_question=test_question
        )
        
        # 生成报告和图表
        print("\n📋 生成测试报告...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"{here}/ttft_plots_{timestamp}/ttft_report_{timestamp}.json"
        ttft_reporter.generate_report(report_file)
        
        print("\n📊 生成可视化图表...")
        plot_dir = f"{here}/ttft_plots_{timestamp}"
        ttft_reporter.plot_ttft_distribution_histograms(plot_dir)

        print(f"\n✅ TTFT 测试完成!")
        print(f"   报告文件: {report_file}")
        print(f"   图表目录: {plot_dir}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        ttft_reporter.generate_report("ttft_report_interrupted.json")
        ttft_reporter.plot_ttft_distribution_histograms("ttft_plots_interrupted")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        ttft_reporter.generate_report("ttft_report_error.json")


if __name__ == "__main__":
    asyncio.run(main())