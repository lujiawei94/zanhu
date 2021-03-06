import json
from django.test import RequestFactory
from test_plus.test import CBVTestCase
from django.contrib.messages.storage.fallback import FallbackStorage
from zanhu.qa.models import Question, Answer
from zanhu.qa import views

class BaseQATest(CBVTestCase):

    def setUp(self):
        self.user = self.make_user('user1')
        self.other_user = self.make_user('user2')
        self.question_one = Question.objects.create(
            title='问题1',
            user=self.user,
            content='问题1内容',
            tags='测试1, 测试2',
        )
        self.question_two = Question.objects.create(
            user=self.user,
            title='问题2',
            has_answer=True,
            content='问题2内容',
            tags='测试1, 测试2',
        )
        self.answer = Answer.objects.create(
            user=self.user,
            question=self.question_two,
            is_answer=True,
            content='问题2正确答案',
        )

        self.request = RequestFactory().get('/fake-url')
        self.request.user = self.user


class TestQuestionListView(BaseQATest):

    def test_context_data(self):
        response = self.get(views.QuestionListView, request=self.request)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['questions'],
                                 [map(repr, [self.question_one, self.question_two])],
                                 ordered=False)
        self.assertContext('active', 'all')

class TestAnsweredQuestionListView(BaseQATest):

    def test_context_data(self):
        response = self.get(views.AnsweredQuestionListView, request=self.request)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['questions'], [repr(self.question_two)])
        self.assertContext('active', 'answered')


class TestUnAnsweredQuestionListView(BaseQATest):

    def test_context_data(self):
        response = self.get(views.UnansweredQuestionListView, request=self.request)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['questions'], [repr(self.question_one)])
        self.assertContext('active', 'unanswered')

class TestCreateQuestionView(BaseQATest):

    def test_get(self):
        response = self.get(views.CreateQuestionView, request=self.request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '标题')
        self.assertContains(response, '标签')
        self.assertContains(response, '编辑')
        self.assertContains(response, '预览')
        self.assertIsInstance(response.context_data['view'], views.CreateQuestionView)

    def test_post(self):
        data = {
            'title': 'title',
            'content': 'content',
            'tags': 'tag1,tag2',
            'status': 'O'
                }
        request = RequestFactory().post('/fake-url', data=data)
        request.user = self.user
        # RequestFactory测试含有django.contrib.messages的视图 https://code.djangoproject.com/ticket/17971
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.get(views.CreateQuestionView, request=request)
        self.assertEqual(response.status_code, 302)
        assert response.url == '/qa/'

class TestQuestionDetailView(BaseQATest):

    def test_get_context_data(self):
        response = self.get(views.QuestionDetailView, request=self.request, pk=self.question_one.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['question'], self.question_one)


class TestCreateAnswerView(BaseQATest):
    def test_get(self):
        response = self.get(views.CreateAnswerView, request=self.request, question_id=self.question_one.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '编辑')
        self.assertContains(response, '预览')
        self.assertIsInstance(response.context_data['view'], views.CreateAnswerView)

    def test_post(self):
        data = {'content': 'content'}
        request = RequestFactory().post('/fake-url', data=data)
        request.user = self.user
        # RequestFactory测试含有django.contrib.messages的视图 https://code.djangoproject.com/ticket/17971
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.CreateAnswerView, request=request)
        self.assertEqual(response.status_code, 302)
        assert response.url == f'/qa/question-detail/{self.question_one.id}'

class TestQAVote(BaseQATest):

    def setUP(self):
        super(TestQAVote, self).setUp()
        self.request = RequestFactory().post('/fake-url', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.request.POST = self.request.POST.copy()  # 对于不可变对象的处理方式
        self.request.user = self.other_user

    def test_question_upvote(self):
        self.request.POST['question'] = self.question_one.id
        self.request.POST['value'] = 'U'
        response = self.post(views.question_vote, request=self.request)
        self.assertEqual(response.status_code, 200)
        assert json.loads(response.content)['votes'] == 1

    def test_question_downvote(self):
        self.request.POST['question'] = self.question_two.id
        self.request.POST['value'] = 'D'
        response = self.post(views.question_vote, request=self.request)
        assert response.status_code == 200
        assert json.loads(response.content)['votes'] == -1

    def test_answer_upvote(self):
        self.request.POST['answer'] = self.answer.uuid_id
        self.request.POST['value'] = 'U'
        response = self.post(views.answer_vote, request=self.request)
        assert response.status_code == 200
        assert json.loads(response.content)['votes'] == 1

    def test_answer_downvote(self):
        self.request.POST['answer'] = self.answer.uuid_id
        self.request.POST['value'] = 'D'
        response = self.post(views.answer_vote, request=self.request)
        assert response.status_code == 200
        assert json.loads(response.content)['votes'] == -1


    def test_accept_answer(self):
        """接受回答"""
        self.request.user = self.user  # self.user是提问者
        self.request.POST['answer'] = self.answer.uuid_id

        response = views.accept_answer(self.request)  # 等同于 response = self.post(views.accept_answer, request=self.request)

        assert response.status_code == 200
        assert json.loads(response.content)['status'] == 'true'

