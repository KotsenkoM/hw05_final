from django.test import TestCase

from ..models import User, Post, Group


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа'
        )
        cls.user = User.objects.create(
            username='Тестовое имя',
        )
        cls.post = Post.objects.create(
            text='Тест' * 100,
            group=cls.group,
            author=cls.user,
        )

    def test_str_field(self):
        post = PostModelTest.post
        self.assertEqual(str(post), self.post.text[:15])

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите содержание Вашей публикации',
            'group': 'Укажите сообщество',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
