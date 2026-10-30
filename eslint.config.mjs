import js from "@eslint/js";

export default [
  {
    files: ["static/dashboard/dashboard.js", "static/js/navigation.js", "static/js/theme.js"],
    ...js.configs.recommended,
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "script",
      globals: Object.fromEntries([
        "localStorage", "htmx", "DOMParser", "window", "document", "HTMLElement", "HTMLFormElement", "HTMLDetailsElement",
        "HTMLButtonElement", "Element", "HTMLTextAreaElement", "HTMLInputElement",
        "AbortController", "DOMException", "URLSearchParams", "fetch"
      ].map(name => [name, "readonly"]))
    },
    rules: { ...js.configs.recommended.rules, eqeqeq: "error", "no-var": "error", "prefer-const": "error" }
  }
];
