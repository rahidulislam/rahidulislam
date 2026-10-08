"""Shared search metadata for managed projects and source-backed defaults."""
from django.templatetags.static import static
from .portfolio_content import fallback_projects


def project_card(project):
    if isinstance(project, dict):
        card = dict(project)
        card['image_url'] = static(card['image']) if card.get('image') else ''
    else:
        source = next((item for item in fallback_projects if item['name'] == project.name), {})
        card = {key: getattr(project, key) for key in ('name', 'slug', 'short_desc', 'project_role', 'validation')}
        card['category'] = project.category.name
        card['image_url'] = project.get_image_url() or ''
        card['image_alt'] = project.image_alt
        card['tags'] = [tag.strip() for tag in project.technologies.splitlines() if tag.strip()] if project.technologies.strip() else source.get('tags', [])
        card['work_type'] = project.work_type or source.get('work_type', '')
    if not card.get('work_type'):
        card['work_type'] = 'frontend' if card['slug'] == 'ilmora-madrasha-management' else 'fullstack' if card['slug'] == 'portfolio-website' else 'backend' if card['slug'] in {'talentbridge', 'smart-document-vault', 'hotelmotel', 'theproperty', 'homeopathic-management-api'} else ''
    card['work_type_label'] = {'backend': 'Backend', 'frontend': 'Frontend', 'fullstack': 'Full-stack'}.get(card['work_type'], 'Unspecified')
    card['search_text'] = ' '.join(str(card.get(key, '')) for key in ('name', 'short_desc', 'category', 'project_role', 'tags')).casefold()
    return card


def filter_catalog(data, query='', work_type='', technology=''):
    cards = [project_card(item) for item in data['fallback_projects']] + [project_card(item) for item in data['projects']]
    technologies = sorted({tag for card in cards for tag in card.get('tags', [])}, key=str.casefold)
    filtered = [card for card in cards if
                all(token in card['search_text'] for token in query.casefold().split()) and
                (not work_type or card['work_type'] == work_type) and
                (not technology or technology.casefold() in [tag.casefold() for tag in card.get('tags', [])])]
    return filtered, technologies
