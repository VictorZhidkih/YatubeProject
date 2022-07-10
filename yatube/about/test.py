from django.test import Client, TestCase


class AboutTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/"""
        about_list = ['/about/tech/', '/about/author/']
        for i in about_list:
            with self.subTest(field=i):
                response = AboutTest.guest_client.get(i)
                self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/"""
        about_list = {
            'about/tech.html': '/about/tech/',
            'about/author.html': '/about/author/',
        }
        for template, address in about_list.items():
            with self.subTest(field=address):
                response = AboutTest.guest_client.get(address)
                self.assertTemplateUsed(response, template)
