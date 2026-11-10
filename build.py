#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Galwiki 静态站点构建器。

运行：python3 build.py
产出：8 个内容页 + 404、sitemap.xml、robots.txt、rss.xml、
      search-index.js / .json、assets/img/og-cover.png

设计要点：
  * 页面数据集中在 content_data.py / content_pages.py，模板与 SEO 元数据在此统一注入
  * 每页输出一套 JSON-LD @graph（WebSite / Organization / BreadcrumbList / 页型实体）
  * 全站零外部依赖，file:// 直接双击打开也能用（搜索索引走 .js 而非 fetch）
"""

from __future__ import annotations

import html as html_lib
import json
import re
import datetime
import email.utils
from pathlib import Path

from content_data import SITE, ORG, NAV, WORKS, GLOSSARY, FAQ, TIMELINE
from content_pages import PAGES

ROOT = Path(__file__).resolve().parent
TODAY = datetime.date.today().isoformat()
SITE_URL = SITE["url"].rstrip("/")
ORG_ID = SITE_URL + "/#organization"
WEB_ID = SITE_URL + "/#website"
OG_IMAGE = SITE_URL + "/assets/img/og-cover.png"


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------
def strip_tags(raw: str) -> str:
    """把 HTML 片段转为纯文本，供结构化数据与搜索索引使用。"""
    text = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.S | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def esc(s: str) -> str:
    return html_lib.escape(str(s), quote=True)


def page_url(page: dict) -> str:
    if page["file"] == "index.html":
        return SITE_URL + "/"
    return SITE_URL + "/" + page["file"]


def jsonld_safe(obj) -> str:
    """JSON-LD 里禁止出现裸 </ ，避免提前闭合 script 标签。"""
    return json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/")


# ---------------------------------------------------------------------------
# 结构化数据
# ---------------------------------------------------------------------------
def schema_graph(page: dict) -> list:
    url = page_url(page)
    graph = [
        {
            "@type": "WebSite",
            "@id": WEB_ID,
            "url": SITE_URL + "/",
            "name": SITE["full_name"],
            "alternateName": SITE["name"],
            "description": SITE["description"],
            "inLanguage": "zh-CN",
            "publisher": {"@id": ORG_ID},
        },
        {
            "@type": "Organization",
            "@id": ORG_ID,
            "name": SITE["name"],
            "url": SITE_URL + "/",
            "description": ORG["description"],
            "logo": {"@type": "ImageObject", "url": OG_IMAGE},
            "email": "hello@galgameinfowiki.github.io",
        },
    ]

    if page["file"] != "index.html":
        graph.append({
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "首页", "item": SITE_URL + "/"},
                {"@type": "ListItem", "position": 2, "name": page["h1"], "item": url},
            ],
        })

    ptype = page["schema"]
    breadcrumb_ref = {"@id": url + "#breadcrumb"} if page["file"] != "index.html" else None

    if ptype == "FAQPage":
        entity = {
            "@type": "FAQPage",
            "@id": url + "#webpage",
            "url": url,
            "name": page["h1"],
            "description": page["description"],
            "inLanguage": "zh-CN",
            "isPartOf": {"@id": WEB_ID},
            "datePublished": SITE["published"],
            "dateModified": TODAY,
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": strip_tags(item["a"])},
                }
                for item in FAQ
            ],
        }
    else:
        entity = {
            "@type": ptype,
            "@id": url + "#webpage",
            "url": url,
            "name": page["h1"],
            "headline": page["h1"],
            "description": page["description"],
            "inLanguage": "zh-CN",
            "isPartOf": {"@id": WEB_ID},
            "datePublished": SITE["published"],
            "dateModified": TODAY,
            "author": {"@id": ORG_ID},
            "publisher": {"@id": ORG_ID},
            "mainEntityOfPage": url,
            "image": {"@type": "ImageObject", "url": OG_IMAGE, "width": 1200, "height": 630},
        }
        if ptype == "CollectionPage":
            entity["mainEntity"] = {
                "@type": "ItemList",
                "numberOfItems": len(WORKS),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i + 1,
                        "name": w["name"],
                        "url": SITE_URL + "/works.html#" + w["id"],
                    }
                    for i, w in enumerate(WORKS)
                ],
            }
        if ptype == "DefinedTermSet":
            terms = [t for g in GLOSSARY for t in g["terms"]]
            entity["hasDefinedTerm"] = [
                {"@type": "DefinedTerm", "name": t[1], "description": t[3]}
                for t in terms
            ]

    if breadcrumb_ref:
        entity["breadcrumb"] = breadcrumb_ref
    graph.append(entity)
    return graph


# ---------------------------------------------------------------------------
# 页面片段
# ---------------------------------------------------------------------------
ICON_SEARCH = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/></svg>'
ICON_SUN = '<svg class="icon-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
ICON_MOON = '<svg class="icon-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg>'
ICON_MENU = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
ICON_UP = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg>'


def head(page: dict) -> str:
    url = page_url(page)
    robots = "noindex, follow" if page.get("noindex") else "index, follow, max-image-preview:large, max-snippet:-1"
    og_type = "article" if page["schema"] in ("Article", "CollectionPage", "DefinedTermSet", "FAQPage", "AboutPage") else "website"

    # 主题防闪烁：必须在样式表之前同步执行
    theme_boot = """<script>(function(){var t;try{t=localStorage.getItem('galwiki-theme')}catch(e){}if(!t){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}document.documentElement.setAttribute('data-theme',t)})();</script>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(page['title'])}</title>
<meta name="description" content="{esc(page['description'])}">
<meta name="keywords" content="{esc(page['keywords'])}">
<meta name="author" content="{esc(SITE['author'])}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#6742c9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#100e19" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{esc(url)}">
<link rel="alternate" type="application/rss+xml" title="{esc(SITE['full_name'])} RSS" href="{SITE_URL}/rss.xml">
<link rel="icon" type="image/svg+xml" href="assets/img/favicon.svg">

<meta property="og:site_name" content="{esc(SITE['full_name'])}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="zh_CN">
<meta property="og:title" content="{esc(page['title'])}">
<meta property="og:description" content="{esc(page['description'])}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Galwiki · 视觉小说与 Galgame 文化图鉴">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(page['title'])}">
<meta name="twitter:description" content="{esc(page['description'])}">
<meta name="twitter:image" content="{OG_IMAGE}">

{theme_boot}
<link rel="preload" href="assets/css/style.css" as="style">
<link rel="stylesheet" href="assets/css/style.css">
<script src="search-index.js" defer></script>
<script src="assets/js/main.js" defer></script>
<script type="application/ld+json">
{jsonld_safe({"@context": "https://schema.org", "@graph": schema_graph(page)})}
</script>
</head>"""


def header(page: dict) -> str:
    current = page["file"]
    links = "\n".join(
        f'<a href="{f}"' + (' aria-current="page"' if f == current else '') + f'>{label}</a>'
        for f, label in NAV
    )
    return f"""<a class="skip-link" href="#main">跳到正文</a>
<div id="progress" role="presentation"></div>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="index.html" aria-label="{esc(SITE['full_name'])} 首页">
      <span class="brand-mark" aria-hidden="true">G</span>
      <span>Galwiki<small>GALGAME / VISUAL NOVEL</small></span>
    </a>
    <nav class="nav" id="primary-nav" aria-label="主导航">
{links}
    </nav>
    <div class="header-actions">
      <button class="icon-btn" type="button" data-search-open aria-label="打开站内搜索" title="站内搜索 (Ctrl/⌘ + K)">{ICON_SEARCH}</button>
      <button class="icon-btn" type="button" id="theme-toggle" aria-label="切换深色模式" title="切换深色模式">{ICON_SUN}{ICON_MOON}</button>
      <button class="icon-btn menu-toggle" type="button" id="menu-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="打开导航菜单">{ICON_MENU}</button>
    </div>
  </div>
</header>"""


def breadcrumb(page: dict) -> str:
    return f"""<nav class="breadcrumb container" aria-label="面包屑导航">
  <ol><li><a href="index.html">首页</a></li><li aria-current="page">{esc(page['h1'])}</li></ol>
</nav>"""


def toc_html(page: dict) -> tuple[str, str]:
    items = page.get("toc", [])
    if not items:
        return "", ""
    desktop = "\n".join(f'<li><a href="#{esc(i)}">{esc(t)}</a></li>' for i, t in items)
    mobile = "\n".join(f'<li><a href="#{esc(i)}">{esc(t)}</a></li>' for i, t in items)
    desk = f'<aside class="toc" aria-label="本页目录"><strong>本页目录</strong><ol>{desktop}</ol></aside>'
    mob = f'<details class="toc-mobile"><summary>本页目录（{len(items)} 节）</summary><ol>{mobile}</ol></details>'
    return desk, mob


def footer() -> str:
    col1 = "\n".join(f'<li><a href="{f}">{label}</a></li>' for f, label in NAV[:4])
    col2 = "\n".join(f'<li><a href="{f}">{label}</a></li>' for f, label in NAV[4:])
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-about">
        <a class="brand" href="index.html" aria-label="Galwiki 首页"><span class="brand-mark" aria-hidden="true">G</span><span>Galwiki<small>GALGAME / VISUAL NOVEL</small></span></a>
        <p>{esc(SITE['short_desc'])}。只做定义、历史、术语与作品整理，不提供下载、补丁与剧透式攻略，不收录限制级内容。</p>
      </div>
      <div><h3>站点导航</h3><ul>{col1}</ul></div>
      <div><h3>更多内容</h3><ul>{col2}<li><a href="sitemap.xml">站点地图</a></li><li><a href="rss.xml">RSS 订阅</a></li></ul></div>
    </div>
    <div class="footer-bottom">
      <span>© {datetime.date.today().year} {esc(SITE['name'])} · 内容仅供文化科普与资料查阅</span>
      <span>作品名称与商标归各自权利人所有 · <a href="about.html#boundary">内容边界</a> · <a href="about.html#privacy">隐私说明</a></span>
    </div>
  </div>
</footer>
<button class="back-top" id="back-top" type="button" aria-label="返回顶部" title="返回顶部">{ICON_UP}</button>"""


def search_modal() -> str:
    return """<div class="search-backdrop" id="search-backdrop" role="dialog" aria-modal="true" aria-label="站内搜索" aria-hidden="true">
  <div class="search-panel">
    <div class="search-field">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/></svg>
      <input id="search-input" type="search" placeholder="搜索作品、术语、年份或问题…" autocomplete="off" spellcheck="false" aria-label="搜索站内内容">
      <kbd>ESC</kbd>
    </div>
    <div class="search-results" id="search-results" role="listbox" aria-label="搜索结果"></div>
    <div class="search-foot">↑ ↓ 选择 · Enter 打开 · Esc 关闭 · 按 D 切换深浅主题</div>
  </div>
</div>"""


def render(page: dict) -> str:
    url = page_url(page)
    if page["kind"] == "home":
        main = f'<main id="main" tabindex="-1">\n{page["body"]}\n</main>'
    else:
        desk, mob = toc_html(page)
        word_count = len(strip_tags(page["body"]))
        minutes = max(2, round(word_count / 400))
        main = f"""<main id="main" tabindex="-1">
{breadcrumb(page)}
<div class="container">
  <div class="article-head">
    <span class="eyebrow">{esc(page['eyebrow'])}</span>
    <h1>{esc(page['h1'])}</h1>
    <p class="lead">{esc(page['lead'])}</p>
    <div class="article-meta">
      <span>阅读时长 约 {minutes} 分钟</span>
      <span>更新于 {TODAY}</span>
      <span>编辑 {esc(SITE['author'])}</span>
      <span><a href="{esc(url)}">固定链接</a></span>
    </div>
  </div>
</div>
<div class="container layout">
  <div class="layout-main">
{mob}
{page['body']}
  </div>
{desk}
</div>
</main>"""

    return f"""{head(page)}
<body>
{header(page)}
{main}
{footer()}
{search_modal()}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 搜索索引
# ---------------------------------------------------------------------------
def build_search_index() -> list:
    idx = []
    for p in PAGES:
        if p.get("noindex"):
            continue
        idx.append({
            "title": p["h1"],
            "url": p["file"] if p["file"] != "index.html" else "index.html",
            "description": p["description"][:110],
            "keywords": p["keywords"],
            "text": strip_tags(p["body"])[:8000],
        })
    for w in WORKS:
        idx.append({
            "title": w["name"],
            "url": "works.html#" + w["id"],
            "description": f"{w['year']} · {w['studio']} · {w['genre']}",
            "keywords": " ".join(w["tags"]) + " " + w["alt"],
            "text": w["desc"] + " " + w["why"],
        })
    for group in GLOSSARY:
        for tid, term, en, desc in group["terms"]:
            idx.append({
                "title": term,
                "url": "glossary.html#" + tid,
                "description": en + " · " + group["group"],
                "keywords": "galgame 术语 名词 " + term + " " + en,
                "text": desc,
            })
    for item in FAQ:
        idx.append({
            "title": item["q"],
            "url": "faq.html",
            "description": "常见问题",
            "keywords": "galgame 常见问题 问答 " + item["q"],
            "text": strip_tags(item["a"]),
        })
    for t in TIMELINE:
        idx.append({
            "title": t["year"] + " " + t["title"],
            "url": "history.html#" + t["id"],
            "description": "发展简史",
            "keywords": "galgame 历史 发展史 " + t["year"],
            "text": t["desc"],
        })
    return idx


# ---------------------------------------------------------------------------
# sitemap / robots / rss
# ---------------------------------------------------------------------------
def write_sitemap() -> None:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in PAGES:
        if p.get("noindex"):
            continue
        lines.append("  <url>")
        lines.append(f"    <loc>{esc(page_url(p))}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append(f"    <changefreq>{p['changefreq']}</changefreq>")
        lines.append(f"    <priority>{p['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_robots() -> None:
    txt = f"""# {SITE['full_name']}
User-agent: *
Allow: /
Disallow: /search-index.json

# 站点地图
Sitemap: {SITE_URL}/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(txt, encoding="utf-8")


def write_rss() -> None:
    pub_dt = datetime.datetime.strptime(SITE["published"], "%Y-%m-%d").replace(
        tzinfo=datetime.timezone.utc)
    pub = email.utils.format_datetime(pub_dt)
    items = []
    for p in PAGES:
        if p.get("noindex"):
            continue
        items.append(f"""    <item>
      <title>{esc(p['title'])}</title>
      <link>{esc(page_url(p))}</link>
      <guid isPermaLink="true">{esc(page_url(p))}</guid>
      <description>{esc(p['description'])}</description>
      <pubDate>{pub}</pubDate>
    </item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{esc(SITE['full_name'])}</title>
    <link>{SITE_URL}/</link>
    <description>{esc(SITE['description'])}</description>
    <language>zh-CN</language>
    <lastBuildDate>{pub}</lastBuildDate>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (ROOT / "rss.xml").write_text(rss, encoding="utf-8")


# ---------------------------------------------------------------------------
# OG 封面图（Pillow 本地生成，不依赖外部图片）
# ---------------------------------------------------------------------------
def make_og_image() -> None:
    out = ROOT / "assets" / "img" / "og-cover.png"
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
    except ImportError:
        print("  ! 未安装 Pillow，跳过 og-cover.png 生成")
        return

    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#211640")
    draw = ImageDraw.Draw(img)

    # 斜向渐变背景
    for y in range(H):
        k = y / H
        r = int(0x2c + (0x12 - 0x2c) * k)
        g = int(0x1d + (0x0d - 0x1d) * k)
        b = int(0x5c + (0x2a - 0x5c) * k)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # 柔光圆
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W - 420, -260, W + 260, 420], fill=(232, 96, 156, 70))
    gd.ellipse([-250, 380, 350, 900], fill=(96, 190, 220, 55))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 网格线（RGB 画布用三元组，避免 alpha 被忽略成纯白实线）
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(62, 54, 96), width=1)
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=(62, 54, 96), width=1)

    font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

    def font(size):
        for index in (2, 0, 1, 3):
            try:
                return ImageFont.truetype(font_path, size, index=index)
            except Exception:
                continue
        return ImageFont.load_default()

    f_big = font(84)
    f_mid = font(34)
    f_small = font(24)
    f_logo = font(30)

    # 左上角品牌
    draw.rounded_rectangle((72, 62, 124, 114), radius=15, fill=(103, 66, 201))
    draw.text((87, 70), "G", font=f_logo, fill="white")
    draw.text((140, 72), "Galwiki", font=f_mid, fill="#ffffff")

    # 主标题
    draw.text((72, 190), "Galgame 是什么？", font=f_big, fill="#ffffff")
    draw.text((72, 300), "一份给中文读者的完整地图", font=f_mid, fill="#e9d9ff")

    # 分隔线
    draw.rounded_rectangle((72, 388, 168, 394), radius=3, fill="#e8609c")

    # 副信息
    draw.text((72, 424), "定义  ·  发展简史  ·  作品图鉴  ·  术语词典", font=f_small, fill="#c9bce4")
    draw.text((72, 486), "不堆榜单  /  不谈资源  /  不剧透", font=f_small, fill="#9f92c2")

    # 右下角装饰
    draw.ellipse([W - 150, H - 150, W - 66, H - 66], outline=(126, 110, 172), width=2)
    draw.text((W - 128, H - 122), "VN", font=f_small, fill="#d9caff")

    img.save(out, "PNG", optimize=True)
    print(f"  ✓ og-cover.png ({W}×{H}, {out.stat().st_size // 1024} KB)")


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main() -> None:
    print(f"构建 {SITE['full_name']}  →  {ROOT}")
    print(f"域名：{SITE_URL}   构建日期：{TODAY}\n")

    for p in PAGES:
        (ROOT / p["file"]).write_text(render(p), encoding="utf-8")
        print(f"  ✓ {p['file']:<16} {p['schema']:<16} {len(strip_tags(p['body'])):>6} 字")

    idx = build_search_index()
    js = "/* 由 build.py 自动生成，请勿手工编辑 */\nwindow.GALWIKI_INDEX = " + \
         json.dumps(idx, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (ROOT / "search-index.js").write_text(js, encoding="utf-8")
    (ROOT / "search-index.json").write_text(
        json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ search-index.js / .json  ({len(idx)} 条索引)")

    write_sitemap()
    write_robots()
    write_rss()
    print("  ✓ sitemap.xml / robots.txt / rss.xml")
    make_og_image()
    print("\n构建完成。用 `python3 -m http.server 8080` 在本目录启动即可预览。")


if __name__ == "__main__":
    main()
