from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsUrlTests(TestCase):
    """Тестируем urls"""

    @classmethod
    def setUpClass(cls):
        cache.clear()
        super().setUpClass()
        cls.endpoint_posts_index = '/'
        cls.template_posts_index = 'posts/index.html'
        cls.endpoint_posts_group_list = '/group/slug/'
        cls.template_posts_group_list = 'posts/group_list.html'
        cls.endpoint_posts_profile = '/profile/auth/'
        cls.template_posts_profile = 'posts/profile.html'
        cls.endpoint_posts_post_detail = 'posts/post_detail.html'
        cls.template_posts_post_detail = 'posts/post_detail.html'
        cls.endpoint_posts_post_create = '/create/'
        cls.template_posts_post_create = 'posts/create_post.html'
        cls.endpoint_posts_post_edit = 'posts/post_edit'
        cls.template_posts_post_edit = 'posts/create_post.html'

        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.not_authorized_user = User.objects.create_user(username='NoName')
        self.user_2 = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_2)
        self.post_author = Client()
        self.post_author.force_login(self.user)

    def test_unexisting_page(self):
        """Страница unexisting_page вернет ошибку 404"""
        response = self.guest_client.get('/unexisting_page/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_edit_page_available_for_author_only(self):
        """Страница /posts/<post_id>/edit доступна только автору"""
        response = self.post_author.get(f'/posts/{self.post.pk}/edit/')

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_page_available_for_authorized_user_only(self):
        """Создание странички доступно только авторизованному"""
        response = self.authorized_client.get(self.endpoint_posts_post_create)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_available_for_guest_client(self):
        """Страницы доступны всем пользователям"""
        url_names = (
            self.endpoint_posts_index, self.endpoint_posts_group_list,
            self.endpoint_posts_profile, f'/posts/{self.post.pk}/',
        )

        for address in url_names:
            with self.subTest(address=address):
                response = self.post_author.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_refers_to_correct_template_for_all(self):
        """ Для каждого URL-адреса отрисовывается
        правильный шаблон для всех пользователей.
        """
        templates_and_url_names = {
            self.endpoint_posts_index: self.template_posts_index,
            self.endpoint_posts_group_list: self.template_posts_group_list,
            self.endpoint_posts_profile: self.template_posts_profile,
            f'/posts/{self.post.pk}/': self.endpoint_posts_post_detail,
            self.endpoint_posts_post_create: self.template_posts_post_create,
            f'/posts/{self.post.pk}/edit/': self.template_posts_post_edit,
        }

        for address, template in templates_and_url_names.items():
            with self.subTest(template=template):
                response = self.post_author.get(address)

                self.assertTemplateUsed(response, template)

    def test_url_refers_to_correct_template_for_authorized(self):
        """ Для URL-адреса создания поста отрисовывается
        правильный шаблон для авторизованного пользователя.
        """
        response = self.authorized_client.get(self.endpoint_posts_post_create)

        self.assertTemplateUsed(response, self.template_posts_post_create)

    def test_url_refers_to_correct_template_for_author(self):
        response = self.post_author.get(f'/posts/{self.post.pk}/edit/')

        self.assertTemplateUsed(response, self.template_posts_post_create)

    def test_create_redirect_anonymous_on_admin_login(self):
        """Проверка редиректа анонимного пользователя
        при редактировании поста
        """
        response = self.guest_client.get(
            self.endpoint_posts_post_create, follow=True
        )

        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_edit_redirect_authorized_not_author_on_profile(self):
        """Проверка редиректа авторизованого пользователя и
        не автора при редактировании
        """
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )

        self.assertRedirects(
            response, self.endpoint_posts_profile
        )
