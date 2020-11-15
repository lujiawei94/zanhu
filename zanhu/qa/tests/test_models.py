from test_plus import TestCase
from zanhu.articles.models import Article


class ArticleModelsTest(TestCase):

    def setUp(self):
        self.user = self.make_user('user1')
        self.other_user = self.make_user('user2')
        self.article = Article.objects.create(
            title='第一篇文章',
            user=self.user,
            content='第一篇文章内容',
            status='P',
        )
        self.draft_article = Article.objects.create(
            title='第二篇文章',
            user=self.user,
            content='第二篇草稿内容',
        )

    def test_object_instance(self):
        assert isinstance(self.article, Article)
        assert isinstance(self.draft_article, Article)
        assert isinstance(Article.objects.get_published()[0], Article)
        assert isinstance(Article.objects.get_drafts()[0], Article)

    def test_return_values(self):
        assert self.article in Article.objects.get_published()
        assert self.draft_article in Article.objects.get_drafts()
        assert Article.objects.get_drafts()[0].__str__() == '第二篇文章'
        assert Article.objects.get_published()[0].__str__() == '第一篇文章'

