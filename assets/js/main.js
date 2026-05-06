document.querySelector('.menu-toggle')?.addEventListener('click', () => {
  document.querySelector('.sidebar').classList.toggle('active');
});

// Close sidebar on link click (mobile)
document.querySelectorAll('.sidebar a').forEach(a => {
  a.addEventListener('click', () => {
    if (window.innerWidth < 768) document.querySelector('.sidebar').classList.remove('active');
  });
});

// Lazy load images
document.querySelectorAll('img[loading="lazy"]').forEach(img => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.src = e.target.dataset.src; observer.unobserve(e.target); }
    });
  });
  observer.observe(img);
});
