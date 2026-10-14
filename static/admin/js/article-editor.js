(() => {
  'use strict';
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.article-markdown-editor').forEach(editor => {
      const shell = document.createElement('div'); shell.className = 'article-editor-shell';
      editor.before(shell); shell.append(editor);
      const toolbar = document.createElement('div'); toolbar.className = 'article-editor-toolbar'; toolbar.setAttribute('role', 'group'); toolbar.setAttribute('aria-label', 'Article formatting'); shell.prepend(toolbar);
      const status = document.createElement('p'); status.className = 'article-editor-status'; status.setAttribute('aria-live', 'polite'); shell.append(status);
      const preview = document.createElement('div'); preview.className = 'article-editor-preview'; preview.hidden = true; shell.append(preview);
      const tools = [['Heading', '\n## ', '', 'Heading'], ['Bold', '**', '**', 'bold text'], ['Italic', '*', '*', 'italic text'], ['List', '\n- ', '', 'List item'], ['Quote', '\n> ', '', 'Quote'], ['Code', '\n```\n', '\n```\n', 'code'], ['Link', '[', '](https://example.com)', 'Link text'], ['Image', '![', '](/media/articles/covers/image.jpg)', 'Image description']];
      tools.forEach(([label, before, after, placeholder]) => {
        const button = document.createElement('button'); button.type = 'button'; button.textContent = label;
        button.addEventListener('click', () => {
          preview.hidden = true; editor.hidden = false; previewButton.textContent = 'Preview';
          const start = editor.selectionStart, end = editor.selectionEnd;
          const selected = editor.value.slice(start, end) || placeholder;
          editor.setRangeText(before + selected + after, start, end, 'end'); editor.focus();
          editor.setSelectionRange(start + before.length, start + before.length + selected.length);
          editor.dispatchEvent(new Event('input', {bubbles: true}));
        }); toolbar.append(button);
      });
      const previewButton = document.createElement('button'); previewButton.type = 'button'; previewButton.textContent = 'Preview'; toolbar.append(previewButton);
      previewButton.addEventListener('click', async () => {
        if (!preview.hidden) { preview.hidden = true; editor.hidden = false; previewButton.textContent = 'Preview'; editor.focus(); return; }
        previewButton.disabled = true;
        try {
          const response = await fetch(editor.dataset.previewUrl, {method: 'POST', credentials: 'same-origin', headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value}, body: new URLSearchParams({body: editor.value})});
          if (!response.ok) throw new Error('Preview unavailable');
          const data = await response.json(); preview.innerHTML = data.html; preview.hidden = false; editor.hidden = true; previewButton.textContent = 'Edit';
        } catch (_) { status.textContent = 'Preview unavailable. Your text is preserved; please try again.'; }
        finally { previewButton.disabled = false; }
      });
      const update = () => { status.textContent = `${editor.value.trim().split(/\s+/).filter(Boolean).length} words · Markdown · Image: replace the URL with your uploaded cover URL or an HTTPS image URL.`; };
      editor.addEventListener('input', update); update();
    });
  });
})();
