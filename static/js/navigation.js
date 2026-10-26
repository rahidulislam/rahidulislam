/* HTMX 2.0.11 is vendored under static/vendor/htmx (BSD-0-Clause). */
(() => {
  'use strict';
  // Never persist pages containing contact details or CSRF tokens to localStorage.
  document.getElementById('navigation-status').hidden = false;
  htmx.config.historyCacheSize = 0;
  htmx.config.refreshOnHistoryMiss = true;
  htmx.config.allowEval = false;
  htmx.config.allowScriptTags = false;

  document.addEventListener('htmx:beforeRequest', event => {
    const element = event.detail.elt;
    if (element.matches('a[download], a[data-lightbox]')) {
      event.preventDefault();
    }
  });

  document.addEventListener('htmx:beforeSwap', event => {
    if (!event.detail.isError && event.detail.target.id === 'page-shell') {
      const page = new DOMParser().parseFromString(event.detail.serverResponse, 'text/html');
      // Some endpoints return files or redirects outside the public page shell.
      if (!page.getElementById('page-shell')) {
        event.detail.shouldSwap = false;
        const status = document.getElementById('navigation-status');
        status.classList.remove('htmx-indicator');
        status.textContent = 'Unable to load this page. Please open it again.';
        return;
      }
      const selector = 'meta[name="description"], meta[property^="og:"], meta[name^="twitter:"], meta[property^="article:"], link[rel="canonical"], script[type="application/ld+json"]';
      document.head.querySelectorAll(selector).forEach(node => node.remove());
      page.head.querySelectorAll(selector).forEach(node => document.head.append(node.cloneNode(true)));
      document.documentElement.lang = page.documentElement.lang;
    }
  });

  document.addEventListener('htmx:afterSettle', event => {
    if (event.detail.target.id !== 'page-shell') return;
    let fragment = window.location.hash.slice(1);
    try { fragment = decodeURIComponent(fragment); } catch (_) { /* Keep malformed fragments literal. */ }
    const target = (fragment && document.getElementById(fragment)) || document.getElementById('main');
    if (target) {
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      if (fragment) target.scrollIntoView();
    }
  });

  for (const name of ['htmx:responseError', 'htmx:sendError', 'htmx:timeout']) {
    document.addEventListener(name, () => {
      const status = document.getElementById('navigation-status');
      status.classList.remove('htmx-indicator');
      status.textContent = 'The request failed. Please check your connection and try again.';
    });
  }
  document.addEventListener('htmx:beforeRequest', () => {
    const status = document.getElementById('navigation-status');
    status.classList.add('htmx-indicator');
    status.textContent = 'Loading…';
  });
})();
