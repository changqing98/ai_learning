# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目说明

`mycrawler/` 是一个 Python3 短视频平台热门分类爬虫服务，抓取 B站、抖音、小红书的近期热门视频类别，供短视频创作者做选题参考。

## 安装与运行

```bash
cd mycrawler
pip install -r requirements.txt
playwright install chromium   # 小红书需要无头浏览器
```

```bash
python main.py                            # 抓取全部平台 TOP10
python main.py --top 20                   # 自定义条数
python main.py --platform bilibili douyin # 只抓指定平台
```

单独运行某个平台爬虫（在 mycrawler/ 目录下）：
```bash
python -m crawlers.bilibili
python -m crawlers.douyin
python -m crawlers.xiaohongshu
```

## 架构说明

```
mycrawler/
├── main.py              # 入口：解析参数 → 调度三个爬虫 → 打印表格 → 保存 JSON
├── crawlers/
│   ├── bilibili.py      # 调用 B站公开 REST API（ranking/v2 + hotword），无需登录
│   ├── douyin.py        # 调用抖音热搜接口，主接口失败自动切备用接口
│   └── xiaohongshu.py   # Playwright 无头浏览器抓取，先解析内嵌 JSON，再降级 DOM 选择器
├── utils/
│   ├── headers.py       # 各平台 User-Agent / Referer / Cookie 配置
│   └── output.py        # Rich 表格打印 + JSON 文件存储（output/YYYY-MM-DD_HH.json）
└── output/              # 爬取结果（gitignore 中排除）
```

## 反爬与 Cookie 配置

- **B站**：公开 API，通常无需 Cookie，直接可用。
- **抖音**：若两个接口均返回空数据，在 `utils/headers.py` 的 `DOUYIN_HEADERS["Cookie"]` 填入浏览器抓包获取的 Cookie。
- **小红书**：若 Playwright 未能提取数据（需要登录），在 `crawlers/xiaohongshu.py` 的 `context.new_context()` 中添加 `storage_state` 参数，传入已导出的登录态 JSON 文件。
