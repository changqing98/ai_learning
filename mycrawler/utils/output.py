"""结果输出：JSON 存储 + Rich 控制台表格"""

import json
import os
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def save_json(data: dict) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = datetime.now().strftime("%Y-%m-%d_%H") + ".json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath


def print_bilibili(items: list):
    table = Table(title="B站 热门视频分类 TOP", box=box.ROUNDED, style="cyan")
    table.add_column("排名", justify="center", width=6)
    table.add_column("分区", width=16)
    table.add_column("视频数量", justify="right", width=10)
    for item in items:
        table.add_row(str(item["rank"]), item["category"], str(item["count"]))
    console.print(table)


def print_douyin(items: list):
    table = Table(title="抖音 热搜榜 TOP", box=box.ROUNDED, style="magenta")
    table.add_column("排名", justify="center", width=6)
    table.add_column("热搜词", width=30)
    table.add_column("热度值", justify="right", width=12)
    for item in items:
        table.add_row(str(item["rank"]), item["tag"], str(item.get("hot_value", "-")))
    console.print(table)


def print_xiaohongshu(items: list):
    table = Table(title="小红书 热门话题 TOP", box=box.ROUNDED, style="red")
    table.add_column("排名", justify="center", width=6)
    table.add_column("话题", width=30)
    table.add_column("浏览量", justify="right", width=12)
    for item in items:
        table.add_row(str(item["rank"]), item["topic"], item.get("view_count", "-"))
    console.print(table)
