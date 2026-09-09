"""In-memory Europass-style CV PDF renderer."""
from io import BytesIO
from copy import copy
from pathlib import Path
from re import sub
from threading import Lock
from xml.sax.saxutils import escape
import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
BLUE=colors.HexColor('#174c78'); INK=colors.HexColor('#172b3a'); GREY=colors.HexColor('#52616c')
_LOCK=Lock(); _READY=False
def _fonts():
    global _READY
    with _LOCK:
        if not _READY:
            root=Path(reportlab.__file__).parent/'fonts'; pdfmetrics.registerFont(TTFont('CVSans',str(root/'Vera.ttf'))); pdfmetrics.registerFont(TTFont('CVSans-Bold',str(root/'VeraBd.ttf'))); pdfmetrics.registerFontFamily('CVSans',normal='CVSans',bold='CVSans-Bold'); _READY=True
def _clean(v): return escape(sub(r'<[^>]*>','', '' if v is None else str(v)))
def build_cv(profile, projects):
    _fonts(); profile=profile or {}; projects=projects or []
    s={'body':ParagraphStyle('cv-body',fontName='CVSans',fontSize=9.5,leading=12,textColor=INK,spaceAfter=3),'label':ParagraphStyle('cv-label',fontName='CVSans-Bold',fontSize=9,leading=12,textColor=BLUE),'title':ParagraphStyle('cv-title',fontName='CVSans-Bold',fontSize=25,leading=29,textColor=BLUE,spaceAfter=8),'role':ParagraphStyle('cv-role',fontName='CVSans-Bold',fontSize=12,leading=16,textColor=INK,spaceAfter=6),'small':ParagraphStyle('cv-small',fontName='CVSans',fontSize=9,leading=12,textColor=GREY,spaceAfter=4)}
    def p(v,k='body'): return Paragraph(_clean(v),s[k])
    def section(label, items):
        heading = Paragraph(label, s['label'])
        heading.keepWithNext = True
        story.extend([Spacer(1, 6), heading, Spacer(1, 4)])
        for item in items:
            if isinstance(item, Paragraph):
                item.style = copy(item.style)
                item.style.leftIndent = 0
            story.append(item)
    story=[Paragraph('CURRICULUM VITAE',s['label']),Spacer(1,12),p(profile.get('name',''),'title'),p(profile.get('role',''),'role'),Spacer(1,8)]
    contacts=[p(profile.get('location',''))]
    for key in ('email','phone','website','github','linkedin'):
        v=profile.get(key)
        if v:
            href=('mailto:'+str(v)) if key=='email' else str(v)
            contacts.append(Paragraph('<link href="%s" color="#174c78">%s</link>'%(escape(href,{'"':'&quot;'}),_clean(v)),s['body']) if href.startswith(('http://','https://','mailto:')) else p(v))
    section('PERSONAL INFORMATION',contacts); section('ABOUT ME',[p(profile.get('summary',''))])
    work=[]
    for x in profile.get('experience',[]):
        work += [p(x.get('dates',''),'small'),Paragraph('<b>%s</b>'%_clean(x.get('role','')),s['body']),p('%s | %s'%(x.get('company',''),x.get('location','')))]
        if x.get('description'): work.append(p(x['description']))
        work.append(Spacer(1,3))
    section('WORK EXPERIENCE',work)
    if profile.get('education'): section('EDUCATION AND TRAINING',[p(x) for x in profile['education']])
    if profile.get('skills'): section('DIGITAL SKILLS',[p(' / '.join(map(str,profile['skills'])))])
    items=[]
    for x in projects:
        items += [Paragraph('<b>%s</b> - %s'%(_clean(x.get('name','')),_clean(x.get('category',''))),s['body']),p(x.get('short_desc',''))]
        if x.get('technical_notes'): items.append(p(' / '.join(map(str,x['technical_notes'])),'small'))
    section('PROJECTS',items); section('LANGUAGE SKILLS',[p(x) for x in profile.get('languages',[])])
    out=BytesIO()
    def footer(c,d): c.setTitle(str(profile.get('name',''))+' - Python Developer CV'); c.setAuthor(str(profile.get('name',''))); c.setFont('CVSans',8); c.setFillColor(GREY); c.drawString(42,24,'Europass-style CV | '+str(profile.get('name',''))); c.drawRightString(A4[0]-42,24,'Page %d'%d.page)
    SimpleDocTemplate(out,pagesize=A4,rightMargin=42,leftMargin=42,topMargin=34,bottomMargin=42).build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
