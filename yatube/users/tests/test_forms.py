from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserTestForm(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='No')
        cls.form = User.objects.create(
            first_name='Тестовое имя',
            last_name='Тестовое фамилия',
            username='Тестовый логин',
            email='Тестовый мейл'
        )

    def setUp(self):
        self.guest_client = Client()

    def test_new_user(self):
        """Проверка на создание нового пользователя"""

        form_user = {
            'first_name': 'Тестовое имя',
            'last_name': 'Тестовое фамилия',
            'username': 'Тестовый логин',
            'email': 'Тестовый мейл'
        }
        users_count = User.objects.count()
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_user,
            follow=True
        )
        self.assertEqual(User.objects.count(), users_count)
        self.assertFormError(
            response,
            'form',
            'username',
            'Введите правильное имя пользователя.Оно может содержать только буквы, цифры и знаки @/./+/-/_'
        )
        self.assertEqual(response.status_code, 200)
