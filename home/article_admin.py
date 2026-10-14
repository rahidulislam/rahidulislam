from django import forms
from django.urls import reverse
from .models import Article


class ArticleEditor(forms.Textarea):
    def __init__(self, attrs=None):
        super().__init__({'class': 'article-markdown-editor', 'rows': 20, **(attrs or {})})

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['data-preview-url'] = reverse('admin:home_article_preview')
        return context

    class Media:
        css = {'all': ('admin/css/article-editor.css',)}
        js = ('admin/js/article-editor.js',)


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {'body': ArticleEditor(), 'body_bn': ArticleEditor()}
