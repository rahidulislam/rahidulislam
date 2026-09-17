/**
 * Rahidul Islam — Portfolio Interactive Features
 * Lightweight, zero-dependency vanilla JavaScript
 */
(() => {
  'use strict';

  // Bootstrap owns the responsive navigation collapse. Close it after a
  // destination is selected so in-page links reveal their target immediately.
  const nav = document.querySelector('#site-nav');
  if (nav && window.bootstrap) {
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
      window.bootstrap.Collapse.getInstance(nav)?.hide();
    }));
  }

  // --- Project Category Filter ---
  const filters = document.querySelector('.filters');
  if (filters) {
    filters.hidden = false;
    filters.addEventListener('click', event => {
      const button = event.target.closest('[data-filter]');
      if (!button) return;
      filters.querySelectorAll('button').forEach(item => { const active = item === button; item.classList.toggle('active', active); item.setAttribute('aria-pressed', String(active)); });
      document.querySelectorAll('[data-category]').forEach(card => { card.hidden = button.dataset.filter !== 'all' && card.dataset.category !== button.dataset.filter; });
      filters.querySelectorAll('button').forEach(item => {
        const active = item === button;
        item.classList.toggle('active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      const selected = button.dataset.filter;
      document.querySelectorAll('[data-category]').forEach(card => {
        const matches = selected === 'all' || card.dataset.category === selected;
        card.hidden = !matches;
      });
    });
  }
  document.querySelectorAll('.print-button').forEach(button => { button.hidden = false; button.addEventListener('click', () => window.print()); });

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
