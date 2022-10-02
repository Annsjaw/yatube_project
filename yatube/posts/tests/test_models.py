from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class ModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User, Group, Post"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария написанный под постом автора, автором',
        )
        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user,
        )

    def test_post_verbose_name(self):
        """Verbose_name в полях модели Post совпадает с ожидаемым."""
        post = ModelTests.post
        field_verbose = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name,
                    expected,
                    'Ошибка в verbose_name'
                )

    def test_post_help_text(self):
        """Help text в полях модели Post совпадает с ожидаемым."""
        post = ModelTests.post
        field_help_text = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text,
                    expected,
                    'Ошибка в help_text'
                )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей Post, Group, Comment
        корректно работает __str__"""
        post = ModelTests.post
        group = ModelTests.group
        comment = ModelTests.comment
        follow = ModelTests.follow
        expected_object_name = {
            self.post: post.text[:15],
            self.group: group.title,
            self.comment: comment.text[:20],
            self.follow: f'{follow.user} - {follow.author}',
        }
        for value, expected in expected_object_name.items():
            with self.subTest(value=value):
                self.assertEqual(expected,
                                 str(value),
                                 'Ошибка в методе __str__'
                                 )

    def test_group_verbose_name(self):
        """Verbose_name в полях модели Group совпадает с ожидаемым."""
        group = ModelTests.group
        field_verbose = {
            'title': 'Название',
            'slug': 'Адрес латиницей',
            'description': 'Описание',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name,
                    expected,
                    'Ошибка в verbose_name'
                )

    def test_comment_verbose_name(self):
        """Verbose_name в полях модели Comment совпадает с ожидаемым."""
        comment = ModelTests.comment
        field_verbose = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата публикации',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name,
                    expected,
                    'Ошибка в verbose_name'
                )

    def test_follow_verbose_name(self):
        """Verbose_name в полях модели Follow совпадает с ожидаемым."""
        follow = ModelTests.follow
        field_verbose = {
            'user': 'user',
            'author': 'author',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name,
                    expected,
                    'Ошибка в verbose_name'
                )
