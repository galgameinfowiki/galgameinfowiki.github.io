/* ==========================================================================
   Galwiki · 交互脚本（原生 JS，零依赖）
   主题切换 / 移动导航 / 阅读进度 / 目录高亮 / 站内搜索 / 返回顶部
   ========================================================================== */
(function () {
  "use strict";

  var doc = document;
  var html = doc.documentElement;

  /* ---------- 1. 亮暗主题 ---------- */
  var THEME_KEY = "galwiki-theme";
  var themeBtn = doc.getElementById("theme-toggle");

  function applyTheme(theme) {
    html.setAttribute("data-theme", theme);
    if (themeBtn) {
      themeBtn.setAttribute("aria-label", theme === "dark" ? "切换到浅色模式" : "切换到深色模式");
      themeBtn.setAttribute("title", theme === "dark" ? "切换到浅色模式" : "切换到深色模式");
    }
  }

  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* 隐私模式下忽略 */ }
    });
  }

  doc.addEventListener("keydown", function (e) {
    if (e.key.toLowerCase() === "d" && !e.metaKey && !e.ctrlKey && !e.altKey) {
      var tag = doc.activeElement && doc.activeElement.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") { return; }
      if (themeBtn) { themeBtn.click(); }
    }
  });

  /* ---------- 2. 移动端导航 ---------- */
  var menuBtn = doc.getElementById("menu-toggle");
  var nav = doc.getElementById("primary-nav");
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", String(open));
      menuBtn.setAttribute("aria-label", open ? "关闭导航菜单" : "打开导航菜单");
    });
    doc.addEventListener("click", function (e) {
      if (!nav.contains(e.target) && !menuBtn.contains(e.target)) {
        nav.classList.remove("open");
        menuBtn.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------- 3. 阅读进度 + 返回顶部 ---------- */
  var progress = doc.getElementById("progress");
  var backTop = doc.getElementById("back-top");
  var ticking = false;

  function onScroll() {
    var docEl = doc.documentElement;
    var scrollable = docEl.scrollHeight - window.innerHeight;
    var ratio = scrollable > 0 ? window.scrollY / scrollable : 0;
    if (progress) { progress.style.width = Math.min(100, Math.max(0, ratio * 100)) + "%"; }
    if (backTop) { backTop.classList.toggle("show", window.scrollY > 600); }
    ticking = false;
  }

  window.addEventListener("scroll", function () {
    if (!ticking) { window.requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  onScroll();

  if (backTop) {
    backTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    });
  }

  /* ---------- 4. 目录高亮（IntersectionObserver） ---------- */
  var tocLinks = Array.prototype.slice.call(doc.querySelectorAll(".toc a[href^='#']"));
  if (tocLinks.length > 0 && "IntersectionObserver" in window) {
    var byId = {};
    tocLinks.forEach(function (link) {
      var id = decodeURIComponent(link.getAttribute("href").slice(1));
      var target = doc.getElementById(id);
      if (target) { byId[id] = link; }
    });

    var visible = {};
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { visible[entry.target.id] = entry.isIntersecting; });
      var firstVisible = null;
      var ids = Object.keys(byId);
      for (var i = 0; i < ids.length; i++) {
        if (visible[ids[i]]) { firstVisible = ids[i]; break; }
      }
      if (!firstVisible) {
        // 视口在两个标题之间时，取最后一个已滚过的标题
        ids.forEach(function (id) {
          var rect = doc.getElementById(id).getBoundingClientRect();
          if (rect.top < 160) { firstVisible = id; }
        });
      }
      if (firstVisible) {
        tocLinks.forEach(function (l) { l.classList.remove("active"); });
        byId[firstVisible].classList.add("active");
      }
    }, { rootMargin: "-90px 0px -70% 0px", threshold: [0, 1] });

    Object.keys(byId).forEach(function (id) { observer.observe(doc.getElementById(id)); });
  }

  /* ---------- 5. 站内搜索（索引由 build.py 生成为 search-index.js） ---------- */
  var backdrop = doc.getElementById("search-backdrop");
  var input = doc.getElementById("search-input");
  var results = doc.getElementById("search-results");
  var openBtns = doc.querySelectorAll("[data-search-open]");
  var index = Array.isArray(window.GALWIKI_INDEX) ? window.GALWIKI_INDEX : [];
  var activePos = -1;

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function score(item, q) {
    var title = item.title.toLowerCase();
    var desc = (item.description || "").toLowerCase();
    var kw = (item.keywords || "").toLowerCase();
    var text = (item.text || "").toLowerCase();
    if (title.indexOf(q) !== -1) { return 5; }
    if (kw.indexOf(q) !== -1) { return 4; }
    if (desc.indexOf(q) !== -1) { return 3; }
    if (text.indexOf(q) !== -1) { return 1; }
    return 0;
  }

  function render(q) {
    if (!results) { return; }
    activePos = -1;
    var query = q.trim().toLowerCase();
    var hits;
    if (query === "") {
      hits = index.slice(0, 8);
    } else {
      hits = index
        .map(function (item) { return { item: item, s: score(item, query) }; })
        .filter(function (x) { return x.s > 0; })
        .sort(function (a, b) { return b.s - a.s; })
        .slice(0, 10)
        .map(function (x) { return x.item; });
    }

    if (hits.length === 0) {
      results.innerHTML = '<div class="search-empty">没有找到相关内容，试试「入门」「术语」「发展史」或某部作品名。</div>';
      return;
    }
    results.innerHTML = hits.map(function (item, i) {
      return '<a class="search-result" data-pos="' + i + '" href="' + escapeHtml(item.url) + '">' +
               "<strong>" + escapeHtml(item.title) + "</strong>" +
               "<span>" + escapeHtml(item.description || "") + "</span>" +
             "</a>";
    }).join("");
  }

  function openSearch() {
    if (!backdrop) { return; }
    backdrop.classList.add("open");
    backdrop.setAttribute("aria-hidden", "false");
    doc.body.style.overflow = "hidden";
    if (input) { input.value = ""; render(""); input.focus(); }
  }

  function closeSearch() {
    if (!backdrop) { return; }
    backdrop.classList.remove("open");
    backdrop.setAttribute("aria-hidden", "true");
    doc.body.style.overflow = "";
  }

  Array.prototype.forEach.call(openBtns, function (btn) {
    btn.addEventListener("click", openSearch);
  });

  doc.addEventListener("keydown", function (e) {
    var isOpen = backdrop && backdrop.classList.contains("open");
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      isOpen ? closeSearch() : openSearch();
      return;
    }
    if (!isOpen) { return; }
    if (e.key === "Escape") { closeSearch(); return; }
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      var items = results ? results.querySelectorAll(".search-result") : [];
      if (items.length === 0) { return; }
      activePos = e.key === "ArrowDown"
        ? (activePos + 1) % items.length
        : (activePos - 1 + items.length) % items.length;
      items.forEach(function (el, i) { el.classList.toggle("active", i === activePos); });
      items[activePos].scrollIntoView({ block: "nearest" });
    }
    if (e.key === "Enter" && activePos >= 0 && results) {
      var target = results.querySelector('.search-result[data-pos="' + activePos + '"]');
      if (target) { window.location.href = target.getAttribute("href"); }
    }
  });

  if (backdrop) {
    backdrop.addEventListener("click", function (e) { if (e.target === backdrop) { closeSearch(); } });
  }
  if (input) { input.addEventListener("input", function () { render(input.value); }); }

  /* ---------- 6. 兜底：为正文裸表格自动加滚动容器 ---------- */
  var tables = doc.querySelectorAll(".prose table");
  Array.prototype.forEach.call(tables, function (table) {
    if (table.parentElement && table.parentElement.classList.contains("table-wrap")) { return; }
    var wrap = doc.createElement("div");
    wrap.className = "table-wrap";
    table.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);
  });

  /* ---------- 7. 外部链接安全属性 ---------- */
  var externals = doc.querySelectorAll('a[href^="http"]');
  Array.prototype.forEach.call(externals, function (a) {
    if (a.hostname !== window.location.hostname) {
      a.setAttribute("rel", "noopener noreferrer");
      a.setAttribute("target", "_blank");
    }
  });
})();
