from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()


class PostFormsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_post = Client()
        self.author_post.force_login(self.author)

    def test_send_valid_form_post_create(self):
        """при отправке валидной формы со страницы создания
        поста reverse('posts:post_create')
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={'username': 'test_user'}
            ), msg_prefix='Ошибка редиректа'
        )
        self.assertEqual(Post.objects.count(), posts_count + 1,
                         'Ошибка создания поста')
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Тестовый пост',
            ).exists()
        )

    def test_valid_form_post_edit(self):
        """Тестирование отредактированного поста """
        posts_count = Post.objects.count()
        form_post = {
            'text': 'Измененный  пост',
            'group': self.group.id,
        }
        response = self.author_post.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_post,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                group=self.group.id,
                text='Измененный  пост',
            ).exists()
        )
