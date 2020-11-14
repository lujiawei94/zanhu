import tempfile
from PIL import Image
from test_plus import TestCase
from django.test import Client, override_settings
from django.urls import reverse
from zanhu.articles.models import Article


class ArticleViewsTest(TestCase):

    @staticmethod
    def get_temp_img():
        """创建并读取临时图像"""
        size = (200, 200)
        color = (255, 0, 0, 0)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image = Image.new('RGB', size, color)
            image.save(f, 'PNG')
        return open(f.name, mode='rb')

    def setUp(self):
        self.user = self.make_user('user')
        #self.client = Client()
        self.client.login(user='user', password='password')
        self.article = Article.objects.create(
            title="文章标题",
            content="文章内容",
            status="P",
            user=self.user,
        )
        self.test_img = self.get_temp_img()

    def tearDown(self):
        self.test_img.close()

    def test_index_articles(self):
        """测试文章列表页"""
        response = self.client.get(reverse('articles:list'))
        self.assertEqual(response.status_code, 200)

    def test_article(self):
        """访问文章"""
        response = self.client.get(reverse('articles:article', kwargs={'slug': 'wen-zhang-biao-ti'}))
        self.assertEqual(response.status_code, 200)

    def test_404_error(self):
        """访问不存在的文章"""
        response = self.client.get(reverse('articles:article', kwargs={'slug': 'no-slug'}))
        self.assertEqual(response.status_code, 404)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_article(self):
        """测试文章创建后跳转"""
        response = self.client.post(reverse("articles:write_new"),
                                    {"title": "这是文章标题",
                                     "content": "这是文章内容",
                                     "tags": "测试",
                                     "status": "P",
                                     "image": self.test_img})
        assert response.status_code == 302

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_multi_articles(self):
        """测试多篇文章发表"""
        published_count = Article.objects.get_published().count()
        draft_count = Article.objects.get_drafts().count()
        articles_count = Article.objects.count()
        response1 = self.client.post(reverse("articles:write_new"),
                                    {"title": "这是文章标题1",
                                     "content": "这是文章内容1",
                                     "tags": "测试",
                                     "status": "P",
                                     "image": self.test_img})
        self.assertEqual(Article.objects.get_published().count(), published_count + 1)
        self.assertEqual(Article.objects.count(), articles_count+1)
        response2 = self.client.post(reverse("articles:write_new"),
                                    {"title": "这是文章标题2",
                                     "content": "这是文章内容2",
                                     "tags": "测试",
                                     "status": "D",
                                     "image": self.test_img})
        self.assertEqual(Article.objects.get_drafts().count(), draft_count+1)
        self.assertEqual(Article.objects.count(), articles_count+2)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_draft_articles(self):
        """测试草稿箱功能"""
        response = self.client.post(reverse("articles:write_new"),
                                    {"title": "草稿文章",
                                     "content": "草稿箱的文章",
                                     "tags": "测试",
                                     "status": "D",
                                     "image": self.test_img})
        resp = self.client.get(reverse("articles:drafts"))
        assert resp.status_code == 200
        assert response.status_code == 302
        assert resp.context["articles"][0].slug == "cao-gao-wen-zhang"

