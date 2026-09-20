/**
 * Rahidul Islam — Portfolio Interactive Features
 * Lightweight, zero-dependency vanilla JavaScript
 */
(() => {
  'use strict';

  // --- Mobile Navigation ---
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#site-nav');
  if (toggle && nav) {
    const mobile = window.matchMedia('(max-width: 768px)');
    const setOpen = open => {
      const shouldOpen = mobile.matches && open;
      nav.classList.toggle('is-open', shouldOpen);
      nav.toggleAttribute('inert', mobile.matches && !shouldOpen);
      toggle.setAttribute('aria-expanded', String(shouldOpen));
    };
    const closeMenu = () => setOpen(false);

    toggle.addEventListener('click', () => {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
      if (mobile.matches) closeMenu();
    }));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        closeMenu();
        toggle.focus();
      }
    });
    mobile.addEventListener('change', closeMenu);
    closeMenu();
  }

  // --- Project Category Filter ---
  const filters = document.querySelector('.filters');
  if (filters) {
    filters.hidden = false;
    filters.addEventListener('click', event => {
      const button = event.target.closest('[data-filter]');
      if (!button) return;
      filters.querySelectorAll('button').forEach(item => {
        const active = item === button;
        item.classList.toggle('active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      const selected = button.dataset.filter;
      let visibleCount = 0;
      document.querySelectorAll('[data-category]').forEach(card => {
        const matches = selected === 'all' || card.dataset.category === selected;
        card.hidden = !matches;
        if (matches) visibleCount += 1;
      });
      const status = document.querySelector('[data-filter-status]');
      if (status) status.textContent = `${visibleCount} project${visibleCount === 1 ? '' : 's'} shown`;
    });
  }

  // --- Print Support ---
  document.querySelectorAll('.print-button').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => window.print());
  });

  // --- Back to Top Smooth Scroll ---
  const backToTop = document.querySelector('.back-to-top');
  if (backToTop) {
    backToTop.addEventListener('click', event => {
      event.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
})();
