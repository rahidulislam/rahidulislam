"""Shared, live content for the portfolio and its downloadable CV."""
import json
from pathlib import Path

from django.utils.html import strip_tags

from .models import Education, Experience, PersonalInfo, Project, Skill, SocialMedia
from .portfolio_content import fallback_projects


SKILL_GROUPS = {
    'Python': 'Backend Engineering', 'Django': 'Backend Engineering',
    'Django REST Framework': 'Backend Engineering', 'REST APIs': 'Backend Engineering',
    'PostgreSQL': 'Database', 'MySQL': 'Database', 'SQLite': 'Database',
    'Django ORM': 'Database', 'JWT authentication': 'Authentication & Security',
    'OAuth2': 'Authentication & Security', 'Redis': 'Async & Caching',
    'Celery': 'Async & Caching', 'Docker': 'DevOps', 'Nginx': 'DevOps',
    'GitHub Actions': 'DevOps', 'Git': 'DevOps', 'GitHub': 'DevOps',
    'Pytest': 'Testing & API Tools', 'OpenAPI': 'Testing & API Tools',
    'Swagger': 'Testing & API Tools',
}


def get_portfolio_data():
    profile = json.loads(Path(__file__).with_name('cv_profile.json').read_text())
    person = PersonalInfo.objects.first()
    if person:
        for target, source in [('name', 'name'), ('role', 'profession'), ('location', 'address'),
                               ('email', 'email'), ('phone', 'phone'), ('website', 'website')]:
            value = getattr(person, source)
            if value:
                profile[target] = value
        if person.bio or person.short_bio:
            profile['summary'] = strip_tags(person.bio or person.short_bio)
    links = {name: profile.get(name, '') for name in ('github', 'linkedin')}
    social = list(SocialMedia.objects.all())
    for item in social:
        if item.name.casefold() in links:
            links[item.name.casefold()] = item.social_link
    profile.update(links)
    social_items = [{'name': name.title() if name != 'github' else 'GitHub', 'social_link': url}
                    for name, url in links.items() if url]
    social_items += [item for item in social if item.name.casefold() not in links]

    experiences = list(Experience.objects.prefetch_related('bullets').order_by('-id'))
    def key(company):
        value = company.casefold().strip()
        return 'wege' if value in ('wege', 'wege llc', 'wege general llc') else value
    replacements = {key(item.company): item for item in experiences}
    work = []
    used = set()
    for item in profile['experience']:
        identity = key(item['company'])
        record = replacements.get(identity)
        if record:
            item = {'role': record.designation, 'company': record.company,
                    'dates': f'{record.start_year} - {record.end_year}',
                    'location': record.address, 'description': strip_tags(record.description),
                    'bullets': [strip_tags(bullet.text) for bullet in record.bullets.all()]}
            used.add(record.pk)
        work.append(item)
    for record in experiences:
        if record.pk not in used:
            work.insert(0, {'role': record.designation, 'company': record.company,
                            'dates': f'{record.start_year} - {record.end_year}',
                           'location': record.address, 'description': strip_tags(record.description),
                           'bullets': [strip_tags(bullet.text) for bullet in record.bullets.all()]})
    profile['experience'] = work
    education = list(Education.objects.order_by('-id'))
    if education:
        profile['education'] = [f'{item.degree_name} | {item.institute}, {item.address} | '
                                f'{item.start_year} - {item.end_year}. {strip_tags(item.description)}'
                                for item in education]
    skill_records = list(Skill.objects.all())
    skills = [skill.name for skill in skill_records]
    profile['skills'] = skills or profile['skills']
    projects = list(Project.objects.filter(is_published=True).select_related('category').all())
    existing_names = {name.casefold() for name in Project.objects.values_list('name', flat=True)}
    curated = [item for item in fallback_projects if item['name'].casefold() not in existing_names]
    cv_projects = curated + [{'name': item.name, 'category': item.category.name,
                              'short_desc': item.short_desc, 'technical_notes': item.features.splitlines()} for item in projects]
    grouped = {}
    for skill in skill_records:
        grouped.setdefault(skill.group, []).append(skill)
    if not skill_records:
        for name in profile['skills']:
            group = SKILL_GROUPS.get(name, 'Web & Tools')
            grouped.setdefault(group, []).append({'name': name})
    skill_groups = [{'name': name, 'skills': group_skills} for name, group_skills in grouped.items()]
    return {'cv_profile': profile, 'cv_projects': cv_projects, 'social_items': social_items,
            'skill_groups': skill_groups,
            'personal_info': person, 'projects': projects, 'fallback_projects': curated}
