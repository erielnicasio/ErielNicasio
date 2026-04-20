/* ============================================================
   AYUDA A UN TERCERO — Main JavaScript
   Shared functionality across all pages
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  DB.init();
  initNavbar();
  initMobileNav();
  initAccessibility();
  lucide.createIcons();
});

/* ── Navbar scroll behavior ─────────────────────────────── */
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;

  const hasHero = !!document.querySelector('.hero');
  const onScroll = () => {
    if (window.scrollY > 60 || !hasHero) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ── Mobile navigation toggle ───────────────────────────── */
function initMobileNav() {
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (!toggle || !links) return;

  toggle.addEventListener('click', () => {
    links.classList.toggle('open');
    toggle.classList.toggle('active');
  });

  // Close menu when clicking a link
  links.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      links.classList.remove('open');
      toggle.classList.remove('active');
    });
  });
}

/* ── Accessibility widget ───────────────────────────────── */
function initAccessibility() {
  const trigger = document.querySelector('.access-trigger');
  const menu = document.querySelector('.access-menu');
  if (!trigger || !menu) return;

  trigger.addEventListener('click', () => {
    menu.classList.toggle('active');
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.access-widget')) {
      menu.classList.remove('active');
    }
  });
}

/* ── Counter animation ──────────────────────────────────── */
function animateCounters() {
  const counters = document.querySelectorAll('[data-count]');
  counters.forEach(counter => {
    const target = parseInt(counter.dataset.count, 10);
    const duration = 1500;
    const step = target / (duration / 16);
    let current = 0;

    const update = () => {
      current += step;
      if (current >= target) {
        counter.textContent = target.toLocaleString('es-DO');
        return;
      }
      counter.textContent = Math.floor(current).toLocaleString('es-DO');
      requestAnimationFrame(update);
    };
    update();
  });
}

/* ── Intersection Observer for animations ───────────────── */
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.observe').forEach(el => observer.observe(el));
}

/* ── Tab switching ──────────────────────────────────────── */
function initTabs(containerSelector) {
  const container = document.querySelector(containerSelector);
  if (!container) return;

  const btns = container.querySelectorAll('.tab-btn');
  const contents = container.querySelectorAll('.tab-content');

  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      btns.forEach(b => b.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const targetEl = container.querySelector(`#${target}`);
      if (targetEl) targetEl.classList.add('active');
    });
  });
}

/* ── Modal helpers ──────────────────────────────────────── */
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('active');
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove('active');
}

/* ── Format currency ────────────────────────────────────── */
function formatCurrency(amount) {
  return '$' + Number(amount).toLocaleString('es-DO', { minimumFractionDigits: 2 });
}

/* ── Toast notification ─────────────────────────────────── */
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  toast.style.cssText = `
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    padding: 14px 24px; border-radius: 8px; font-weight: 600; font-size: .9rem;
    color: white; box-shadow: 0 8px 24px rgba(0,0,0,.15);
    animation: fadeInUp .4s ease;
    background: ${type === 'success' ? '#2E9E5A' : type === 'error' ? '#DC2626' : '#1B5FAA'};
  `;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity .3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
