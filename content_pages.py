# -*- coding: utf-8 -*-
"""Galwiki 页面正文与页面元数据。

每页 body 为完整 HTML 片段；h2 的 id 与 toc 一一对应，
build.py 会据此生成桌面目录、移动端目录与 BreadcrumbList 之外的全部页面元素。
"""

from content_data import (
    SITE, NAV, WORKS, GLOSSARY, FAQ, TIMELINE, SOURCES, KEYWORD_CLOUD,
)


# ---------------------------------------------------------------------------
# 组件片段
# ---------------------------------------------------------------------------
def work_card(w):
    tags = "".join('<span class="tag">%s</span>' % t for t in w["tags"])
    return f"""
<article class="work" id="{w['id']}">
  <div class="work-badge" aria-hidden="true">{w['year'][:4]}</div>
  <div>
    <h3>{w['name']} <span class="visually-hidden">作品介绍</span></h3>
    <p class="work-sub">{w['alt']} · {w['studio']} · {w['year']} · {w['genre']} · 分级：{w['grade']}</p>
    <p>{w['desc']}</p>
    <p><strong>适合谁：</strong>{w['why']}</p>
    <div class="tags">{tags}</div>
  </div>
</article>"""


def works_list():
    return "\n".join(work_card(w) for w in WORKS)


def glossary_sections():
    out = []
    for group in GLOSSARY:
        cards = "\n".join(
            f'<div class="term" id="{tid}"><dt>{term}<small>{en}</small></dt><dd>{desc}</dd></div>'
            for tid, term, en, desc in group["terms"]
        )
        out.append(
            f'<section class="term-group" id="{group["id"]}">'
            f'<h2>{group["group"]}</h2>'
            f'<div class="term-grid"><dl style="display:contents">{cards}</dl></div>'
            f'</section>'
        )
    return "\n".join(out)


def faq_items(items=None, open_first=False):
    src = items if items is not None else FAQ
    out = []
    for i, item in enumerate(src):
        opened = " open" if (open_first and i == 0) else ""
        out.append(
            f'<details class="faq-item"{opened}><summary>{item["q"]}</summary>'
            f'<div class="answer"><p>{item["a"]}</p></div></details>'
        )
    return "\n".join(out)


def timeline_items():
    return "\n".join(
        f'<li id="{t["id"]}"><span class="year">{t["year"]}</span>'
        f'<h3>{t["title"]}</h3><p>{t["desc"]}</p></li>'
        for t in TIMELINE
    )


def sources_list():
    return "\n".join(
        f'<li><a href="{url}" rel="noopener noreferrer" target="_blank">{name}</a>'
        f'<span class="visually-hidden">（{note}）</span> — {note}</li>'
        for name, url, note in SOURCES
    )


def nav_cards(exclude=None):
    labels = {
        "guide.html": ("新手入门指南", "从选第一部到读懂路线系统，六步走完不踩坑。", "01"),
        "works.html": ("经典作品图鉴", "16 部剧情向作品：年份、厂商、题材与适合谁。", "02"),
        "history.html": ("四十年发展简史", "从 1985 到今天，11 个节点看清类型如何定型。", "03"),
        "glossary.html": ("术语词典", "路线、立绘、True End、FD……47 个词一次讲清。", "04"),
        "compare.html": ("概念辨析", "Galgame、视觉小说、AVG、乙女游戏到底差在哪。", "05"),
        "faq.html": ("常见问题", "15 个被问得最多的问题，集中回答。", "06"),
    }
    out = []
    for href, (title, desc, num) in labels.items():
        if href == exclude:
            continue
        out.append(
            f'<a class="card" href="{href}">'
            f'<span class="tag tag-brand">{num}</span>'
            f'<h3 style="margin-top:12px">{title}</h3><p>{desc}</p></a>'
        )
    return "\n".join(out)


def related_cards(files):
    meta = {f: label for f, label in NAV}
    descs = {
        "index.html": "从定义、历史到作品，一页建立整体印象",
        "guide.html": "六步入门法、按口味推荐表与通关时长参考",
        "works.html": "16 部剧情向作品的年份、厂商与看点",
        "history.html": "11 个节点串起四十年的类型演变",
        "glossary.html": "47 个术语，按概念 / 玩法 / 制作 / 发行分类",
        "compare.html": "Galgame、视觉小说、AVG 的对照表与用法建议",
        "faq.html": "15 个常见问题的集中解答",
        "about.html": "站点定位、内容边界与编辑方针",
    }
    return "\n".join(
        f'<a class="related-card" href="{f}"><strong>{meta.get(f, f)}</strong>'
        f'<span>{descs.get(f, "")}</span></a>'
        for f in files
    )


def related_block(files, title="继续阅读"):
    return f"""
<div class="related">
  <h2>{title}</h2>
  <div class="related-grid">{related_cards(files)}</div>
</div>"""


def cta_band(title="从一页开始，把这条脉络读完", text="先花五分钟搞清 Galgame 与视觉小说的关系，再按口味挑第一部，比直接翻榜单更有效。", primary=("guide.html", "打开入门指南"), secondary=("works.html", "浏览作品图鉴")):
    return f"""
<aside class="cta-band">
  <h2>{title}</h2>
  <p>{text}</p>
  <div class="hero-actions">
    <a class="btn btn-primary" href="{primary[0]}">{primary[1]} →</a>
    <a class="btn btn-ghost" href="{secondary[0]}">{secondary[1]}</a>
  </div>
</aside>"""


# ---------------------------------------------------------------------------
# 首页
# ---------------------------------------------------------------------------
TERM_COUNT = sum(len(g["terms"]) for g in GLOSSARY)

HOME_BODY = f"""
<section class="hero">
  <div class="hero-grid-overlay" aria-hidden="true"></div>
  <div class="container hero-inner">
    <span class="eyebrow">Galgame / Visual Novel 中文资料站</span>
    <h1>Galgame 是什么？<br><span class="grad">一份给中文读者的完整地图</span></h1>
    <p class="hero-lead">
      从 1994 年的《心跳回忆》到 Key 社、TYPE-MOON 的剧情向经典，<strong>这个以文字、立绘与音乐讲故事的载体，已经走过了四十年</strong>。
      Galwiki 用不剧透、可核查的方式，讲清它的定义、历史、术语与值得读的作品——不堆榜单，不谈资源，只帮你把路走明白。
    </p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="guide.html">新手从哪里开始 →</a>
      <a class="btn btn-ghost" href="compare.html">先搞清概念区别</a>
      <a class="btn btn-ghost" href="https://game123.download/" target="_blank" rel="noopener">galgame游戏资源获取 ↗</a>
    </div>
    <div class="hero-stats">
      <div><span class="num">40+</span><span class="label">年类型演变</span></div>
      <div><span class="num">{len(WORKS)}</span><span class="label">部作品收录</span></div>
      <div><span class="num">{TERM_COUNT}</span><span class="label">条术语释义</span></div>
      <div><span class="num">{len(FAQ)}</span><span class="label">个常见问题</span></div>
    </div>
  </div>
</section>

<section class="section" id="definition">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Definition · 定义</span>
      <h2>一句话说清 Galgame</h2>
      <p>它是「以角色关系为叙事驱动」的游戏类型，不是某个内容分级的代名词。把这三件事分开，后面所有概念就都不绕了。</p>
    </div>
    <div class="grid">
      <div class="card">
        <span class="tag tag-brand">它是什么</span>
        <h3 style="margin-top:12px">以文字叙事为核心的互动小说</h3>
        <p>用立绘、背景、配音与音乐表现场景，玩家通过阅读与选项推进剧情，与角色建立关系，走向不同结局。它在结构上属于<a href="compare.html#matrix">视觉小说</a>这一更大的门类。</p>
      </div>
      <div class="card">
        <span class="tag tag-pink">它不是什么</span>
        <h3 style="margin-top:12px">不等于限制级内容</h3>
        <p>分级与题材是两个维度。《CLANNAD》2004 年首发即为全年龄，Steam 上大量作品也是全年龄版。本站只讨论剧情与文化，<a href="about.html#boundary">内容边界见此</a>。</p>
      </div>
      <div class="card">
        <span class="tag tag-teal">为什么值得读</span>
        <h3 style="margin-top:12px">长文本才能承载的结构</h3>
        <p>多路线共同拼出世界观、伏笔跨线回收，是影视与动画较难复现的叙事方式。<a href="history.html#1999">1999 年前后的「泣系」</a>让这种可能性被真正看见。</p>
      </div>
    </div>
    <div class="callout" style="margin-top:26px">
      <p><strong>一句话版本：</strong>Galgame 是「和角色一起把故事读完」的游戏；视觉小说是它最常见的表现形式；全年龄 / 限制级只是发行分级。想要严格的术语对照，看 <a href="compare.html">概念辨析</a>。</p>
    </div>
  </div>
</section>

<section class="section section-alt" id="start">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Start here · 从哪开始</span>
      <h2>六个入口，按需挑一个</h2>
      <p>每个页面都独立成篇，也互相链接。第一次来，从「入门指南」或「概念辨析」开始最省时间。</p>
    </div>
    <div class="grid">{nav_cards()}</div>
  </div>
</section>

<section class="section" id="picks">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Editor's picks · 编辑精选</span>
      <h2>四部适合作为起点的作品</h2>
      <p>按「门槛低、有中文或全年龄版、能代表一种写法」挑出。完整 {len(WORKS)} 部请到 <a href="works.html">作品图鉴</a>。</p>
    </div>
    <div class="grid grid-2">
      <a class="card" href="works.html#steins-gate"><span class="tag tag-brand">科幻 · 全年龄</span><h3 style="margin-top:12px">命运石之门 <small>（2009）</small></h3><p>时间旅行设定与伏笔收束的范本，不太依赖恋爱要素，从悬疑小说转过来也顺。</p></a>
      <a class="card" href="works.html#summer-pockets"><span class="tag tag-teal">治愈 · 官方中文</span><h3 style="margin-top:12px">Summer Pockets <small>（2018）</small></h3><p>Key 社近年长篇里语言门槛最低的一部，Steam 版自 2022 年起支持中文。</p></a>
      <a class="card" href="works.html#planetarian"><span class="tag tag-pink">短篇 · 2–3 小时</span><h3 style="margin-top:12px">planetarian ～星之梦～ <small>（2004）</small></h3><p>几乎没有分支的电子小说，时间成本最低，适合先确认自己喜不喜欢这个载体。</p></a>
      <a class="card" href="works.html#clannad"><span class="tag tag-brand">长篇 · 剧情标杆</span><h3 style="margin-top:12px">CLANNAD <small>（2004）</small></h3><p>从校园写到家庭，把「家族」放进游戏结构里，是剧情向全年龄作品的里程碑。</p></a>
    </div>
  </div>
</section>

<section class="section section-alt" id="timeline-brief">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Timeline · 速览</span>
      <h2>五个年份，看懂来龙去脉</h2>
      <p>完整编年（含具体发售日期与厂商）在 <a href="history.html">发展简史</a>，这里只取最关键的转折点。</p>
    </div>
    <div class="table-wrap">
      <table>
        <caption class="visually-hidden">Galgame 发展史五个关键年份</caption>
        <thead><tr><th scope="col">年份</th><th scope="col">事件</th><th scope="col">改变了什么</th></tr></thead>
        <tbody>
          <tr><td><a href="history.html#1992">1992</a></td><td>élf《同级生》发售</td><td>「恋爱过程」第一次成为核心玩法</td></tr>
          <tr><td><a href="history.html#1994">1994</a></td><td>Konami《心跳回忆》发售</td><td>全年龄恋爱养成成型，类型出圈</td></tr>
          <tr><td><a href="history.html#1996">1996</a></td><td>Leaf《雫》提出「视觉小说」</td><td>文字叙事的表现形式被正式命名</td></tr>
          <tr><td><a href="history.html#1999">1999–2004</a></td><td>《Kanon》《AIR》《CLANNAD》</td><td>剧本本身成为卖点，全年龄转向</td></tr>
          <tr><td><a href="history.html#2014">2014 起</a></td><td>Steam 渠道与官方中文</td><td>海外读者第一次有了便捷正版入口</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="section" id="keywords">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Topics · 热门问题</span>
      <h2>大家都在搜什么</h2>
      <p>这些长尾问题都能在站内找到答案，点开即是对应章节。</p>
    </div>
    <div class="keyword-row">
      {''.join(f'<a href="{href}">{text}</a>' for text, href in KEYWORD_CLOUD)}
    </div>
  </div>
</section>

<section class="section section-alt" id="quick-faq">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Quick answers · 速答</span>
      <h2>三个最常被问到的问题</h2>
      <p>其余 {len(FAQ) - 3} 个问题整理在 <a href="faq.html">常见问题</a>。</p>
    </div>
    <div class="faq-list">{faq_items(FAQ[:3], open_first=True)}</div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="container">{cta_band()}</div>
</section>
"""


# ---------------------------------------------------------------------------
# 入门指南
# ---------------------------------------------------------------------------
GUIDE_BODY = f"""
<div class="prose">
  <p>很多人第一次接触 Galgame，是被一份「神作榜」劝退的：名字记不住、篇幅动辄几十小时、术语一窍不通，还怕踩到不适合自己的题材。这篇指南不推荐「最伟大的作品」，只帮你<strong>用最低成本确认自己要不要继续读下去</strong>。</p>

  <h2 id="step1">第一步：先确认这个载体适不适合你</h2>
  <p>Galgame 的核心体验是<strong>长时间、沉浸式的阅读</strong>。它与动画、小说的差别，在于你需要在关键节点做选择，并接受「一个周目只能看到一部分故事」。如果你喜欢读小说、愿意为伏笔等待，大概率会喜欢；如果你更想要即时反馈和操作感，可能会觉得节奏太慢。</p>
  <div class="callout"><p><strong>自测：</strong>你能不能接受连续两小时安静地读文字、听 BGM，并且暂时不知道结局？能，就往下走；不能，先试 <a href="works.html#planetarian">两小时的短篇</a>，成本最低。</p></div>

  <h2 id="step2">第二步：选平台与版本，别在下载上耗一整天</h2>
  <p>对中文读者来说，<strong>Steam 是目前最省事的入口</strong>：正版、价格友好、支持中文的作品越来越多，还能直接看商店页的分级与语言标注。主机与移动端则有官方移植版，适合不想坐在电脑前的读者。</p>
  <ul>
    <li><strong>优先官方中文版</strong>：翻译一致性、系统兼容性与后续更新都更稳，老作品的民间汉化常在新系统上遇到乱码或闪退。</li>
    <li><strong>看清分级标注</strong>：同一部作品可能同时有原版与全年龄版，商店页会明确写出，别只看标题。未成年人请选择全年龄版本。</li>
    <li><strong>确认支持平台</strong>：想用手机玩，就查官方是否出了 iOS / Android 版，而不是默认 PC 版可以随便搬过去。</li>
  </ul>
  <p>本站不提供任何下载、补丁或资源链接，只做资料整理与阅读引导。理由写在 <a href="about.html#boundary">内容边界</a> 里。</p>

  <h2 id="step3">第三步：按口味挑第一部，而不是按排名</h2>
  <p>下面这张表按「你想读到什么」来分，比按评分排序更实用。作品详情都可以在 <a href="works.html">作品图鉴</a> 里点开。</p>
  <div class="table-wrap">
    <table>
      <caption class="visually-hidden">按阅读口味推荐的第一部 Galgame</caption>
      <thead><tr><th scope="col">如果你想读…</th><th scope="col">建议从这部开始</th><th scope="col">理由</th></tr></thead>
      <tbody>
        <tr><td>硬核科幻、伏笔回收</td><td><a href="works.html#steins-gate">命运石之门</a>（2009）</td><td>设定严谨，恋爱要素少，前期慢热但后期爆发力强</td></tr>
        <tr><td>密室悬疑、叙述诡计</td><td><a href="works.html#ever17">Ever17</a>（2002）</td><td>多视角叙事的教科书，务必不要提前搜剧透</td></tr>
        <tr><td>短篇、两三个小时读完</td><td><a href="works.html#planetarian">星之梦</a> / <a href="works.html#atri">ATRI</a></td><td>篇幅短、情绪完整，适合试水</td></tr>
        <tr><td>情感长篇、有官方中文</td><td><a href="works.html#summer-pockets">Summer Pockets</a>（2018）</td><td>门槛低、节奏友好，Steam 版支持中文</td></tr>
        <tr><td>轻松日常、不想被虐</td><td><a href="works.html#senren-banka">千恋＊万花</a>（2016）</td><td>氛围明快，日常向作品的代表</td></tr>
        <tr><td>家族与人生、长线铺垫</td><td><a href="works.html#clannad">CLANNAD</a>（2004）</td><td>剧情向标杆，但需要投入较长阅读时间</td></tr>
        <tr><td>世界观与多路线结构</td><td><a href="works.html#fate-stay-night">Fate/stay night</a>（2004）</td><td>三条路线层层解锁设定，结构感极强</td></tr>
      </tbody>
    </table>
  </div>

  <h2 id="time">通关时长参考：先有个心理预期</h2>
  <div class="table-wrap">
    <table>
      <caption class="visually-hidden">不同类型作品的通关时长参考</caption>
      <thead><tr><th scope="col">篇幅</th><th scope="col">单条 / 单部时长</th><th scope="col">典型例子</th></tr></thead>
      <tbody>
        <tr><td>短篇电子小说</td><td>约 2–10 小时</td><td>《planetarian ～星之梦～》《ATRI》</td></tr>
        <tr><td>中等篇幅单线</td><td>约 10–20 小时</td><td>多数日常向作品的单个角色线</td></tr>
        <tr><td>长篇全路线</td><td>约 50–100 小时</td><td>《CLANNAD》《白色相簿2》</td></tr>
      </tbody>
    </table>
  </div>
  <p>数字只是量级参考，实际差异很大。善用 <a href="glossary.html#skip">Skip（跳过已读）</a> 能在多周目时省下大量重复阅读时间。</p>

  <h2 id="step4">第四步：花十分钟认识基本系统</h2>
  <p>不需要背术语，只要知道四件事就能顺畅玩下去：</p>
  <ol>
    <li><strong>存档 / 读档</strong>：在关键选项前存一次，想看另一条分支直接读回来，不用重开。</li>
    <li><strong>共通线与个人线</strong>：前半段是所有角色共享的剧情，之后才分岔到 <a href="glossary.html#route">路线</a>。</li>
    <li><strong>结局类型</strong>：<a href="glossary.html#true-end">True End</a> 往往要通关其他路线后才解锁，别以为第一个结局就是全部。</li>
    <li><strong>Backlog 与 Auto</strong>：一个用来回看文本，一个用来自动推进，按自己的阅读节奏选。</li>
  </ol>
  <p>完整 47 条释义在 <a href="glossary.html">术语词典</a>，遇到不认识的词再查也来得及。</p>

  <h2 id="step5">第五步：建立自己的阅读节奏</h2>
  <p>建议戴耳机、留整块时间，别用「刷短视频」的方式快进——这个类型的情绪铺垫常常藏在日常对话里。遇到觉得慢的段落，先判断是不是在铺伏笔；多数长篇前半段的闲笔，后半段都会回来。</p>
  <blockquote><p>「不要急着跳过对话」几乎是所有老玩家给新人的第一条建议。这里的信息密度，往往比画面上看起来高。</p></blockquote>

  <h2 id="step6">第六步：避坑与社区礼仪</h2>
  <ul>
    <li><strong>防剧透</strong>：<a href="works.html#ever17">Ever17</a>、<a href="works.html#steins-gate">命运石之门</a> 这类作品的核心乐趣就是反转，查资料时尽量只看无剧透介绍。</li>
    <li><strong>别迷信「神作榜」</strong>：口味差异极大，榜单前列的长篇未必适合作为第一部。</li>
    <li><strong>支持正版</strong>：官方中文版与数字平台让这个市场还能继续运转，也省去兼容性与安全风险。</li>
    <li><strong>分级自觉</strong>：看清商店分级，未成年人选择全年龄版本；本站不收录、不讨论限制级内容。</li>
  </ul>
  <p>还有具体疑问，多半能在 <a href="faq.html">常见问题</a> 里找到；想搞清「Galgame 和视觉小说到底差在哪」，去看 <a href="compare.html">概念辨析</a>。</p>

  {related_block(['works.html', 'compare.html', 'glossary.html', 'faq.html'])}
  {cta_band('准备好挑第一部了吗？', '按口味对照作品图鉴，比按排名硬啃轻松得多。', ('works.html', '打开作品图鉴'), ('faq.html', '先看常见问题'))}
</div>
"""


# ---------------------------------------------------------------------------
# 作品图鉴
# ---------------------------------------------------------------------------
WORKS_BODY = f"""
<div class="prose">
  <p>这份图鉴收录 <strong>{len(WORKS)} 部剧情向作品</strong>，筛选标准是：在类型史上有明确位置、以剧本或叙事结构见长、且<strong>存在全年龄版本或本身即为全年龄定位</strong>。它不是评分榜，也不排名——目的是让你在读到某个名字时，能迅速知道「它讲什么、谁做的、为什么常被提起、适不适合我」。</p>

  <div class="callout">
    <p><strong>关于分级：</strong>部分作品的原版含限制级内容，但另有全年龄版或全年龄移植版；表中「分级」一列已标注。本站只讨论剧情、结构与文化背景，不收录、不描述限制级内容，也不提供任何下载或补丁。购买前请以官方商店的分级与语言标注为准，未成年人请选择全年龄版本。</p>
  </div>

  <h2 id="how">怎么读这份图鉴</h2>
  <p>每张卡片给出四类信息：<strong>发行年份、制作 / 发行厂商、题材与分级、以及「适合谁」</strong>。年份指的是该作品最初发售的年份，不是移植或中文化的年份；若一部作品分序章与终章（如《白色相簿2》），会写成区间。想了解某部作品在整个类型史里的位置，可以对照 <a href="history.html">发展简史</a> 的编年表一起看。</p>

  <h2 id="list">作品列表（{len(WORKS)} 部）</h2>
  <div class="work-list">
    {works_list()}
  </div>

  <h2 id="by-genre">按题材速查</h2>
  <div class="table-wrap">
    <table>
      <caption class="visually-hidden">按题材分类的作品速查表</caption>
      <thead><tr><th scope="col">题材方向</th><th scope="col">代表作品</th><th scope="col">阅读提示</th></tr></thead>
      <tbody>
        <tr><td>催泪 / 情感</td><td><a href="works.html#kanon">Kanon</a>、<a href="works.html#air">AIR</a>、<a href="works.html#clannad">CLANNAD</a>、<a href="works.html#summer-pockets">Summer Pockets</a></td><td>Key 社「季节组曲」脉络，日常铺垫较长，情绪在后半段集中释放</td></tr>
        <tr><td>科幻 / 悬疑</td><td><a href="works.html#steins-gate">命运石之门</a>、<a href="works.html#ever17">Ever17</a>、<a href="works.html#planetarian">星之梦</a></td><td>强依赖伏笔与反转，务必避开剧透</td></tr>
        <tr><td>奇幻 / 世界观</td><td><a href="works.html#fate-stay-night">Fate/stay night</a>、<a href="works.html#mahoutsukai-no-yoru">魔法使之夜</a>、<a href="works.html#rewrite">Rewrite</a></td><td>多路线共同拼出设定，单线读完通常不等于读完全部</td></tr>
        <tr><td>恋爱 / 群像</td><td><a href="works.html#white-album-2">白色相簿2</a>、<a href="works.html#memories-off">秋之回忆</a>、<a href="works.html#atri">ATRI</a></td><td>重点在人物关系的细腻变化，而非设定规模</td></tr>
        <tr><td>青春 / 友情</td><td><a href="works.html#little-busters">Little Busters!</a>、<a href="works.html#clannad">CLANNAD</a></td><td>群像调度是看点，适合喜欢伙伴戏的读者</td></tr>
        <tr><td>轻松日常</td><td><a href="works.html#senren-banka">千恋＊万花</a>、<a href="works.html#atri">ATRI</a></td><td>篇幅与情绪压力都较小，适合作为第一部</td></tr>
        <tr><td>历史坐标</td><td><a href="works.html#tokimeki-memorial">心跳回忆</a>、<a href="works.html#memories-off">秋之回忆</a></td><td>更接近养成模拟或早期全年龄恋爱冒险，读的是类型如何定型</td></tr>
      </tbody>
    </table>
  </div>

  <h2 id="grade">「全年龄版」到底怎么看</h2>
  <p>同一部作品存在多个版本是很常见的事：原版、全年龄版、主机移植版、国际平台版，彼此可能在文本、CG、分级与语言上都有差异。多数情况下，全年龄版会删去限制级段落并做衔接，主线结构不变；也有厂商会补写剧情或新增插画。少数作品的情感铺陈会因此受影响，所以<strong>看版本说明，不要只看标题</strong>。相关术语见 <a href="glossary.html#release">「版本与发行」</a> 一节。</p>
  <p>如果你还没决定从哪部开始，<a href="guide.html#step3">入门指南的按口味推荐表</a> 更直接；想先弄明白「Galgame」这个词到底涵盖什么，看 <a href="compare.html">概念辨析</a>。</p>

  {related_block(['guide.html', 'history.html', 'glossary.html', 'compare.html'])}
  {cta_band('还没选好第一部？', '六步入门法里有一张按口味分类的推荐表，两分钟就能定位。', ('guide.html', '打开入门指南'), ('faq.html', '查看常见问题'))}
</div>
"""


# ---------------------------------------------------------------------------
# 发展简史
# ---------------------------------------------------------------------------
HISTORY_BODY = f"""
<div class="prose">
  <p>把 Galgame 的四十年压缩成一句话：<strong>它从「以美少女角色为卖点的电脑游戏」，一步步变成了「用长文本承载复杂叙事的互动小说」，再借数字发行走向全球中文读者</strong>。下面按 11 个节点串起这条线，关键发售日期均经多来源交叉核对，参考来源列在文末。</p>

  <h2 id="overview">先看清脉络：三次转向</h2>
  <div class="table-wrap">
    <table>
      <caption class="visually-hidden">Galgame 发展史的三次结构性转向</caption>
      <thead><tr><th scope="col">阶段</th><th scope="col">时间</th><th scope="col">核心变化</th></tr></thead>
      <tbody>
        <tr><td>玩法定型</td><td>1985–1994</td><td>文字冒险 + 角色互动 → 恋爱过程成为核心 → 全年龄恋爱养成出圈</td></tr>
        <tr><td>叙事升级</td><td>1996–2006</td><td>视觉小说命名、泣系确立、同人社团崛起，剧本取代尺度成为主要卖点</td></tr>
        <tr><td>渠道重构</td><td>2014 至今</td><td>本土市场收缩，Steam / 主机 / 官方中文打开海外增量</td></tr>
      </tbody>
    </table>
  </div>

  <h2 id="timeline">编年：11 个关键节点</h2>
  <ol class="timeline">
    {timeline_items()}
  </ol>

  <h2 id="names">几个容易被搞混的年份</h2>
  <p>网上的中文资料常把这几个时间点写错，这里单独说明，便于你核对其他来源：</p>
  <ul>
    <li><strong>《同级生》是 1992 年 12 月 17 日</strong>，1995 年 1 月 31 日发售的是《同级生 2》。有的行业报告把《同级生》写成 1995 年，属于与续作混淆。</li>
    <li><strong>Key 社成立于 1998 年 7 月 21 日</strong>，但处女作《Kanon》发售于 <strong>1999 年 6 月 4 日</strong>。「1998 年成立并推出 Kanon」是常见的合并误写。</li>
    <li><strong>《ONE ～光辉的季节～》属于 Tactics 社</strong>（1998 年 5 月 29 日），是 Key 社成立前由原班人马完成的作品，不是 Key 社作品。</li>
    <li><strong>《心跳回忆》首发于 1994 年 5 月 27 日的 PC Engine 平台</strong>，后续 PlayStation、世嘉土星、Windows 版本属于移植，年份各不相同。</li>
  </ul>

  <h2 id="market">行业规模：本土收缩，不等于类型消失</h2>
  <p>公开报道中较常被引用的是矢野经济研究所的统计：日本相关市场规模从 2003 年约 <strong>560 亿日元</strong>的高点，到 2015 年缩减至约 <strong>150 亿日元</strong>量级。多家媒体把原因归结为几个叠加因素：智能手机与手游重新分配了娱乐时间、单机长文本的时间与价格门槛偏高、优秀剧本家转向轻小说与动画编剧，以及盗版与渠道变化。</p>
  <p>但另一面是，2014 年后 Steam 等国际平台让旧作与新作都获得了二次生命周期，官方中文与主机移植显著降低了中文读者的门槛。所以更准确的说法是<strong>「本土收缩、全球重构」</strong>：厂商数量在减少，可被读到的作品反而变多了。</p>

  <h2 id="china">中文圈与国产作品</h2>
  <p>早期中文读者主要依靠民间汉化与社区交流接触这个类型，<a href="works.html#clannad">《CLANNAD》</a>、<a href="works.html#fate-stay-night">《Fate/stay night》</a> 等作品的动画改编也起到了重要的「入口」作用。2014 年之后，国内同人团队陆续推出中文原创作品，例如《高考恋爱一百天》《三色绘恋》，多以校园与本土生活经验为题材，并常以低价策略在数字平台发行。近年官方中文版本增多，又进一步改变了阅读门槛。</p>

  <h2 id="sources">资料来源</h2>
  <p>本页的年份、日期与厂商信息以以下公开资料交叉核对；涉及具体版本与分级，仍请以发行方公告与官方商店页为准。</p>
  <ul>{sources_list()}</ul>
  <p>想顺着年份去找作品，可以直接跳到 <a href="works.html">作品图鉴</a>；想弄懂文里出现的「泣系」「视觉小说」「全年龄版」，看 <a href="glossary.html">术语词典</a>。</p>

  {related_block(['works.html', 'compare.html', 'guide.html', 'about.html'])}
  {cta_band('把作品放回它的年代', '知道一部作品诞生在什么节点，往往比看评分更能判断自己会不会喜欢。', ('works.html', '浏览作品图鉴'), ('guide.html', '回到入门指南'))}
</div>
"""


# ---------------------------------------------------------------------------
# 术语词典
# ---------------------------------------------------------------------------
GLOSSARY_BODY = f"""
<div class="prose">
  <p>这个圈子的缩写和日语借词特别多，但它们大多只是在描述<strong>「故事怎么组织」「画面怎么构成」「版本怎么发行」</strong>。这里把 {TERM_COUNT} 个高频词按五组整理，每条一句话讲清，不堆黑话。</p>

  <h2 id="how">怎么用这份词典</h2>
  <p>按 <code>Ctrl/⌘ + K</code> 可以直接搜词条与全站页面；桌面端右侧目录可跳转到各分组。想理解词与词之间的关系，比如「共通线 → 路线 → True End」这条链，建议配合 <a href="guide.html#step4">入门指南第四步</a> 一起读。概念层面的辨析（Galgame / 视觉小说 / AVG）放在 <a href="compare.html">概念辨析</a> 页。</p>

  {glossary_sections()}

  <h2 id="next">查完之后</h2>
  <p>术语只是路标。真正决定体验的还是作品本身：<a href="works.html">作品图鉴</a> 里每部作品都标了题材与适合人群；<a href="history.html">发展简史</a> 则能告诉你这些说法分别是在哪个年代出现的。</p>

  {related_block(['compare.html', 'guide.html', 'works.html', 'faq.html'])}
  {cta_band('想找某个具体说法？', '15 个常见问题里覆盖了不少「这词到底什么意思」的实战场景。', ('faq.html', '查看常见问题'), ('compare.html', '看概念对照表'))}
</div>
"""


# ---------------------------------------------------------------------------
# 概念辨析
# ---------------------------------------------------------------------------
COMPARE_BODY = f"""
<div class="prose">
  <p>「Galgame」「视觉小说」「AVG」「乙女游戏」这几个词在中文互联网上经常混着用，吵了二十年也没吵出统一答案。原因不复杂：<strong>它们描述的根本不是同一个维度</strong>——有的说题材与受众，有的说表现形式，有的说玩法框架。下面先把维度拆开，再给一张对照表。</p>

  <h2 id="why">为什么会混用</h2>
  <p>历史上这些名称是不同厂商在不同年代为了定位自己的产品而提出来的：Chunsoft 用「音效小说」强调声音氛围，Leaf 在 1996 年用「视觉小说」强调文字覆盖画面的读法，Konami 用「全年龄恋爱养成」强调玩法与分级。等到中文圈一次性接触这些作品时，它们已经被打包成同一个「品类」，于是名称自然就叠在了一起。</p>
  <blockquote><p>可以粗略记成：<strong>Galgame 说「这是什么类型的作品」，视觉小说说「它以什么形式呈现」，AVG / ADV 说「它的玩法框架」，全年龄 / 限制级说「它怎么分级」</strong>。</p></blockquote>

  <h2 id="matrix">概念对照表</h2>
  <div class="table-wrap">
    <table>
      <caption class="visually-hidden">Galgame 及相邻概念对照表</caption>
      <thead><tr><th scope="col">概念</th><th scope="col">描述的是</th><th scope="col">核心特征</th><th scope="col">代表作品 / 厂商</th></tr></thead>
      <tbody>
        <tr><td><strong>Galgame（美少女游戏）</strong></td><td>题材与受众</td><td>以女性角色与角色关系为叙事驱动，常有攻略目标</td><td>《同级生》élf、《心跳回忆》Konami</td></tr>
        <tr><td><strong>视觉小说 VN</strong></td><td>表现形式</td><td>文字为主体、覆盖画面，配立绘 / 背景 / 音乐；分支可多可少</td><td>《雫》Leaf、Key 社作品</td></tr>
        <tr><td><strong>AVG / ADV（文字冒险）</strong></td><td>玩法框架</td><td>读文本 + 做选择 + 触发分支与结局，强调「选项」</td><td>《Ever17》KID、《命运石之门》5pb.</td></tr>
        <tr><td><strong>恋爱模拟 / 养成</strong></td><td>玩法框架</td><td>以日程安排、数值与好感度推进关系，文本量相对克制</td><td>《心跳回忆》Konami</td></tr>
        <tr><td><strong>乙女游戏</strong></td><td>目标受众</td><td>玩法结构相近，但视角与攻略对象相反</td><td>面向女性玩家的恋爱冒险作品</td></tr>
        <tr><td><strong>音效小说 Sound Novel</strong></td><td>表现形式（先驱）</td><td>强调音效与氛围烘托，是视觉小说概念的前身</td><td>《弟切草》Chunsoft</td></tr>
        <tr><td><strong>全年龄 / 限制级</strong></td><td>发行分级</td><td>与上述所有维度正交，同一作品可能有多个版本</td><td>《CLANNAD》全年龄版、Steam 版</td></tr>
      </tbody>
    </table>
  </div>

  <h2 id="vn">Galgame vs 视觉小说：最常被问的一对</h2>
  <p>按 Leaf 社最初的用法，「视觉小说」特指<strong>文字铺满整个画面、背景 CG 被文字层覆盖</strong>的表现方式，用以区别传统「文字放在底部对话框」的 AVG。也就是说，视觉小说原本是 AVG 的一个子类，而不是与 AVG 并列的大类。</p>
  <p>后来英文语境里的 <em>Visual Novel</em> 含义扩大，几乎成了「日式文字叙事游戏」的统称；中文圈也跟着把两者当同义词用。于是今天的实际情况是：<strong>绝大多数 Galgame 都是视觉小说，但并非所有视觉小说都是 Galgame</strong>——比如几乎没有攻略要素、只讲一个故事的 <a href="works.html#planetarian">《planetarian ～星之梦～》</a>，或者推理、恐怖题材的文字冒险作品。</p>
  <div class="callout"><p><strong>实用建议：</strong>日常交流里混用完全没问题；写资料、做索引或跟人争论时，先说明自己用的是「表现形式」还是「题材类型」，能省掉大半误会。</p></div>

  <h2 id="adv">AVG / ADV / 恋爱模拟：差别在「玩家做什么」</h2>
  <p>AVG（Adventure Game，日式也写 ADV）字面是冒险游戏，早期范围很宽；在这个品类里通常指<strong>通过阅读与选项推进剧情</strong>的文字冒险。恋爱模拟（Dating Sim）则更接近养成：安排日程、提升数值、触发事件，<a href="works.html#tokimeki-memorial">《心跳回忆》</a>是典型。1990 年代中期之前这两条线还分得比较清楚，之后逐渐合流——现代作品往往既有大量文本，也保留好感度与分支。</p>
  <p>顺带一提，<a href="glossary.html#structure">「路线」「flag」「True End」</a>这些词主要来自文字冒险这一侧；「好感度」「参数」更多来自养成那一侧。</p>

  <h2 id="audience">乙女游戏与分级：两个独立的坐标轴</h2>
  <p><strong>乙女游戏</strong>面向女性玩家、以男性角色为攻略对象，玩法框架与 Galgame 高度相似，可视为同一套结构在不同受众上的延伸，不属于 Galgame 的子集。</p>
  <p><strong>分级</strong>则完全独立于以上所有分类。这个品类里既有全年龄定位的作品，也有原版与全年龄版并行的情况；Steam 等国际平台上架的以全年龄版为主。把「Galgame」直接等同于限制级内容，既不准确，也会让很多优秀作品被误读。本站只讨论剧情与文化，未成年人请选择明确标注全年龄的版本。</p>

  <h2 id="usage">中文语境用法速查</h2>
  <div class="table-wrap">
    <table>
      <caption class="visually-hidden">中文语境下不同场景的推荐用词</caption>
      <thead><tr><th scope="col">场景</th><th scope="col">推荐用词</th><th scope="col">原因</th></tr></thead>
      <tbody>
        <tr><td>向完全没接触过的人解释</td><td>「互动小说 / 文字冒险游戏」</td><td>避免生造词，直接说清阅读体验</td></tr>
        <tr><td>强调攻略角色、多结局</td><td>Galgame / 恋爱冒险</td><td>突出目标导向与分支结构</td></tr>
        <tr><td>强调文本与阅读形式</td><td>视觉小说</td><td>与动画、漫画等媒介做区分</td></tr>
        <tr><td>在英文社区检索</td><td>Visual Novel / VN</td><td>英文语境的通用叫法，检索结果更全</td></tr>
        <tr><td>讨论版本与购买</td><td>写清「全年龄版 / 官方中文版」</td><td>避免把不同版本当成同一件商品</td></tr>
      </tbody>
    </table>
  </div>
  <p>想从具体作品入手理解这些区别，<a href="works.html">作品图鉴</a> 里按题材做了分类；对名称的来历感兴趣，可以看 <a href="history.html#1996">发展简史 1996 年那一节</a>。</p>

  {related_block(['glossary.html', 'guide.html', 'faq.html', 'history.html'])}
  {cta_band('概念清楚了，接下来挑作品', '按题材与门槛筛一遍，比在名词里打转更有效。', ('works.html', '打开作品图鉴'), ('glossary.html', '查术语词典'))}
</div>
"""


# ---------------------------------------------------------------------------
# 常见问题
# ---------------------------------------------------------------------------
FAQ_BODY = f"""
<div class="prose">
  <p>这里集中回答 <strong>{len(FAQ)} 个被问得最多的问题</strong>，尽量给结论、给依据、给下一步去哪看，不绕弯子。按 <code>Ctrl/⌘ + K</code> 可以搜索全站页面与词条。</p>

  <h2 id="list">全部问答</h2>
  <div class="faq-list">{faq_items(FAQ, open_first=True)}</div>

  <h2 id="more">没找到答案？</h2>
  <p>如果是「某个词是什么意思」，多半在 <a href="glossary.html">术语词典</a>；如果是「某部作品讲什么」，去 <a href="works.html">作品图鉴</a>；如果是「我该从哪部开始」，<a href="guide.html#step3">入门指南的按口味推荐表</a> 最直接。想核对某个年份或说法的来历，<a href="history.html#sources">发展简史附有资料来源</a>。</p>
  <p>本站是纯资料站，不提供下载、补丁、剧透式攻略，也不收录限制级内容；作品信息请以发行方公告与官方商店页为准。</p>

  {related_block(['guide.html', 'compare.html', 'glossary.html', 'about.html'])}
  {cta_band('从一份不劝退的书单开始', '入门指南把「选第一部」拆成了六个步骤，照着走就行。', ('guide.html', '打开入门指南'), ('works.html', '浏览作品图鉴'))}
</div>
"""


# ---------------------------------------------------------------------------
# 关于本站
# ---------------------------------------------------------------------------
ABOUT_BODY = f"""
<div class="prose">
  <p>Galwiki 是一个<strong>面向中文读者的 Galgame 与视觉小说文化科普站</strong>。它不追热点、不做榜单、不提供资源，只做一件看似笨拙的事：把这个类型里容易混淆的概念、容易被写错的年份、以及值得读的作品，整理成一套能长期查阅的中文资料。</p>

  <h2 id="position">站点定位</h2>
  <p>中文互联网上关于 Galgame 的内容很多，但常见两种极端：一种是社区内部的黑话讨论，新人看不懂；一种是批量生成的「推荐大全」，事实错漏、年份混用、堆砌关键词。Galwiki 想补上中间那一层——<strong>定义清楚、来源可查、不剧透、对新人友好，同时不牺牲准确性</strong>。</p>
  <p>目前共 {len(NAV) - 1} 个内容页：入门指南、作品图鉴、发展简史、术语词典、概念辨析、常见问题，加上你正在读的这一页。各页之间互相链接，可以从任意一页进入。</p>

  <h2 id="boundary">内容边界（请先读这一段）</h2>
  <ul>
    <li><strong>不收录、不描述限制级内容。</strong>本站只讨论剧情、结构、历史与文化背景；作品图鉴只收录有全年龄版本或本身为全年龄定位的剧情向作品。</li>
    <li><strong>不提供游戏下载、汉化补丁、破解或攻略。</strong>所有版本与购买信息请通过官方商店与发行方渠道获取。</li>
    <li><strong>不做剧透式介绍。</strong>涉及悬疑、反转类作品时，只讲题材与结构，不写关键情节。</li>
    <li><strong>分级提示。</strong>同一作品可能存在多个版本，表中分级仅供参考，请以官方商店标注为准；未成年人请选择全年龄版本。</li>
    <li><strong>面向全年龄读者写作。</strong>内容适合一般读者与家长查阅，用于了解这一游戏文化类型。</li>
  </ul>
  <div class="callout"><p><strong>为什么这样设边界？</strong>一是让读者不必担心版权与安全风险；二是让内容能长期稳定地被引用与检索；三是把一个常被误解的类型，放回它作为「互动叙事载体」的位置上讨论。</p></div>

  <h2 id="editorial">编辑方针</h2>
  <ol>
    <li><strong>事实交叉核对</strong>：涉及发售日期、厂商、成立年份的信息，至少比对两个独立公开来源；来源清单公开在 <a href="history.html#sources">发展简史</a> 与下方。</li>
    <li><strong>主动标注争议</strong>：像「第一部 Galgame」「Key 社成立与处女作年份」这类常被写错的地方，单独列出说明，不假装只有一种说法。</li>
    <li><strong>区分事实与观点</strong>：年份、厂商、平台属于事实；「适合谁」「值得读吗」属于编辑判断，行文上会明确区分。</li>
    <li><strong>内容与视觉分离</strong>：全站为静态 HTML，术语与作品数据集中维护，便于持续修订而不破坏页面结构。</li>
    <li><strong>持续更新</strong>：发现资料有误或版本信息变化时会修订，页面会同步更新修改日期。</li>
  </ol>

  <h2 id="privacy">隐私与技术</h2>
  <p>本站是<strong>零依赖的纯静态站点</strong>：没有第三方统计脚本、没有广告 SDK、没有追踪 Cookie、没有外部字体与 CDN 请求。站内搜索的索引随页面一起加载，查询只发生在你的浏览器里，不会上传任何输入。主题偏好保存在浏览器本地存储中。</p>
  <p>技术上使用语义化 HTML5、CSS 自定义属性与原生 JavaScript，配套 sitemap.xml、robots.txt、RSS 与 JSON-LD 结构化数据；支持亮 / 暗主题、键盘导航、跳转正文链接、减少动效偏好与打印样式。</p>

  <h2 id="sources">主要参考资料</h2>
  <ul>{sources_list()}</ul>
  <p>作品名称、角色与相关商标归各自权利人所有；本站仅作介绍性与评论性使用。若发现事实错误或需要补充出处，欢迎通过下方方式反馈。</p>

  <h2 id="contact">联系与反馈</h2>
  <p>内容勘误、来源补充、词条建议，都可以发到 <a href="mailto:hello@galgameinfowiki.github.io">hello@galgameinfowiki.github.io</a>。 Typo、年份错误这类问题尤其欢迎指出——这类资料站的价值，很大程度来自长期校对。</p>

  {related_block(['history.html', 'faq.html', 'compare.html', 'index.html'])}
  {cta_band('从定义开始读起', '如果还没逛过其他页面，首页是最短的一条路径。', ('index.html', '返回首页'), ('guide.html', '打开入门指南'))}
</div>
"""


# ---------------------------------------------------------------------------
# 404
# ---------------------------------------------------------------------------
NOTFOUND_BODY = """
<div class="prose" style="text-align:center; padding-block:40px">
  <p class="eyebrow" style="justify-content:center">404 · Not Found</p>
  <p>链接可能已经移动，或者地址里有笔误。别担心，站内内容都在下面这几个入口里。</p>
  <p style="margin-top:26px"><a class="btn btn-primary" href="index.html">返回首页</a></p>
  <div class="grid" style="margin-top:40px;text-align:left">
    <a class="card" href="guide.html"><h3>入门指南</h3><p>六步走完，从选第一部到读懂路线系统。</p></a>
    <a class="card" href="works.html"><h3>作品图鉴</h3><p>16 部剧情向作品的年份、厂商与看点。</p></a>
    <a class="card" href="glossary.html"><h3>术语词典</h3><p>47 个高频词，按五组集中讲清。</p></a>
  </div>
</div>
"""


# ---------------------------------------------------------------------------
# 页面元数据表
# ---------------------------------------------------------------------------
PAGES = [
    {
        "file": "index.html", "kind": "home",
        "title": "Galgame 是什么？视觉小说入门、经典作品与发展简史 | Galwiki",
        "description": "Galgame 是什么？用不剧透、可核查的方式讲清定义、与视觉小说的区别、四十年发展简史和 16 部剧情向经典作品，附新手入门指南、术语词典与常见问题。",
        "keywords": "galgame,galgame是什么,美少女游戏,视觉小说,galgame入门,galgame推荐,galgame发展史,Visual Novel",
        "h1": "Galgame 是什么？一份给中文读者的完整地图",
        "lead": "从定义、历史、术语到作品，一份不堆榜单、不谈资源的中文入门地图。",
        "eyebrow": "Galgame / Visual Novel 中文资料站",
        "schema": "WebPage", "priority": "1.0", "changefreq": "weekly",
        "toc": [], "related": [], "body": HOME_BODY,
    },
    {
        "file": "guide.html", "kind": "article",
        "title": "Galgame 新手入门指南：第一部怎么选、要玩多久、怎么避坑 | Galwiki",
        "description": "第一次玩 Galgame 该从哪部开始？六步入门法：确认载体是否适合你、选平台与官方中文版、按口味挑第一部、通关时长参考、认识路线与存档系统、避坑与社区礼仪。",
        "keywords": "galgame入门,galgame新手,galgame推荐,第一部galgame,galgame通关时长,galgame平台,官方中文",
        "h1": "Galgame 新手入门指南",
        "lead": "不推荐「最伟大的作品」，只帮你用最低成本确认：这个以阅读为核心的载体，适不适合你。",
        "eyebrow": "Guide · 入门指南",
        "schema": "Article", "priority": "0.9", "changefreq": "monthly",
        "toc": [("step1", "确认载体是否适合你"), ("step2", "选平台与版本"), ("step3", "按口味挑第一部"),
                ("time", "通关时长参考"), ("step4", "认识基本系统"), ("step5", "建立阅读节奏"),
                ("step6", "避坑与社区礼仪")],
        "related": ["works.html", "compare.html", "glossary.html", "faq.html"],
        "body": GUIDE_BODY,
    },
    {
        "file": "works.html", "kind": "article",
        "title": "Galgame 经典作品图鉴：16 部剧情向作品与全年龄版本说明 | Galwiki",
        "description": "16 部剧情向 Galgame 资料：CLANNAD、命运石之门、Ever17、白色相簿2、Summer Pockets、Fate/stay night 等的发售年份、厂商、题材、分级与适合人群，并说明全年龄版怎么看。",
        "keywords": "galgame推荐,galgame神作,经典galgame,全年龄galgame,剧情向galgame,CLANNAD,命运石之门,Key社作品",
        "h1": "Galgame 经典作品图鉴",
        "lead": "16 部有全年龄版本或全年龄定位的剧情向作品：年份、厂商、题材、看点与适合谁。",
        "eyebrow": "Works · 作品图鉴",
        "schema": "CollectionPage", "priority": "0.9", "changefreq": "monthly",
        "toc": [("how", "怎么读这份图鉴"), ("list", "作品列表"), ("by-genre", "按题材速查"), ("grade", "「全年龄版」怎么看")],
        "related": ["guide.html", "history.html", "glossary.html", "compare.html"],
        "body": WORKS_BODY,
    },
    {
        "file": "history.html", "kind": "article",
        "title": "Galgame 发展简史：从 1985 到今天的 11 个关键节点 | Galwiki",
        "description": "Galgame 四十年发展史编年：1985 萌芽、1992《同级生》、1994《心跳回忆》、1996 视觉小说命名、1998 Key 社成立、2004《CLANNAD》全年龄转向、2014 Steam 渠道，附资料来源与常见年份勘误。",
        "keywords": "galgame发展史,galgame历史,美少女游戏历史,心跳回忆1994,Key社成立,CLANNAD全年龄,Steam galgame",
        "h1": "Galgame 发展简史",
        "lead": "从「以美少女角色为卖点的电脑游戏」到「用长文本承载复杂叙事」，11 个节点串起四十年。",
        "eyebrow": "History · 发展简史",
        "schema": "Article", "priority": "0.8", "changefreq": "monthly",
        "toc": [("overview", "三次转向"), ("timeline", "编年：11 个节点"), ("names", "容易被搞混的年份"),
                ("market", "行业规模与收缩"), ("china", "中文圈与国产作品"), ("sources", "资料来源")],
        "related": ["works.html", "compare.html", "guide.html", "about.html"],
        "body": HISTORY_BODY,
    },
    {
        "file": "glossary.html", "kind": "article",
        "title": "Galgame 术语词典：47 个高频词一次讲清 | Galwiki",
        "description": "Galgame 常用术语大全：路线、共通线、flag、True End、立绘、CG、差分、FD、泣きゲー、全年龄版等 47 个词，按基础概念、玩法结构、美术制作、版本发行、社区用语五组整理。",
        "keywords": "galgame术语,galgame名词,共通线,个人线,True End,立绘,CG,FD,泣きゲー,AVG,ADV",
        "h1": "Galgame 术语词典",
        "lead": "47 个高频词，按五组整理：概念、玩法、美术与制作、版本发行、社区用语。",
        "eyebrow": "Glossary · 术语词典",
        "schema": "DefinedTermSet", "priority": "0.8", "changefreq": "monthly",
        "toc": [("how", "怎么用这份词典")] + [(g["id"], g["group"]) for g in GLOSSARY] + [("next", "查完之后")],
        "related": ["compare.html", "guide.html", "works.html", "faq.html"],
        "body": GLOSSARY_BODY,
    },
    {
        "file": "compare.html", "kind": "article",
        "title": "Galgame 和视觉小说的区别：AVG、ADV、乙女游戏概念辨析 | Galwiki",
        "description": "Galgame 和视觉小说有什么区别？AVG、ADV、恋爱模拟、乙女游戏、全年龄版分别指什么？用一张对照表讲清各概念描述的维度，并给出中文语境下的推荐用法。",
        "keywords": "galgame和视觉小说区别,视觉小说是什么,AVG和ADV区别,乙女游戏,galgame定义,Visual Novel",
        "h1": "Galgame / 视觉小说 / AVG：概念辨析",
        "lead": "这些词吵了二十年没统一，是因为它们描述的根本不是同一个维度。",
        "eyebrow": "Compare · 概念辨析",
        "schema": "Article", "priority": "0.9", "changefreq": "monthly",
        "toc": [("why", "为什么会混用"), ("matrix", "概念对照表"), ("vn", "Galgame vs 视觉小说"),
                ("adv", "AVG / ADV / 恋爱模拟"), ("audience", "乙女游戏与分级"), ("usage", "中文语境用法速查")],
        "related": ["glossary.html", "guide.html", "faq.html", "history.html"],
        "body": COMPARE_BODY,
    },
    {
        "file": "faq.html", "kind": "article",
        "title": "Galgame 常见问题 15 问：分级、中文、时长、平台与入门 | Galwiki",
        "description": "Galgame 常见问题集中解答：是不是 18 禁、需要日语吗、有官方中文吗、第一部选什么、要玩多久、手机能玩吗、全年龄版差在哪、为什么行业规模缩小、本站是否提供下载。",
        "keywords": "galgame常见问题,galgame问答,galgame有中文吗,galgame手机,galgame时长,全年龄版,galgame 18禁",
        "h1": "Galgame 常见问题",
        "lead": "15 个被问得最多的问题，给结论、给依据、也告诉你下一步去哪看。",
        "eyebrow": "FAQ · 常见问题",
        "schema": "FAQPage", "priority": "0.8", "changefreq": "monthly",
        "toc": [("list", "全部问答"), ("more", "没找到答案？")],
        "related": ["guide.html", "compare.html", "glossary.html", "about.html"],
        "body": FAQ_BODY,
        "faq": FAQ,
    },
    {
        "file": "about.html", "kind": "article",
        "title": "关于 Galwiki：站点定位、内容边界与编辑方针 | Galwiki",
        "description": "Galwiki 是面向中文读者的 Galgame 与视觉小说文化科普站。了解我们的内容边界、事实核对方针、隐私政策、技术说明与参考资料来源。",
        "keywords": "关于Galwiki,galgame资料站,内容边界,编辑方针,资料来源,隐私",
        "h1": "关于 Galwiki",
        "lead": "一个不追热点、不做榜单、不提供资源的中文资料站，以及它为什么要这样设边界。",
        "eyebrow": "About · 关于本站",
        "schema": "AboutPage", "priority": "0.5", "changefreq": "yearly",
        "toc": [("position", "站点定位"), ("boundary", "内容边界"), ("editorial", "编辑方针"),
                ("privacy", "隐私与技术"), ("sources", "主要参考资料"), ("contact", "联系与反馈")],
        "related": ["history.html", "faq.html", "compare.html", "index.html"],
        "body": ABOUT_BODY,
    },
    {
        "file": "404.html", "kind": "article",
        "title": "页面未找到 | Galwiki",
        "description": "这个页面不存在或已移动。可以从首页、新手入门指南、经典作品图鉴与术语词典重新进入 Galwiki，继续查阅 Galgame 定义、四十年发展简史与常见问题。",
        "keywords": "404,页面未找到",
        "h1": "页面未找到",
        "lead": "链接可能已移动，站内内容都在下面几个入口里。",
        "eyebrow": "404 · Not Found",
        "schema": "WebPage", "priority": "0.1", "changefreq": "yearly",
        "toc": [], "related": [], "body": NOTFOUND_BODY,
        "noindex": True,
    },
]
