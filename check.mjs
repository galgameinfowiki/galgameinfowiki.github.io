#!/usr/bin/env node
/* ==========================================================================
   check.mjs · 本地 SEO / 结构自检（零依赖）

   用法：node check.mjs
   检查：元数据完整性、H1 唯一性、标题层级、JSON-LD 合法性、
        全部内链与锚点可达性、sitemap / robots / RSS / OG 图 / 搜索索引。
   有错误时以非零退出码结束，方便接进 CI。
   ========================================================================== */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const read = (f) => fs.readFileSync(path.join(ROOT, f), "utf8");
const exists = (f) => fs.existsSync(path.join(ROOT, f));

const htmlFiles = fs.readdirSync(ROOT)
  .filter((f) => f.endsWith(".html"))
  .sort((a, b) => (a === "index.html" ? -1 : b === "index.html" ? 1 : a.localeCompare(b)));

const errors = [];
const warns = [];
const err = (file, msg) => errors.push(`${file}：${msg}`);
const warn = (file, msg) => warns.push(`${file}：${msg}`);

const cache = Object.fromEntries(htmlFiles.map((f) => [f, read(f)]));
const idsOf = (content) => new Set([...content.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]));

function checkHead(file, c) {
  if (!/^<!DOCTYPE html>/i.test(c)) err(file, "缺少 <!DOCTYPE html>");
  if (!/<html lang="zh-CN"/.test(c)) err(file, "html 缺少 lang=\"zh-CN\"");
  if (!/name="viewport"/.test(c)) err(file, "缺少 viewport meta");

  const title = (c.match(/<title>([\s\S]*?)<\/title>/) || [])[1] || "";
  if (!title) err(file, "缺少 <title>");
  else if (title.length > 65) warn(file, `title ${title.length} 字符，建议 ≤ 60`);
  if (title && !/Galwiki/.test(title)) warn(file, "title 未包含品牌词");

  const desc = (c.match(/<meta name="description" content="([^"]*)"/) || [])[1] || "";
  if (!desc) err(file, "缺少 meta description");
  else if (desc.length < 60 || desc.length > 170) warn(file, `description ${desc.length} 字符，建议 80–155`);

  if (!/<meta name="keywords" content="[^"]+"/.test(c)) err(file, "缺少 meta keywords");
  if (!/<link rel="canonical" href="https:\/\//.test(c)) err(file, "缺少 canonical");
  for (const k of ["og:type", "og:title", "og:description", "og:url", "og:image", "og:locale", "og:site_name"]) {
    if (!c.includes(`property="${k}"`)) err(file, `缺少 ${k}`);
  }
  for (const k of ["twitter:card", "twitter:title", "twitter:description", "twitter:image"]) {
    if (!c.includes(`name="${k}"`)) err(file, `缺少 ${k}`);
  }
  if (!/<meta name="robots" content=/.test(c)) err(file, "缺少 robots meta");
  if (!/<link rel="alternate" type="application\/rss\+xml"/.test(c)) warn(file, "缺少 RSS 自动发现链接");

  const h1 = [...c.matchAll(/<h1[\s>]/g)].length;
  if (h1 !== 1) err(file, `H1 数量为 ${h1}（应为 1）`);
  const h2 = [...c.matchAll(/<h2[\s>]/g)].length;
  if (h2 === 0 && file !== "404.html") warn(file, "没有 H2，长内容建议分节");

  // id 唯一性
  const allIds = [...c.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]);
  const dup = allIds.filter((v, i) => allIds.indexOf(v) !== i);
  if (dup.length) err(file, `重复 id：${[...new Set(dup)].join(", ")}`);

  // JSON-LD
  const ld = [...c.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  if (ld.length !== 1) err(file, `JSON-LD 块数量为 ${ld.length}（应为 1）`);
  else {
    try {
      const data = JSON.parse(ld[0][1]);
      const types = (data["@graph"] || []).map((x) => x["@type"]).flat();
      for (const need of ["WebSite", "Organization"]) {
        if (!types.includes(need)) err(file, `JSON-LD 缺少 ${need}`);
      }
      if (file !== "index.html" && !types.includes("BreadcrumbList")) err(file, "JSON-LD 缺少 BreadcrumbList");
      if (file === "faq.html") {
        const faq = data["@graph"].find((x) => x["@type"] === "FAQPage");
        if (!faq || !faq.mainEntity || faq.mainEntity.length < 5) err(file, "FAQPage 的 mainEntity 不完整");
      }
    } catch (e) {
      err(file, `JSON-LD 无法解析：${e.message}`);
    }
  }

  // 图片 alt
  for (const m of c.matchAll(/<img\b[^>]*>/g)) {
    if (!/\balt=/.test(m[0])) err(file, "img 缺少 alt 属性");
  }
  // 外链安全
  for (const m of c.matchAll(/<a\b[^>]*target="_blank"[^>]*>/g)) {
    if (!/rel="[^"]*noopener/.test(m[0])) err(file, "target=_blank 缺少 rel=noopener");
  }

  return { title: title.length, desc: desc.length, h2 };
}

function checkLinks(file, c) {
  const localIds = idsOf(c);
  let count = 0, anchors = 0;
  const seen = new Set();
  for (const m of c.matchAll(/\bhref="([^"]+)"/g)) {
    const href = m[1];
    if (/^(https?:|mailto:|javascript:)/i.test(href)) continue;
    if (href === "" || href === "#") { err(file, `空链接 href="${href}"`); continue; }
    const [filePart, hash] = href.split("#");
    const target = filePart === "" ? file : filePart;
    count++;
    const key = target + (hash ? "#" + hash : "");
    if (seen.has(key)) continue;
    seen.add(key);
    if (!/^[\w./-]+$/.test(target)) { err(file, `可疑链接 ${href}`); continue; }
    if (!exists(target)) { err(file, `内链指向不存在的文件：${href}`); continue; }
    if (hash) {
      anchors++;
      if (target.endsWith(".html")) {
        const tc = cache[target] || fs.readFileSync(path.join(ROOT, target), "utf8");
        if (!idsOf(tc).has(hash)) err(file, `锚点不存在：${href}`);
      }
    }
  }
  if (/href="http:\/\//.test(c)) warn(file, "存在 http:// 明文链接");
  return { count, anchors };
}

console.log("\nGalwiki · SEO 与结构自检报告");
console.log("═".repeat(104));
console.log("页面".padEnd(18) + "T".padEnd(6) + "D".padEnd(6) + "H2".padEnd(6) + "内链".padEnd(8) + "锚点".padEnd(8) + "结果");
console.log("─".repeat(104));

const rows = [];
for (const [file, c] of Object.entries(cache)) {
  const before = errors.length;
  const meta = checkHead(file, c);
  const links = checkLinks(file, c);
  const ok = errors.length === before;
  rows.push({ file, ...meta, ...links, ok });
  console.log(
    file.padEnd(18) +
    String(meta.title).padEnd(6) +
    String(meta.desc).padEnd(6) +
    String(meta.h2).padEnd(6) +
    String(links.count).padEnd(8) +
    String(links.anchors).padEnd(8) +
    (ok ? "✓ 通过" : "✗ 有问题")
  );
}

console.log("─".repeat(104));
console.log(`页面 ${htmlFiles.length} 个 · 内链合计 ${rows.reduce((s, r) => s + r.count, 0)} 条 · 锚点 ${rows.reduce((s, r) => s + r.anchors, 0)} 处`);

/* ---------- 全局产物 ---------- */
console.log("\n全局产物检查");
console.log("─".repeat(104));

function globalCheck(label, fn) {
  const before = errors.length;
  try {
    const note = fn();
    console.log(`  ${errors.length === before ? "✓" : "✗"} ${label}${note ? " — " + note : ""}`);
  } catch (e) {
    err("全局", `${label}：${e.message}`);
    console.log(`  ✗ ${label} — ${e.message}`);
  }
}

globalCheck("sitemap.xml", () => {
  const x = read("sitemap.xml");
  const locs = [...x.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
  if (locs.length !== htmlFiles.length - 1) {
    err("sitemap.xml", `收录 ${locs.length} 个 URL，页面（不含 404）为 ${htmlFiles.length - 1} 个`);
  }
  if (x.includes("404.html")) err("sitemap.xml", "不应收录 404.html");
  for (const l of locs) {
    if (!l.includes("/sitemap")) {
      const f = l.split("/").pop() || "index.html";
      if (f !== "index.html" && !exists(f)) err("sitemap.xml", `URL 无对应文件：${l}`);
    }
  }
  return `${locs.length} 个 URL`;
});

globalCheck("robots.txt", () => {
  const r = read("robots.txt");
  if (!/User-agent:\s*\*/.test(r)) err("robots.txt", "缺少 User-agent: *");
  if (!/Sitemap:\s*https?:\/\//.test(r)) err("robots.txt", "缺少 Sitemap 指令");
  return "含 Sitemap 指令";
});

globalCheck("rss.xml", () => {
  const r = read("rss.xml");
  if (!/<rss version="2.0"/.test(r)) err("rss.xml", "缺少 rss 2.0 声明");
  const items = [...r.matchAll(/<item>/g)].length;
  if (items < 5) err("rss.xml", "item 数量过少");
  return `${items} 个条目`;
});

globalCheck("OG 封面图", () => {
  if (!exists("assets/img/og-cover.png")) { err("og-cover.png", "文件不存在"); return; }
  const buf = fs.readFileSync(path.join(ROOT, "assets/img/og-cover.png"));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  if (w !== 1200 || h !== 630) err("og-cover.png", `尺寸 ${w}×${h}，建议 1200×630`);
  return `${w}×${h}, ${(buf.length / 1024).toFixed(0)} KB`;
});

globalCheck("搜索索引", () => {
  const js = read("search-index.js");
  const start = js.indexOf("window.GALWIKI_INDEX = ");
  if (start < 0) { err("search-index.js", "缺少全局变量"); return; }
  const raw = js.slice(start + "window.GALWIKI_INDEX = ".length).trim().replace(/;\s*$/, "");
  const idx = JSON.parse(raw);
  if (idx.length < 50) err("search-index.js", "索引条目过少");
  for (const item of idx) {
    const f = item.url.split("#")[0];
    if (!exists(f)) err("search-index.js", `索引指向不存在的文件 ${item.url}`);
  }
  const json = JSON.parse(read("search-index.json"));
  if (json.length !== idx.length) err("search-index.json", "与 js 索引条目数不一致");
  return `${idx.length} 条，js/json 一致`;
});

globalCheck("静态资源", () => {
  for (const f of ["assets/css/style.css", "assets/js/main.js", "assets/img/favicon.svg", "search-index.js"]) {
    if (!exists(f)) err("资源", `缺少 ${f}`);
  }
  return "CSS / JS / favicon / 索引齐备";
});

globalCheck("零外部依赖", () => {
  // 只检查真正会发起请求的标签（link/script/img），<a> 的参考资料外链不算资源依赖
  const assetTag = /<(?:link|script|img)\b[^>]*(?:src|href)="(https?:\/\/[^"]+)"/g;
  for (const [file, c] of Object.entries(cache)) {
    const ext = [...c.matchAll(assetTag)]
      .map((m) => m[1])
      .filter((u) => !u.includes("galgameinfowiki.github.io") && !u.includes("galwiki.example.com") && !u.includes("schema.org"));
    if (ext.length) warn(file, `存在外部资源引用：${ext.slice(0, 2).join(", ")}`);
  }
  return "无 CDN / 外部字体 / 第三方脚本";
});

/* ---------- 汇总 ---------- */
console.log("\n" + "═".repeat(104));
if (warns.length) {
  console.log(`提示 ${warns.length} 条：`);
  warns.forEach((w) => console.log("  · " + w));
}
if (errors.length) {
  console.log(`\n✗ 发现 ${errors.length} 个问题：`);
  errors.forEach((e) => console.log("  · " + e));
  process.exit(1);
}
console.log("✓ 全部检查通过：元数据、结构化数据、内链锚点、站点地图与资源均正常。\n");
