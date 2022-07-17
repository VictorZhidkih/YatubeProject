# import shutil
# import tempfile

# from posts.forms import PostForm
# from django.conf import settings
# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.contrib.auth import get_user_model
# from django.test import Client, TestCase, override_settings
# from django.urls import reverse

# from ..models import Group, Post

# # Создаем временную папку для медиа-файлов;
# # на момент теста медиа папка будет переопределена
# TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

# User = get_user_model()


# # Для сохранения media-файлов в тестах будет использоваться
# # временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
# @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
# class PostFormsTest(TestCase):

#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.author = User.objects.create_user(username='auth')
#         cls.group = Group.objects.create(
#             title='Тестовая группа',
#             slug='test_slug',
#             description='Тестовое описание',
#         )
#         cls.post = Post.objects.create(
#             author=cls.author,
#             text='Тестовый пост',
#             group=cls.group,
#         )
#         cls.form = PostForm()

#     @classmethod
#     def tearDownClass(cls):
#         super().tearDownClass()
#         shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

#     def setUp(self):
#         self.user = User.objects.create_user(username='test_user')
#         self.authorized_client = Client()
#         self.authorized_client.force_login(self.user)
#         self.author_post = Client()
#         self.author_post.force_login(self.author)

#     def test_send_valid_form_post_create(self):
#         """Валидная форма создает новый пост авторизованным пользователем."""
#         posts_count = Post.objects.count()
#         small_gif = (
#             b'\x47\x49\x46\x38\x39\x61\x02\x00'
#             b'\x01\x00\x80\x00\x00\x00\x00\x00'
#             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
#             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
#             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
#             b'\x0A\x00\x3B'
#         )
#         uploaded = SimpleUploadedFile(
#             name='small.gif',
#             content=small_gif,
#             content_type='image/gif'
#         )
#         form_data = {
#             'text': 'Тестовый пост',
#             'group': self.group.id,
#             'image': uploaded,
#         }

#         response = self.authorized_client.post(
#             reverse('posts:post_create'),
#             data=form_data,
#             follow=True
#         )

#         self.assertRedirects(
#             response,
#             reverse(
#                 'posts:profile', kwargs={'username': 'test_user'}
#             ), msg_prefix='Ошибка редиректа'
#         )
#         self.assertEqual(Post.objects.count(), posts_count + 1,
#                          'Ошибка создания поста')

#         self.assertTrue(
#             Post.objects.filter(
#                 author=self.user,
#                 text='Тестовый пост',
#                 group=self.group.id,
#                 image='posts/small.gif'
#             ).exists()
#         )

#     def test_valid_form_post_edit(self):
#         """Тестирование отредактированного поста """
#         posts_count = Post.objects.count()
#         big_gif = (
#             b'\x47\x49\x46\x38\x39\x61\x02\x00'
#             b'\x01\x00\x80\x00\x00\x00\x00\x00'
#             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
#             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
#             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
#             b'\x0A\x00\x3B'
#         )
#         uploaded = SimpleUploadedFile(
#             name='big.gif',
#             content=big_gif,
#             content_type='image/gif'
#         )
#         form_post = {
#             'text': 'Измененный  пост',
#             'group': self.group.id,
#             'image': uploaded,
#         }

#         response = self.author_post.post(
#             reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
#             data=form_post,
#             follow=True
#         )

#         self.assertRedirects(
#             response, reverse(
#                 'posts:post_detail', kwargs={'post_id': self.post.id}
#             )
#         )
#         self.assertEqual(Post.objects.count(), posts_count)
#         self.assertTrue(
#             Post.objects.filter(
#                 author=self.author,
#                 id=self.post.id,
#                 group=self.group.id,
#                 text='Измененный  пост',
#                 image='posts/big.gif',
#             ).exists()
#         )
