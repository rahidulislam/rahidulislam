import js from "@eslint/js";

export default [
  { ignores: ["static/vendor/**", "staticfiles/**"] },
  {
    files: ["static/**/*.js"],
    ...js.configs.recommended,
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "script",
      globals: Object.fromEntries([
        "Node", "localStorage", "htmx", "DOMParser", "window", "document", "HTMLElement", "HTMLFormElement", "HTMLDetailsElement",
        "HTMLButtonElement", "Element", "HTMLTextAreaElement", "HTMLInputElement",
        "AbortController", "DOMException", "URLSearchParams", "fetch", "Event"
      ].map(name => [name, "readonly"]))
    },
    rules: { ...js.configs.recommended.rules, eqeqeq: "error", "no-var": "error", "prefer-const": "error" }
  }
];
