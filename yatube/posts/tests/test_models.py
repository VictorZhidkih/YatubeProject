from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, более пятнадцати символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models_str = {PostModelTest.post: PostModelTest.post.text[:15],
                      PostModelTest.group: PostModelTest.group.title}

        for model, expected_values in models_str.items():
            with self.subTest(model=model):
                self.assertEqual(model.__str__(), expected_values,
                                 f'Ошибка метода __str__ в'
                                 f' модели {type(model).__name__}')

    def test_title_label(self):
        """verbose_name поля title совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verbose = {
            'text': 'текст',
            'pub_date': 'Дата публикации',
            'author': 'автор',
            'group': 'группа'
        }

        for field, expected_name in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_name
                )
