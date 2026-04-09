"""抖音热榜爬虫

使用抖音热搜榜公开接口，提取当前热门话题/词条。
若接口因风控返回空数据，请在 utils/headers.py 的 DOUYIN_HEADERS 中填入有效 Cookie。
"""

from typing import List, Dict

import requests

from utils.headers import DOUYIN_HEADERS

# 抖音热搜榜接口
HOT_SEARCH_URL = "https://www.douyin.com/aweme/v1/hot/search/list/"
# 备用：抖音热点榜（无需签名）
BOARD_URL = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"

TIMEOUT = 10


def _fetch_primary(top_n: int) -> List[Dict]:
    """使用主接口抓取热搜榜"""
    params = {"device_platform": "webapp", "aid": "6383", "count": top_n}
    resp = requests.get(
        HOT_SEARCH_URL, headers=DOUYIN_HEADERS, params=params, timeout=TIMEOUT
    )
    resp.raise_for_status()
    data = resp.json()

    word_list = data.get("data", {}).get("word_list", [])
    results = []
    for rank, item in enumerate(word_list[:top_n], start=1):
        results.append({
            "rank": rank,
            "tag": item.get("word", ""),
            "hot_value": item.get("hot_value", 0),
            "label": item.get("label", ""),
        })
    return results


def _fetch_fallback(top_n: int) -> List[Dict]:
    """备用接口：抖音热点榜"""
    params = {"count": top_n}
    resp = requests.get(
        BOARD_URL, headers=DOUYIN_HEADERS, params=params, timeout=TIMEOUT
    )
    resp.raise_for_status()
    data = resp.json()

    word_list = data.get("word_list", [])
    results = []
    for rank, item in enumerate(word_list[:top_n], start=1):
        results.append({
            "rank": rank,
            "tag": item.get("word", ""),
            "hot_value": item.get("hot_value", 0),
            "label": item.get("label", ""),
        })
    return results


def crawl(top_n: int = 10) -> Dict:
    """主入口：返回抖音热搜数据"""
    print("[抖音] 正在抓取热搜榜...")
    results = []

    try:
        results = _fetch_primary(top_n)
    except Exception as e:
        print(f"[抖音] 主接口失败 ({e})，尝试备用接口...")

    if not results:
        try:
            results = _fetch_fallback(top_n)
        except Exception as e:
            print(f"[抖音] 备用接口也失败 ({e})，请检查网络或补充 Cookie")

    print(f"[抖音] 完成，共 {len(results)} 条热搜")
    return {"hot_search": results}


if __name__ == "__main__":
    from utils.output import print_douyin
    result = crawl()
    print_douyin(result["hot_search"])
