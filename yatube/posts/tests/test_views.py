from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User, Follow


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа',
            slug='test-slug',
        )
        cls.user = User.objects.create_user(username='Тестовое имя')
        cls.user2 = User.objects.create(username='User_2')
        cls.post = Post.objects.create(
            text='Тест',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_user2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_user2.force_login(self.user2)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('index'),
            'new_post.html': reverse('new_post'),
            'group.html': reverse('group', kwargs={'slug': self.group.slug}),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        first_post = response.context['page'][0]
        self.assertEqual(first_post, self.post)

    def test_group_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )
        context_page = response.context['group']
        self.assertEqual(context_page.title, self.group.title)
        self.assertEqual(context_page.slug, self.group.slug)

    def test_new_page_shows_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('post_edit', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))
        self.assertEqual(response.context['post'], self.post)

    def test_profile_page_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('profile', kwargs={
            'username': self.user.username,
        }))
        self.assertEqual(response.context['author'], self.user)

    def test_post_page_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))
        self.assertEqual(response.context['post'], self.post)

    def test_group_shows_new_post(self):
        """Новый пост появился в указанной группе."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page']), 1)

    def test_user_follow(self):
        """Подписка на автора работает правильно."""
        Follow.objects.get_or_create(user=self.user2, author=self.user)
        self.authorized_client.get(
            reverse('profile_follow',
                    kwargs={'username': self.user}))
        follow = Follow.objects.first()
        count = Follow.objects.count()
        self.assertEqual(count, 1)
        self.assertEqual(follow.user, self.user2)
        self.assertEqual(follow.author, self.user)

    def test_user_unfollow(self):
        """Отписка от других пользователей работает правильно."""
        Follow.objects.create(user=self.user2, author=self.user)
        self.authorized_client.get(
            reverse('profile_unfollow',
                    kwargs={'username': self.user}))
        count = Follow.objects.count()
        self.assertEqual(count, 1)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый текст',
            slug='test',
        )
        cls.user = User.objects.create_user(username='StasBasov')
        for number in range(13):
            Post.objects.create(
                group=cls.group,
                author=cls.user,
                text='Тестовый текст' + str(number),
            )

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
