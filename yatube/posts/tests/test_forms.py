import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User, Group"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized_user_Oleg')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа Практикума',
            slug='test-practicum-group-slug',
            description='Тестовое описание группы Практикума',
        )
        cls.post = Post.objects.create(text='Тестовый текст поста',
                                       author=cls.user,
                                       group=cls.group,
                                       )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_auth_user(self):
        """Создаем тестовый пост авторизованным пользователем, проверяем
        редирект и статус страницы"""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый текст поста принадлежащий группе Практикум',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_create_post_guest_user(self):
        """Проверяем доступность и редирект незарегистрированным юзером """
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст поста'}
        response_post = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        response_get = self.guest_client.get(reverse('posts:post_create'))
        self.assertNotEqual(
            response_get.status_code,
            HTTPStatus.OK,
            'Статус код get запроса не должен равняться 200'
        )
        self.assertRedirects(
            response_get,
            '/auth/login/?next=/create/',
        )
        self.assertEqual(response_post.status_code, HTTPStatus.OK)
        self.assertRedirects(response_post, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post_auth_user(self):
        """Редактируем созданный пост проверяем редирект и статус страницы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст поста '
                    '(эта часть добавлена после редактирования)',
        }
        response_post = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        response_get = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post = response_get.context['post']
        self.assertEqual(response_post.status_code, HTTPStatus.OK)
        self.assertEqual(
            post.text,
            form_data['text'],
            'Проверьте что изменения в посте сохранены'
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'Количество постов не соответствует ожидаемому'
        )
        self.assertRedirects(
            response_post,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

    def test_edit_post_guest_user(self):
        """Проверяем доступность и редирект незарегистрированным юзером """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст поста '
                    '(эта часть добавлена после редактирования)',
        }
        response_post = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        response_get = self.guest_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(response_post.status_code, HTTPStatus.OK)
        self.assertNotEqual(
            self.post.text,
            form_data['text'],
            'Проверьте что изменений в посте нет'
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'Количество постов не соответствует ожидаемому'
        )
        self.assertNotEqual(response_get.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response_get, '/auth/login/?next=%2Fposts%2F1%2Fedit%2F'
        )


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized_user')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(text='Тестовый текст поста',
                                       author=cls.user,
                                       )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_add_comment_auth_user(self):
        """Авторизованный пользователь может комментировать и
        редирект работает исправно"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
            HTTPStatus.FOUND,
        )

    def test_add_comment_guest_user(self):
        """Авторизованный пользователь не может комментировать"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий'
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
