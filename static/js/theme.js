(() => {
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const key = 'portfolio-theme';
  let choice = null;
  try {
    const stored = localStorage.getItem(key);
    if (stored === 'light' || stored === 'dark') choice = stored;
  } catch (_) { /* The switch still works when storage is unavailable. */ }
  function apply() {
    const dark = choice ? choice === 'dark' : system.matches;
    root.dataset.theme = dark ? 'dark' : 'light';
    const button = document.querySelector('.theme-toggle');
    if (button) {
      button.hidden = false;
      button.setAttribute('aria-pressed', String(dark));
      button.setAttribute('aria-label', dark ? 'Enable light mode' : 'Enable dark mode');
      button.title = dark ? 'Enable light mode' : 'Enable dark mode';
    }
    document.querySelectorAll('meta[name="theme-color"]').forEach(meta => {
      meta.content = dark ? '#101a23' : '#fafbfc';
    });
  }
  apply();
  system.addEventListener('change', () => { if (!choice) apply(); });
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) {
      choice = event.newValue === 'light' || event.newValue === 'dark' ? event.newValue : null;
      apply();
    }
  });
  document.addEventListener('DOMContentLoaded', () => {
    apply();
    document.querySelector('.theme-toggle')?.addEventListener('click', () => {
      choice = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(key, choice); } catch (_) { /* Session-only preference. */ }
      apply();
    });
  });
})();
