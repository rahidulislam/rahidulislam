(() => {
  'use strict';
  /** @param {EventTarget | null} target */
  function contactLink(target) {
    const link = target instanceof Element ? target.closest('.footer-contact-action') : null;
    return link instanceof HTMLElement ? link : null;
  }
  // Delegation also covers footer links replaced by HTMX navigation.
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    document.querySelectorAll('.footer-contact-action:hover, .footer-contact-action:focus').forEach(link => {
      link.setAttribute('data-tooltip-dismissed', '');
    });
  });
  document.addEventListener('focusin', event => {
    contactLink(event.target)?.removeAttribute('data-tooltip-dismissed');
  });
  document.addEventListener('pointerover', event => {
    const link = contactLink(event.target);
    if (link && !(event.relatedTarget instanceof Node && link.contains(event.relatedTarget))) {
      link.removeAttribute('data-tooltip-dismissed');
    }
  });
})();
