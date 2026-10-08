"""Reserve source-backed experience URLs when generating managed slugs."""
FALLBACK_SLUGS = {
    'talentbridge': 'talentbridge',
    'wege': 'wege-llc',
    'meektec it': 'meektec-it',
    'research rider': 'research-rider',
}


def experience_identity(company):
    value = company.casefold().strip()
    return 'wege' if value in ('wege', 'wege llc', 'wege general llc') else value


def reserved_experience_slugs(company):
    identity = experience_identity(company)
    return {slug for name, slug in FALLBACK_SLUGS.items() if name != identity}
