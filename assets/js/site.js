// What this site needs JavaScript for: the theme toggle, the copy button and the arrival trigger.
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

// Arrival: a timed entrance that starts when a phone or shape reaches the screen. A scroll-driven one
// ran at the scroll's speed, so a fast flick popped it in and every scroll frame repainted it. Only
// objects below the screen are ever hidden (.pending), and only by this script.
(() => {
  if (!("IntersectionObserver" in window)) return;
  const io = new IntersectionObserver((entries) => {
    for (const { target: el, isIntersecting } of entries) {
      if (!isIntersecting) { el.classList.add("pending"); continue; }
      // already on screen at load: it was painted, so leave it be instead of blinking it out and back
      if (el.classList.contains("pending")) el.classList.replace("pending", "arrived");
      io.unobserve(el);
    }
  }, { rootMargin: "0px 0px -10% 0px" });
  document.querySelectorAll(".arrive, .phone-group").forEach((el) => io.observe(el));
})();
