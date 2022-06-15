# X - Проверить статус страницы posts/<str:post_id>/edit/
# X - Создать тесты на проверку template
# X - Сделать рефакторинг для тестов на 200

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User, Group, Post"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)  # Авторизация через созданного юзера
        # Тестовый словарь для всех видов тестов
        cls.url = {
            'guest_client': {'/': 'posts/index.html',
                             '/group/test-group-slug/': 'posts/group_list.html',
                             '/profile/authorized_user/': 'posts/profile.html',
                             f'/posts/{PostsURLTests.post.id}/': 'posts/post_detail.html',
                             },
            'authorized_client': {'/create/': 'posts/post_create.html',
                                  f'/posts/{PostsURLTests.post.id}/edit/': 'posts/post_create.html',
                                  },
        }

    def test_guest_url_code_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404, 'Статус несуществующей страницы не равен 404')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for templates_url_names in self.url.values():
            for path, template in templates_url_names.items():
                with self.subTest(path=path):
                    response = self.authorized_client.get(path)
                    self.assertTemplateUsed(
                        response,
                        template,
                        f'Шаблон {template} не соответствует шаблону по адресу {path}'
                    )

    def test_urls_code_200(self):
        """Проверка адресов на 200"""
        for user, urls in self.url.items():
            for path in urls.keys():
                with self.subTest(path=path):
                    # getattr получает данные главного класса и подставляет нужный аргумент
                    response = getattr(self, user).get(path)
                    self.assertEqual(response.status_code, 200, f'Статус код страницы {path} не равен 200')
