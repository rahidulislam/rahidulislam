/**
 * Rahidul Islam — Portfolio Interactive Features
 * Lightweight, zero-dependency vanilla JavaScript
 */
(() => {
  'use strict';

  // --- Mobile Navigation Drawer ---
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#site-nav');
  if (toggle && nav) {
    toggle.hidden = false;
    const closeMenu = () => { toggle.setAttribute('aria-expanded', 'false'); nav.classList.remove('is-open'); };
    const closeMenu = () => {
      toggle.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
    };
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open)); nav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    });
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', event => { if (event.key === 'Escape' && nav.classList.contains('is-open')) { closeMenu(); toggle.focus(); } });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        closeMenu();
        toggle.focus();
      }
    });
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
