import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(publication_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(publication_date=time)
        return self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(publication_date=time)
        return self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, publication_date=time)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['total_questions'], [])

    def test_past_question(self):
        create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['total_questions'],
            ['<Question: Past question>']
        )

    def test_future_question(self):
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['total_questions'], [])

    def test_future_question_and_past_question(self):
        create_question(question_text="Past question", days=-30)
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['total_questions'],
            ['<Question: Past question>']
        )

    def test_two_past_questions(self):
        create_question(question_text="Past Question 1", days=-30)
        create_question(question_text="Past Question 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['total_questions'],
            ['<Question: Past Question 1>', '<Question: Past Question 2>']
        )


class QuestionDetailViewTests(TestCase):

    def test_future_question_detail(self):
        future_question = create_question(question_text="Future Question", days=30)
        response = self.client.get(reverse('polls:details', args=(future_question.id,)))
        self.assertEquals(response.status_code, 404)

    def test_past_question_detail(self):
        past_question = create_question(question_text="Past Question", days=-5)
        response = self.client.get(reverse('polls:details', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text)


class QuestionResultViewTests(TestCase):

    def test_future_question_result(self):
        future_question = create_question(question_text="Future Question", days=5)
        response = self.client.get(reverse('polls:results', args=(future_question.id,)))
        self.assertEquals(response.status_code, 404)

    def test_past_question_result(self):
        past_question = create_question(question_text="Past Question", days=-5)
        response = self.client.get(reverse('polls:results', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text)
