"""
短视频平台热门分类爬虫服务
抓取 B站 / 抖音 / 小红书 的近期热门视频类别，输出 JSON 报告 + 控制台表格。

用法：
    python main.py            # 抓取全部平台（默认 TOP10）
    python main.py --top 20   # 自定义返回条数
    python main.py --platform bilibili douyin  # 只抓指定平台
"""

import argparse
import sys
import os
from datetime import datetime

# 确保在 mycrawler 目录下可直接运行
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.rule import Rule

import crawlers.bilibili as bili_crawler
import crawlers.douyin as douyin_crawler
import crawlers.xiaohongshu as xhs_crawler
from utils.output import save_json, print_bilibili, print_douyin, print_xiaohongshu

console = Console()

ALL_PLATFORMS = ["bilibili", "douyin", "xiaohongshu"]


def run(platforms: list, top_n: int) -> dict:
    report = {"crawled_at": datetime.now().isoformat(timespec="seconds")}

    if "bilibili" in platforms:
        console.print(Rule("[cyan]B站[/cyan]"))
        try:
            result = bili_crawler.crawl(top_n)
            report["bilibili"] = result
            print_bilibili(result["categories"])
            if result["hot_words"]:
                console.print(f"  热搜词：{' | '.join(result['hot_words'])}\n")
        except Exception as e:
            console.print(f"[red][B站] 抓取失败: {e}[/red]")
            report["bilibili"] = {"error": str(e)}

    if "douyin" in platforms:
        console.print(Rule("[magenta]抖音[/magenta]"))
        try:
            result = douyin_crawler.crawl(top_n)
            report["douyin"] = result
            print_douyin(result["hot_search"])
        except Exception as e:
            console.print(f"[red][抖音] 抓取失败: {e}[/red]")
            report["douyin"] = {"error": str(e)}

    if "xiaohongshu" in platforms:
        console.print(Rule("[red]小红书[/red]"))
        try:
            result = xhs_crawler.crawl(top_n)
            report["xiaohongshu"] = result
            print_xiaohongshu(result["hot_topics"])
        except Exception as e:
            console.print(f"[red][小红书] 抓取失败: {e}[/red]")
            report["xiaohongshu"] = {"error": str(e)}

    return report


def main():
    parser = argparse.ArgumentParser(description="短视频平台热门分类爬虫")
    parser.add_argument(
        "--platform",
        nargs="+",
        choices=ALL_PLATFORMS,
        default=ALL_PLATFORMS,
        help="指定抓取平台（默认全部）",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="每平台返回条数（默认10）",
    )
    args = parser.parse_args()

    console.print(
        f"\n[bold]短视频热门分类爬虫[/bold]  "
        f"平台: {', '.join(args.platform)}  TOP: {args.top}\n"
    )

    report = run(args.platform, args.top)

    filepath = save_json(report)
    console.print(Rule())
    console.print(f"[green]报告已保存至：{filepath}[/green]\n")


if __name__ == "__main__":
    main()
