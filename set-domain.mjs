#!/usr/bin/env node
/* ==========================================================================
   set-domain.mjs · 部署前把占位域名一次性换成真实域名

   用法：node set-domain.mjs https://www.example.com
   作用：替换 content_data.py / content_pages.py / build.py 中的占位域名与邮箱，
        然后自动重新运行 build.py 生成全站页面、sitemap、robots 与结构化数据。
   ========================================================================== */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const PLACEHOLDER_HOST = "galwiki.example.com";
const PLACEHOLDER_URL = `https://${PLACEHOLDER_HOST}`;
const PLACEHOLDER_MAIL = `hello@${PLACEHOLDER_HOST}`;

let target = process.argv[2];
if (!target) {
  console.error("用法：node set-domain.mjs https://你的域名");
  console.error("示例：node set-domain.mjs https://www.mygalsite.com");
  process.exit(1);
}
target = target.trim().replace(/\/+$/, "");
if (!/^https?:\/\//i.test(target)) target = "https://" + target;

let host;
try {
  host = new URL(target).hostname;
} catch {
  console.error("域名格式不正确：" + target);
  process.exit(1);
}
if (host === PLACEHOLDER_HOST) {
  console.error("请填写真实域名，不要继续使用占位域名。");
  process.exit(1);
}

const files = ["content_data.py", "content_pages.py", "build.py"];
let total = 0;

for (const name of files) {
  const file = path.join(ROOT, name);
  const before = fs.readFileSync(file, "utf8");
  let after = before
    .split(PLACEHOLDER_URL).join(target)
    .split(PLACEHOLDER_MAIL).join(`hello@${host}`)
    .replace("（示例地址，部署时请替换为真实邮箱）", "");
  const count = before === after ? 0 : (before.split(PLACEHOLDER_URL).length - 1)
    + (before.split(PLACEHOLDER_MAIL).length - 1);
  if (before !== after) {
    fs.writeFileSync(file, after, "utf8");
    console.log(`  ✓ ${name} 替换 ${count} 处`);
    total += count;
  }
}

if (total === 0) {
  console.log("  ! 没有找到占位域名，可能已经替换过了。仍会重新构建一次。");
}

console.log("\n重新构建站点…\n");
try {
  const out = execFileSync("python3", ["build.py"], { cwd: ROOT, encoding: "utf8" });
  console.log(out);
} catch (e) {
  console.error("构建失败：", e.message);
  process.exit(1);
}

// 复核构建产物里的域名
const sitemap = fs.readFileSync(path.join(ROOT, "sitemap.xml"), "utf8");
const canonical = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const ok = sitemap.includes(target) && canonical.includes(`rel="canonical" href="${target}/"`);
console.log(ok ? `✓ 校验通过：sitemap 与 canonical 均已指向 ${target}` : "! 校验未通过，请检查生成结果");
console.log(`\n接下来：把整个 galwiki/ 目录上传到静态托管，确认 ${target}/sitemap.xml 可访问后提交搜索引擎。`);
if (!ok) process.exit(1);
