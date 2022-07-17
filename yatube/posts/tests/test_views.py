from http import HTTPStatus

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Comment

User = get_user_model()


class PostViewsTest(TestCase):
    '''Класс для тестирования View'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.endpoint_posts_index = 'posts:index'
        cls.template_posts_index = 'posts/index.html'
        cls.endpoint_posts_group_list = 'posts:group_list'
        cls.template_posts_group_list = 'posts/group_list.html'
        cls.endpoint_posts_profile = 'posts:profile'
        cls.template_posts_profile = 'posts/profile.html'
        cls.endpoint_posts_post_detail = 'posts:post_detail'
        cls.template_posts_post_detail = 'posts/post_detail.html'
        cls.endpoint_posts_post_create = 'posts:post_create'
        cls.template_posts_post_create = 'posts/create_post.html'
        cls.endpoint_posts_post_edit = 'posts:post_edit'
        cls.template_posts_post_edit = 'posts/create_post.html'
        cls.endpoint_posts_add_comment = 'posts:add_comment'

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

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
            image=uploaded,
            
        )
        cls.new_group = Group.objects.create(
            title='Новая группа',
            slug='test-slug_new',
            description='Новое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.post_author = Client()
        self.user_2 = User.objects.create_user(username='No')
        self.authorized_client.force_login(self.user_2)
        self.post_author.force_login(self.user)
        
    def test_comment_only_authorized_user(self):
        """Оставить комент может только авторизованный user"""
        response = self.guest_client.get(
            reverse('posts:add_comment',
            kwargs={'post_id': self.post.id}
            )
        )
        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse(self.endpoint_posts_index): self.template_posts_index,
            reverse(self.endpoint_posts_group_list,
                    kwargs={'slug': self.group.slug}):
            self.template_posts_group_list,
            reverse(self.endpoint_posts_profile,
                    kwargs={'username': self.user}):
            self.template_posts_profile,
            reverse(self.endpoint_posts_post_detail,
                    kwargs={'post_id': self.post.id}):
            self.template_posts_post_detail,
            reverse(self.endpoint_posts_post_create):
            self.template_posts_post_create,
            reverse(self.endpoint_posts_post_edit,
                    kwargs={'post_id': self.post.id}):
            self.template_posts_post_edit,
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.post_author.get(template)

                self.assertTemplateUsed(response, reverse_name)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(self.endpoint_posts_index))

        self.assertEqual(
            response.context['page_obj'].object_list[0], self.post)
        
        self.assertEqual(
            response.context['page_obj'].object_list[0].image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(self.endpoint_posts_group_list,
                    kwargs={'slug': self.group.slug}
                    )
        )

        test_group_title = response.context.get('group').title
        test_group = response.context.get('group').description
        test_group_image = response.context['page_obj'].object_list[0].image

        self.assertEqual(test_group_title, 'Тестовая группа')
        self.assertEqual(test_group, self.group.description)
        self.assertEqual(test_group_image, self.post.image)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                self.endpoint_posts_profile, kwargs={'username': self.user}
            )
        )
        
        test_image = response.context['page_obj'].object_list[0].image
        test_author = response.context.get('author')

        self.assertEqual(test_author, self.post.author)
        self.assertEqual(test_image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.post_author.get(
            reverse(
                self.endpoint_posts_post_detail,
                kwargs={'post_id': self.post.id}
            )
        )

        self.assertEqual(response.context.get('post'), self.post)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом """
        response = self.post_author.get(
            reverse(self.endpoint_posts_post_create)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context_in_addit(self):
        """Швблон сформирован с правильным контекстом
        после редактироывания
        """
        response = self.post_author.get(
            reverse(self.endpoint_posts_post_edit,
                    kwargs={'post_id': self.post.id}
                    )
        )
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)
    def test_comment_on_post(self):
        """После отправки комментария он появляется на странице поста"""
        # делаешь пост коммента
        comment = Comment.objects.create(
            text = 'Пробный текст',
            post_id = self.post.id,
            author = self.user_2,
        )
        # открваешь вьюху поста
        response = self.authorized_client.get(
            reverse(
                self.endpoint_posts_add_comment,
                kwargs ={'post_id': self.post.id}
            )
        )
        # проверка что в контектсе ресопса есть есть такой комментарий
        print(response.context)
        print("aaaaaaaaaaaaa")

        comments = response.context.get('comments')
        self.assertIn(comments.values_list('id',flat=True), comment)
        
    def test_check_post_on_create(self):
        """Проверка, что пост правильно добавляется на страницы."""
        pages = (
            reverse(self.endpoint_posts_index),
            reverse(self.endpoint_posts_group_list,
                    kwargs={'slug': self.group.slug}
                    ),
            reverse(self.endpoint_posts_profile,
                    kwargs={'username': self.user}
                    )
        )

        for address in pages:
            with self.subTest(address=address):

                response = self.post_author.get(address)

                self.assertEqual(response.context.get('page_obj')[0],
                                 self.post)

    def test_check_post_on_the_right_group(self):
        """Проверка, что пост не попал в группу,
        для которой не был предназначен.
        """
        fake_group = Group.objects.create(
            title='Тестовый заголовок',
            slug='fake-slug',
            description='Тестовое описание',
        )

        response = self.post_author.get(
            reverse(
                self.endpoint_posts_group_list,
                args=[fake_group.slug]
            )
        )

        self.assertNotIn(self.post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.endpoint_posts_index = 'posts:index'
        cls.endpoint_posts_group_list = 'posts:group_list'
        cls.endpoint_posts_profile = 'posts:profile'
        cls.endpoint_posts_post_edit = 'posts:post_edit'

        cls.CONST_POST_PER_SECOND_PAGE = 3
        cls.CONST_all_posts = settings.POST_PER_PAGE + (
            cls.CONST_POST_PER_SECOND_PAGE)
        super().setUpClass()
        cls.author = User.objects.create_user(username='Vitya')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )

        for created_post in range(cls.CONST_all_posts):
            Post.objects.create(
                text=f'Текст {created_post}',
                author=cls.author,
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """Первая страница index содержит десять записей."""
        pages_with_paginator = (
            reverse(self.endpoint_posts_index),
            reverse(self.endpoint_posts_group_list,
                    kwargs={'slug': self.group.slug}),
            reverse(self.endpoint_posts_profile,
                    kwargs={'username': self.author})
        )

        for address in pages_with_paginator:
            response = self.guest_client.get(address)

            self.assertEqual(
                len(response.context['page_obj']), settings.POST_PER_PAGE)

    def test_second_page_contains_3_records(self):
        """Вторая страница index содердит три записи."""
        pages_with_paginator = (
            reverse(self.endpoint_posts_index),
            reverse(self.endpoint_posts_group_list,
                    kwargs={'slug': self.group.slug}),
            reverse(self.endpoint_posts_profile,
                    kwargs={'username': self.author})
        )

        for address in pages_with_paginator:
            response = self.guest_client.get(address + '?page=2')

            self.assertEqual(
                len(response.context['page_obj']), 3
            )
