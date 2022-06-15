from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User, Group, Post"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
        )

    def test_verbose_name(self):
        """Verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTests.post
        field_verbose = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).verbose_name, expected, 'Ошибка в verbose_name')

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__"""
        post = PostModelTests.post
        group = PostModelTests.group
        expected_object_name = {
            self.post: post.text[:15],
            self.group: group.title,
        }
        for value, expected in expected_object_name.items():
            with self.subTest(value=value):
                self.assertEqual(expected, str(value), 'Ошибка в методе __str__')
