"""小红书热门话题爬虫

使用 Playwright 无头浏览器模拟访问，抓取探索页热门话题标签。
首次运行需执行：playwright install chromium
"""

import re
import json
from typing import List, Dict


def _parse_topics_from_page(page_content: str) -> List[Dict]:
    """从页面 HTML/脚本中提取话题数据"""
    results = []

    # 尝试从内联 JSON 数据中提取话题（小红书会把部分数据内嵌在 window.__INITIAL_STATE__ 里）
    pattern = re.compile(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', re.DOTALL)
    match = pattern.search(page_content)
    if match:
        try:
            state = json.loads(match.group(1))
            # 路径可能随版本变化，尽力尝试
            topics = (
                state.get("explore", {}).get("hotTopics", [])
                or state.get("homefeed", {}).get("hotTopics", [])
            )
            for rank, t in enumerate(topics, start=1):
                results.append({
                    "rank": rank,
                    "topic": t.get("name", t.get("title", "")),
                    "view_count": t.get("viewNum", t.get("discussCount", "-")),
                })
        except json.JSONDecodeError:
            pass

    return results


def _parse_topics_from_dom(page) -> List[Dict]:
    """通过 DOM 选择器抓取话题标签（作为备选）"""
    results = []
    # 小红书探索页热门话题区块的选择器（随版本可能变化）
    selectors = [
        ".topic-item",
        "[class*='topic']",
        "[data-testid*='topic']",
    ]
    for selector in selectors:
        items = page.query_selector_all(selector)
        if items:
            for rank, el in enumerate(items[:20], start=1):
                text = el.inner_text().strip()
                if text:
                    results.append({"rank": rank, "topic": text, "view_count": "-"})
            break
    return results


def crawl(top_n: int = 10) -> Dict:
    """主入口：返回小红书热门话题数据"""
    print("[小红书] 正在启动浏览器...")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[小红书] 未安装 playwright，请执行：pip install playwright && playwright install chromium")
        return {"hot_topics": []}

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        try:
            print("[小红书] 正在加载探索页...")
            page.goto("https://www.xiaohongshu.com/explore", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=20000)

            # 先尝试从内嵌 JSON 提取
            content = page.content()
            results = _parse_topics_from_page(content)

            # 若内嵌数据不可用，再尝试 DOM 选择器
            if not results:
                results = _parse_topics_from_dom(page)

            results = results[:top_n]

            if not results:
                print(
                    "[小红书] 未能提取到话题数据，可能需要登录 Cookie 或页面结构已变更。\n"
                    "         请在 context.new_context() 中添加 storage_state 参数传入已登录的 Cookie。"
                )
        except Exception as e:
            print(f"[小红书] 抓取失败: {e}")
        finally:
            browser.close()

    print(f"[小红书] 完成，共 {len(results)} 个热门话题")
    return {"hot_topics": results}


if __name__ == "__main__":
    from utils.output import print_xiaohongshu
    result = crawl()
    print_xiaohongshu(result["hot_topics"])
