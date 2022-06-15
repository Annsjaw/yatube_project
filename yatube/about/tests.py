from django.test import TestCase, Client


class AboutPagesURLTest(TestCase):
    def setUp(self):
        """Создаем неавторизованного пользователя"""
        self.guest_client = Client()
        self.url = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def test_about_url_status_code(self):
        """Проверка доступности адресов статичный страниц"""
        for path in self.url.keys():
            with self.subTest(path=path):
                response = self.guest_client.get(path)
                self.assertEqual(response.status_code, 200, f'Статус код страницы {path} не равен 200')

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для адресов статичных страниц"""
        for path, template in self.url.items():
            with self.subTest(path=path):
                response = self.guest_client.get(path)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Шаблон страницы {path} не соответствует шаблону {template}'
                )