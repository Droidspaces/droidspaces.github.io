// Docs only: search and the device filter. Both controls ship hidden, so a page without
// JavaScript is complete and simply has no search box.
(() => {
  const dialog = document.querySelector(".search-dialog");
  const input = dialog?.querySelector(".search-input");
  const list = dialog?.querySelector(".search-results");
  const openers = document.querySelectorAll(".search-open");
  let index; // fetched on first open, from our own origin

  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text; // textContent, never innerHTML: the index is page text
    return n;
  };

  function snippet(text, q) {
    const at = text.toLowerCase().indexOf(q);
    if (at < 0) return "";
    const start = Math.max(0, at - 60);
    return (start ? "..." : "") + text.slice(start, at + q.length + 80) + "...";
  }

  function search(q) {
    list.replaceChildren();
    if (!q || !index) return;
    const hits = [];
    for (const page of index) {
      const title = page.title.toLowerCase().includes(q);
      const heading = page.headings.find(([, t]) => t.toLowerCase().includes(q));
      const inText = page.text.toLowerCase().includes(q);
      if (!title && !heading && !inText) continue;
      hits.push({
        score: (title ? 3 : 0) + (heading ? 2 : 0) + (inText ? 1 : 0),
        href: heading ? `${page.url}#${heading[0]}` : page.url,
        title: page.title,
        sub: heading ? heading[1] : page.section,
        text: snippet(page.text, q),
      });
    }
    hits.sort((a, b) => b.score - a.score);
    for (const h of hits.slice(0, 20)) {
      const a = el("a", "search-hit");
      a.href = `/docs/${h.href}`;
      a.append(el("span", "search-hit-title", h.title), el("span", "search-hit-sub", h.sub));
      if (h.text) a.append(el("span", "search-hit-text", h.text));
      const li = el("li");
      li.append(a);
      list.append(li);
    }
    if (!hits.length) list.append(el("li", "search-empty", "Nothing matches that."));
  }

  async function open() {
    if (!dialog) return;
    document.getElementById("sidebar")?.hidePopover?.();
    dialog.showModal();
    input.select();
    if (!index) {
      index = await fetch("/docs/search.json").then((r) => r.json()).catch(() => []);
      search(input.value.trim().toLowerCase());
    }
  }

  if (dialog) {
    openers.forEach((b) => { b.hidden = false; b.addEventListener("click", open); });
    input.addEventListener("input", () => search(input.value.trim().toLowerCase()));
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); list.querySelector("a")?.click(); }
    });
    dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); }); // backdrop
    document.addEventListener("keydown", (e) => {
      const typing = /INPUT|TEXTAREA/.test(document.activeElement?.tagName);
      if ((e.key === "k" && (e.ctrlKey || e.metaKey)) || (e.key === "/" && !typing)) {
        e.preventDefault();
        open();
      }
    });
  }

  // community devices: hide table rows that do not contain the query
  const filter = document.querySelector(".device-filter");
  if (filter) {
    filter.hidden = false;
    const tables = [...document.querySelectorAll(".docs-content .table-wrap")];
    const empties = tables.map((t) => {
      const p = el("p", "filter-empty", "No devices match.");
      p.hidden = true;
      t.after(p);
      return p;
    });
    filter.querySelector("input").addEventListener("input", (e) => {
      const q = e.target.value.trim().toLowerCase();
      tables.forEach((t, i) => {
        let shown = 0;
        for (const row of t.querySelectorAll("tbody tr")) {
          row.hidden = !!q && !row.textContent.toLowerCase().includes(q);
          if (!row.hidden) shown++;
        }
        t.hidden = shown === 0;
        empties[i].hidden = shown !== 0;
      });
    });
  }
})();
