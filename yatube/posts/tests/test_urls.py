from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User, Group, Post"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized_user')
        cls.new_user = User.objects.create_user(username='new_user')
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
        cls.authorized_client.force_login(cls.user)
        cls.new_client = Client()
        cls.new_client.force_login(cls.new_user)
        cls.url = {
            'guest_client': {
                '/': 'posts/index.html',
                '/group/test-group-slug/': 'posts/group_list.html',
                '/profile/authorized_user/': 'posts/profile.html',
                f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            },
            'authorized_client': {
                '/create/': 'posts/post_create.html',
                f'/posts/{cls.post.id}/edit/': 'posts/post_create.html',
            },
        }

    def test_guest_url_code_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'Статус несуществующей страницы не равен 404'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for templates_url_names in self.url.values():
            for path, template in templates_url_names.items():
                with self.subTest(path=path):
                    response = self.authorized_client.get(path)
                    self.assertTemplateUsed(
                        response,
                        template,
                        f'Шаблон {template} не соответствует адресу {path}'
                    )

    def test_urls_code_200(self):
        """Проверка адресов на 200"""
        for user, urls in self.url.items():
            for path in urls.keys():
                with self.subTest(path=path):
                    response = getattr(self, user).get(path)
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.OK,
                        f'Статус код страницы {path} не равен 200'
                    )

    def test_urls_redirect_auth_user(self):
        """Авторизованный юзер при переходе на адресс перенаправляется"""
        urls = {
            '/profile/authorized_user/follow/': '/profile/authorized_user/',
            '/profile/authorized_user/unfollow/': '/profile/authorized_user/',
        }
        for path, redirect in urls.items():
            response = self.new_client.get(path, follow=True)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertRedirects(response, redirect)

    def test_urls_redirect_guest_user(self):
        """Не авторизованный юзер при переходе на адресс перенаправляется"""
        urls = {
            '/profile/authorized_user/follow/':
            '/auth/login/?next=%2Fprofile%2Fauthorized_user%2Ffollow%2F',
            '/profile/authorized_user/unfollow/':
            '/auth/login/?next=%2Fprofile%2Fauthorized_user%2Funfollow%2F',
        }
        for path, redirect in urls.items():
            response = self.guest_client.get(path, follow=True)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertRedirects(response, redirect)

    def test_comment_url_redirect_guest_client(self):
        response = self.guest_client.get(
            f'/posts/{self.post.id}/comment/', follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )

    def test_comment_url_redirect_auth_client(self):
        response = self.new_client.get(
            f'/posts/{self.post.id}/comment/', follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')
