from django import forms
from markdownx.fields import MarkdownxFormField

from zanhu.articles.models import Article

class ArticleForm(forms.ModelForm):

    content = MarkdownxFormField()

    class Meta:
        model = Article
        fields = ['title', 'content', 'image', 'tags']
