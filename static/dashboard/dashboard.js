"use strict";

(() => {
  /** @type {AbortController | null} */
  let previewController = null;
  let submitting = false;

  function dirtyForm() {
    return document.querySelector('form[data-editor][data-dirty="true"]');
  }

  function configureNavigation() {
    const navigation = document.querySelector("details.navigation");
    if (navigation instanceof HTMLDetailsElement) {
      navigation.open = !window.matchMedia("(max-width: 760px)").matches;
    }
    submitting = false;
  }

  document.addEventListener("input", (event) => {
    const target = event.target;
    if (target instanceof HTMLElement) {
      const form = target.closest("form[data-editor]");
      if (form instanceof HTMLFormElement) form.dataset.dirty = "true";
    }
  });

  document.addEventListener("change", (event) => {
    const target = event.target;
    if (target instanceof HTMLElement) {
      const form = target.closest("form[data-editor]");
      if (form instanceof HTMLFormElement) form.dataset.dirty = "true";
    }
  });

  window.addEventListener("beforeunload", (event) => {
    if (dirtyForm() && !submitting) {
      event.preventDefault();
      event.returnValue = true;
    }
  });

  document.addEventListener("submit", (event) => {
    if (!(event.target instanceof HTMLFormElement)) return;
    submitting = true;
    // Native validation has already passed when submit fires.
    event.target.querySelectorAll('button[type="submit"]').forEach((button) => {
      // Preserve named action buttons: disabling them would omit their values.
      if (button instanceof HTMLButtonElement && !button.name) button.disabled = true;
    });
  });

  document.addEventListener("htmx:beforeRequest", () => {
    const error = document.getElementById("request-error");
    if (error) error.hidden = true;
  });
  for (const eventName of ["htmx:responseError", "htmx:sendError", "htmx:timeout"]) {
    document.addEventListener(eventName, () => {
      const error = document.getElementById("request-error");
      if (error) error.hidden = false;
    });
  }
  document.addEventListener("htmx:confirm", (event) => {
    if (dirtyForm() && !window.confirm("Leave this page? Your unsaved changes will be lost.")) {
      event.preventDefault();
    }
  });
  document.addEventListener("htmx:beforeSwap", () => {
    if (previewController) previewController.abort();
  });
  document.addEventListener("htmx:afterSwap", () => {
    configureNavigation();
    const main = document.getElementById("main");
    if (main) main.focus({ preventScroll: true });
  });
  window.addEventListener("pageshow", () => {
    submitting = false;
    document.querySelectorAll('button[type="submit"]').forEach((button) => {
      if (button instanceof HTMLButtonElement) button.disabled = false;
    });
  });

  document.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    const button = target.closest("button[data-preview-field]");
    if (!(button instanceof HTMLButtonElement)) return;
    const form = button.closest("form");
    const field = form && form.elements.namedItem(button.dataset.previewField || "");
    const token = form && form.elements.namedItem("csrfmiddlewaretoken");
    const output = document.getElementById("markdown-preview");
    const status = document.getElementById("preview-status");
    const url = button.dataset.previewUrl;
    if (!(field instanceof HTMLTextAreaElement) || !(token instanceof HTMLInputElement) || !output || !status || !url) return;
    if (previewController) previewController.abort();
    const controller = new AbortController();
    previewController = controller;
    status.textContent = "Rendering preview…";
    output.setAttribute("aria-busy", "true");
    try {
      const response = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRFToken": token.value },
        body: new URLSearchParams({ body: field.value }),
        signal: controller.signal,
      });
      if (!response.ok || response.redirected) throw new Error("Preview unavailable");
      const html = await response.text();
      if (!controller.signal.aborted && output.isConnected) {
        // Only the authenticated server's HTML-escaping Markdown renderer supplies this HTML.
        output.innerHTML = html;
        status.textContent = `Preview of ${button.dataset.previewField === "body_bn" ? "Bengali" : "English"} text. Unsaved changes are included.`;
      }
    } catch (error) {
      if (!(error instanceof DOMException && error.name === "AbortError") && status.isConnected) {
        status.textContent = "Preview failed. Your text is unchanged; try again.";
      }
    } finally {
      if (previewController === controller) {
        output.removeAttribute("aria-busy");
        previewController = null;
      }
    }
  });
  configureNavigation();
})();
