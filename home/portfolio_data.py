"""Shared, live content for the portfolio and its downloadable CV."""
import json
from pathlib import Path

from django.utils.html import strip_tags

from .models import Education, Experience, PersonalInfo, Project, Skill, SocialMedia
from .portfolio_content import fallback_projects


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

    experiences = list(Experience.objects.order_by('-id'))
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
                    'location': record.address, 'description': strip_tags(record.description)}
            used.add(record.pk)
        work.append(item)
    for record in experiences:
        if record.pk not in used:
            work.insert(0, {'role': record.designation, 'company': record.company,
                           'dates': f'{record.start_year} - {record.end_year}',
                           'location': record.address, 'description': strip_tags(record.description)})
    profile['experience'] = work
    education = list(Education.objects.order_by('-id'))
    if education:
        profile['education'] = [f'{item.degree_name} | {item.institute}, {item.address} | '
                                f'{item.start_year} - {item.end_year}. {strip_tags(item.description)}'
                                for item in education]
    skills = list(Skill.objects.values_list('name', flat=True))
    profile['skills'] = skills or profile['skills']
    projects = list(Project.objects.select_related('category').all())
    existing_names = {item.name.casefold() for item in projects}
    curated = [item for item in fallback_projects if item['name'].casefold() not in existing_names]
    cv_projects = curated + [{'name': item.name, 'category': item.category.name,
                              'short_desc': item.short_desc, 'technical_notes': []} for item in projects]
    return {'cv_profile': profile, 'cv_projects': cv_projects, 'social_items': social_items,
            'personal_info': person, 'projects': projects, 'fallback_projects': curated}
