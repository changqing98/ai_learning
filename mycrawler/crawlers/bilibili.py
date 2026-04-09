"""B站热门视频分类爬虫（使用公开 REST API，无需登录）"""

from collections import Counter
from typing import List, Dict

import requests

from utils.headers import BILIBILI_HEADERS

# 热门视频排行榜（全站 TOP100）
RANKING_URL = "https://api.bilibili.com/x/web-interface/ranking/v2"
# B站热搜词
HOTWORD_URL = "https://s.search.bilibili.com/main/hotword"

TIMEOUT = 10


def fetch_ranking_categories(top_n: int = 10) -> List[Dict]:
    """
    从热门排行榜提取分区分布，返回 top_n 分区。
    """
    resp = requests.get(RANKING_URL, headers=BILIBILI_HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 0:
        raise RuntimeError(f"B站API返回错误: {data.get('message')}")

    videos = data["data"]["list"]
    category_counter: Counter = Counter()
    for v in videos:
        tname = v.get("tname", "未知")
        category_counter[tname] += 1

    results = []
    for rank, (category, count) in enumerate(category_counter.most_common(top_n), start=1):
        results.append({"rank": rank, "category": category, "count": count})
    return results


def fetch_hot_words(top_n: int = 10) -> List[str]:
    """获取B站热搜词列表"""
    resp = requests.get(HOTWORD_URL, headers=BILIBILI_HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 0:
        return []

    return [item.get("keyword", "") for item in data.get("list", [])[:top_n]]


def crawl(top_n: int = 10) -> Dict:
    """主入口：返回 B站热门分类 + 热搜词数据"""
    print("[B站] 正在抓取热门分类...")
    categories = fetch_ranking_categories(top_n)
    hot_words = fetch_hot_words(top_n)
    print(f"[B站] 完成，共 {len(categories)} 个分区，{len(hot_words)} 个热搜词")
    return {"categories": categories, "hot_words": hot_words}


if __name__ == "__main__":
    from utils.output import print_bilibili
    result = crawl()
    print_bilibili(result["categories"])
    print("热搜词:", result["hot_words"])
