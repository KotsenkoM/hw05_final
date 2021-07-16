from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AndreyG')
        cls.group = Group.objects.create(
            title='Тестовый текст',
            slug='test_slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_for_guest(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group
        }
        self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_post_for_auth_user(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(self.user.posts.filter(
            text=form_data['text'],
            group=form_data['group'],
        ).exists())

    def test_edit_post(self):
        form_data = {
            'text': 'Другой текст',
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            }),
            data=form_data,
            follow=True
        )
        self.assertTrue(self.user.posts.filter(
            text=form_data['text']
        ).exists())
