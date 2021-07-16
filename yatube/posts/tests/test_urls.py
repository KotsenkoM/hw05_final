from http import HTTPStatus
from django.test import TestCase, Client

from ..models import Group, User, Post


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Тестовое имя')
        cls.not_author_user = User.objects.create_user(
            username='Не автор поста'
        )
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.wrong_user = Client()
        self.wrong_user.force_login(self.not_author_user)

    def test_urls_for_not_authorized_users(self):
        """Страница доступна любому пользователю."""
        url_names = (
            '/',
            f'/group/{self.group.slug}/',
            f'/{self.user.username}/',
            f'/{self.user.username}/{self.post.id}/',
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects_for_not_authorized_users(self):
        url_names = (
            '/new/',
            f'/{self.user.username}/{self.post.id}/edit/',
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_for_authorized_users(self):
        """Страница доступна для авторизованных пользователей"""
        url_names = (
            '/new/',
            f'/{self.user.username}/{self.post.id}/edit/',
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_page_for_not_author(self):
        url = f'/{self.user.username}/{self.post.id}/edit/'
        response = self.wrong_user.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            '/new/': 'new_post.html',
            f'/group/{self.group.slug}/': 'group.html',
            f'/{self.user.username}/{self.post.id}/edit/': 'new_post.html',
            f'/{self.user.username}/': 'profile.html',
            f'/{self.user.username}/{self.post.id}/': 'post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_not_found(self):
        """Сервер возвращает код 404, если страница не найдена."""
        url = 'несуществующая страница'
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
