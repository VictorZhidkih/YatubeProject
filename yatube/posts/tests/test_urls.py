from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsUrlTests(TestCase):
    """Тестируем urls"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись, юзера и группу в БД
        # и сохраняем их в качестве переменных класса
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user_2 = User.objects.create_user(username='HasNoName')
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user_2)
        # Получаем и авторизуем автора, а также создаем авторизованный клиент
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

    def test_urls_refers_to_correct_template_for_all(self):
        """ Для каждого URL-адреса отрисовывается
        правильный шаблон для всех пользователей.
        """
        templates_and_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
        }
        for template, address in templates_and_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_refers_to_correct_template_for_authorized(self):
        """ Для URL-адреса создания поста отрисовывается
        правильный шаблон для авторизованного пользователя.
        """
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_url_refers_to_correct_template_for_author(self):
        response = self.post_author.get(f'/posts/{self.post.pk}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
