from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import (FileExtensionValidator, MaxValueValidator,
                                    MinValueValidator)
from django.templatetags.static import static
from django.utils.text import slugify
# Create your models here.


class SocialMedia(models.Model):
    name = models.CharField(max_length=20)
    social_link = models.URLField()

    def __str__(self):
        return self.name


class PersonalInfo(models.Model):
    name = models.CharField(max_length=100)
    profession = models.CharField(max_length=50)
    short_bio = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    dob = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_available = models.BooleanField(default=True)
    address = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    last_degree = models.CharField(max_length=50, blank=True)
    age = models.IntegerField()
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self) -> str:
        return self.name

    def get_image_url(self):
        return self.image.url if self.image else None


class InformationCounter(models.Model):
    happy_client = models.PositiveIntegerField()
    project = models.PositiveIntegerField()
    support = models.PositiveIntegerField()
    awards = models.PositiveIntegerField()

    def __str__(self):
        return str(self.happy_client)


class Skill(models.Model):
    name = models.CharField(max_length=50)
    value = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    group = models.CharField(max_length=50, default='Core')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['group', 'order', 'name', 'pk']

    def __str__(self):
        return self.name


class Interest(models.Model):
    name = models.CharField(max_length=50)
    icon_name = models.CharField(max_length=50)
    icon_color = models.CharField(max_length=7)

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=50)
    review = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return self.client_name


class Education(models.Model):
    degree_name = models.CharField(max_length=50)
    start_year = models.CharField(max_length=10)
    end_year = models.CharField(max_length=10)
    description = models.TextField()
    institute = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.degree_name


class Experience(models.Model):
    designation = models.CharField(max_length=50)
    start_year = models.CharField(max_length=10)
    end_year = models.CharField(max_length=10)
    description = models.TextField()
    company = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.designation


class ExperienceBullet(models.Model):
    experience = models.ForeignKey(
        Experience, on_delete=models.CASCADE, related_name='bullets')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return f'{self.experience}: {self.text[:60]}'


class Service(models.Model):
    name = models.CharField(max_length=50)
    icon_name = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Project(models.Model):
    EVIDENCE_IMAGES = {
        'TalentBridge': ('img/projects/talentbridge-login.png', 'TalentBridge authentication interface'),
        'Smart Document Vault': ('img/projects/document-vault-live.jpg', 'Smart Document Vault live landing page'),
        'HotelMotel': ('img/projects/hotelmotel-live.jpg', 'HotelMotel live landing page'),
        'TheProperty': ('img/projects/theproperty-live.jpg', 'TheProperty live marketplace landing page'),
        'Homeopathic Management API': ('img/projects/homeopathic-live.jpg', 'CuraLink live homeopathic management landing page'),
    }
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='project_category')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, null=True, blank=True)
    short_desc = models.CharField(max_length=100)
    image = models.ImageField('Featured image', upload_to='images/', blank=True)
    url = models.URLField('Live URL', blank=True)
    description = models.TextField(blank=True)
    features = models.TextField(blank=True, help_text='Enter one feature per line.')
    problem = models.TextField(blank=True, help_text='Who needed this and what problem did it address?')
    contribution = models.TextField(blank=True, help_text='Describe your own responsibilities, not the whole team’s work.')
    technical_decisions = models.TextField(blank=True, help_text='Explain implementation choices and tradeoffs. One decision per paragraph.')
    outcome = models.TextField(blank=True, help_text='Describe delivered capabilities. Include metrics only when verified.')
    lessons = models.TextField(blank=True, help_text='What did you learn or what would you improve next?')
    repository_url = models.URLField(blank=True)
    api_docs_url = models.URLField(blank=True)
    architecture_summary = models.TextField(blank=True)
    project_type = models.CharField(max_length=120, blank=True)
    project_role = models.CharField(max_length=120, blank=True)
    collaboration = models.CharField(max_length=120, blank=True)
    development_status = models.CharField(max_length=80, blank=True)
    contribution_areas = models.TextField(
        blank=True, help_text='Enter one contribution area per line.')
    constraints = models.TextField(blank=True)
    validation = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    client_name = models.CharField(max_length=100, blank=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['order', '-date', '-pk']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name) or 'project'
            candidate = base_slug[:120]
            suffix = 2
            while Project.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
                suffix_text = f'-{suffix}'
                candidate = f'{base_slug[:120 - len(suffix_text)]}{suffix_text}'
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def get_image_url(self):
        if self.image:
            return self.image.url
        evidence = self.EVIDENCE_IMAGES.get(self.name)
        return static(evidence[0]) if evidence else None

    @property
    def image_alt(self):
        evidence = self.EVIDENCE_IMAGES.get(self.name)
        return evidence[1] if evidence else f'{self.name} project preview'


class ProjectImage(models.Model):
    SCREENSHOT = 'screenshot'
    ARCHITECTURE = 'architecture'
    KIND_CHOICES = (
        (SCREENSHOT, 'Screenshot'),
        (ARCHITECTURE, 'Architecture diagram'),
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='project_image')
    image = models.ImageField(upload_to='project/', blank=True)
    caption = models.CharField(max_length=200, blank=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=SCREENSHOT)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return self.project.name

    def get_image_url(self):
        return self.image.url if self.image else None

    @property
    def image_alt(self):
        return self.alt_text or self.caption or self.project.image_alt


class EngineeringChallenge(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='engineering_challenges')
    title = models.CharField(max_length=120)
    problem = models.TextField(blank=True)
    approach = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    trade_offs = models.TextField(blank=True)
    verification = models.TextField(
        blank=True, help_text='State only results that can be verified.')
    source_url = models.URLField(blank=True, help_text='Optional source supporting the verification.')
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return f'{self.project}: {self.title}'


class ProjectMetric(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='metrics')
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    explanation = models.TextField(blank=True)
    source_url = models.URLField(blank=True, help_text='Source or measurement documentation for this metric.')
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return f'{self.project}: {self.label}'


def validate_video_size(value):
    if value.size > 50 * 1024 * 1024:
        raise ValidationError('Video files must be 50 MiB or smaller.')


class ProjectVideo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='videos')
    file = models.FileField(
        upload_to='project/videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogv']), validate_video_size],
    )
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    def clean(self):
        super().clean()
        if not self.file:
            raise ValidationError({'file': 'A video file is required.'})

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return self.project.name


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.email
