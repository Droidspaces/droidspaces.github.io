// The three things this site needs JavaScript for: the theme toggle, the copy button, and nothing else.
// The drawer is a native popover. The toggle's icon is picked in CSS, so this only flips the attribute.
(() => {
  const root = document.documentElement;
  const light = matchMedia("(prefers-color-scheme: light)");
  document.getElementById("theme-toggle")?.addEventListener("click", () => {
    const current = root.dataset.theme || (light.matches ? "light" : "dark");
    root.dataset.theme = current === "dark" ? "light" : "dark";
    localStorage.setItem("theme", root.dataset.theme); // the one key the site stores
  });
})();

function copyCode(btn) {
  const code = btn.parentElement.querySelector("pre").textContent;
  const icon = btn.querySelector(".icon");
  navigator.clipboard.writeText(code).then(() => {
    icon.textContent = "check";
    setTimeout(() => { icon.textContent = "content_copy"; }, 1500);
  });
}
