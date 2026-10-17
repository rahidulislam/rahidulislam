from markdown_it import MarkdownIt


def render_article(text: str | None) -> str:
    """One safe renderer shared by published articles and staff previews."""
    return MarkdownIt("js-default", {"breaks": True}).render(text or "")
