import shutil
import tempfile

from django import forms as django_forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User, Group, Post"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized_user')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание группы',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-group-2-slug',
            description='Тестовое описание второй группы',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.post = []
        for x in range(15):  # FIXME разобраться и прикрутить bulk_create
            new_post = Post.objects.create(text=f'Тестовый текст поста {x}',
                                           author=cls.user,
                                           group=cls.group,
                                           image=cls.uploaded,
                                           )
            cls.post.insert(0, new_post)
        cls.form_fields = {
            'text': django_forms.fields.CharField,
            'group': django_forms.fields.ChoiceField,
            'image': django_forms.fields.ImageField,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_page_uses_correct_template_for_auth_user(self):
        """URL-адрес использует правильный шаблон для авторизованного юзера"""
        auth_templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': self.post[0].id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': self.post[0].id}): 'posts/post_create.html',
        }
        for reverse_name, template in auth_templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Шаблон {template} не соответствует {reverse_name}')

    def test_page_uses_correct_template_for_guest(self):
        """URL-адрес использует правильный шаблон для гостя"""
        guest_templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': self.post[0].id}): 'posts/post_detail.html',
        }
        for reverse_name, template in guest_templates_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Шаблон {template} не соответствует {reverse_name}')

    def test_post_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_id_0 = first_object.id
        post_text_0 = first_object.text
        post_user_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post[0].text)
        self.assertEqual(post_user_0, self.post[0].author)
        self.assertEqual(post_group_0, self.post[0].group)
        self.assertEqual(post_image_0, self.post[0].image)
        self.assertEqual(
            post_id_0,
            self.post[0].id,
            'id поста переданного в context не соответствует ожидаемому')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        post_id_0 = first_object.id
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(
            post_id_0,
            self.post[0].id,
            'id поста переданного в context не соответствует ожидаемому'
        )
        self.assertEqual(post_text_0, self.post[0].text)
        self.assertEqual(post_group_0, self.group.title)
        self.assertEqual(post_image_0, self.post[0].image)
        self.assertNotEqual(post_group_0,
                            self.group_2.title,
                            'Созданный пост находится не в указанной группе'
                            )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post[0].text)
        self.assertEqual(post_author_0, self.post[0].author)
        self.assertEqual(post_image_0, self.post[0].image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post[0].id})
        )
        self.assertEqual(response.context['post'].id, self.post[0].id)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post[0].id})
        )
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        """После удаления поста он остается до очистки кеша"""
        response1 = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(text='qwerty', author=self.user)
        response2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response3.content, response2.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User, Group, Post"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized_user')
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание группы',
        )
        cls.post = []
        for x in range(15):
            new_post = Post.objects.create(text=f'Тестовый текст поста {x}',
                                           author=cls.user,
                                           group=cls.group,
                                           )
            cls.post.insert(0, new_post)
        cls.templates_page_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user}),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_paginator_first_page(self):
        """Количество постов на первой странице равно 10"""
        for page_name in self.templates_page_names:
            response = self.client.get(page_name)
            self.assertEqual(
                len(response.context['page_obj'].object_list),
                10,
                f'Paginator вывел не 10 постов на первой странице {page_name}'
            )

    def test_paginator_second_page(self):
        """Количество постов на второй странице равно 5"""
        for page_name in self.templates_page_names:
            response = self.client.get(page_name + '?page=2')
            self.assertEqual(
                len(response.context['page_obj'].object_list),
                5,
            )


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='auth_user_1')
        cls.user_2 = User.objects.create_user(username='auth_user_2')
        cls.user_3 = User.objects.create_user(username='auth_user_3')
        cls.guest_client = Client()
        cls.user_2_client = Client()
        cls.user_2_client.force_login(cls.user_2)
        cls.user_1_client = Client()
        cls.user_1_client.force_login(cls.user_1)
        cls.post = []
        for x in range(3):
            new_post = Post.objects.create(text=f'Тестовый текст поста {x}',
                                           author=cls.user_1,
                                           )
            cls.post.insert(0, new_post)
        Follow.objects.create(user=cls.user_2, author=cls.user_3)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_auth_user_2_following_user_1(self):
        """Юзер 2 подписался на юзера 1"""
        followers_count = Follow.objects.count()
        self.user_2_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user_1}),
            follow=True
        )
        self.assertEqual(Follow.objects.count(), followers_count + 1)

    def test_auth_user_3_unfollowing_user_1(self):
        """Юзер 1 отписался от юзера 3"""
        followers_count = Follow.objects.count()
        self.user_2_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_3}
                    ),
            follow=True
        )
        self.assertEqual(Follow.objects.count(), followers_count - 1)

    def test_guest_user_following_user_1(self):
        """Гость подписался на юзера 1"""
        followers_count = Follow.objects.count()
        self.guest_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user_1}),
            follow=True
        )
        self.assertEqual(Follow.objects.count(), followers_count)

    def test_guest_user_unfollowing_user_1(self):
        """Гость отписался от юзера 1"""
        followers_count = Follow.objects.count()
        self.guest_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_1}
                    ),
            follow=True
        )
        self.assertEqual(Follow.objects.count(), followers_count)

    def test_folowers_see_new_post(self):
        """Подписчик видит новый пост избранного автора,
         а другой пользователь нет"""
        resp_u2_before = self.user_2_client.get(reverse('posts:follow_index'))
        obj_user_2_before = resp_u2_before.context['page_obj']
        post_count_user_2_before = obj_user_2_before.paginator.count
        resp_u1_before = self.user_1_client.get(reverse('posts:follow_index'))
        obj_user_1_before = resp_u1_before.context['page_obj']
        post_count_user_1_before = obj_user_1_before.paginator.count
        Post.objects.create(text='Текст поста Usera 3',
                            author=self.user_3,
                            )
        resp_u2_after = self.user_2_client.get(reverse('posts:follow_index'))
        obj_user_2_after = resp_u2_after.context['page_obj']
        post_count_user_2_after = obj_user_2_after.paginator.count
        resp_u1_after = self.user_1_client.get(reverse('posts:follow_index'))
        obj_user_1_after = resp_u1_after.context['page_obj']
        post_count_user_1_after = obj_user_1_after.paginator.count

        self.assertEqual(
            post_count_user_2_after,
            post_count_user_2_before + 1,
            'Пост не добавился у подписчика')
        self.assertEqual(
            post_count_user_1_after,
            post_count_user_1_before,
            'Посты не должны добавляться если не подписан на автора')


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.creator = User.objects.create_user(username='creator')
        cls.commentator = User.objects.create_user(username='commentator')
        cls.guest_client = Client()
        cls.commentator_client = Client()
        cls.commentator_client.force_login(cls.commentator)
        cls.post = Post.objects.create(text='Тестовый текст поста',
                                       author=cls.creator
                                       )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_comment_appears_on_page(self):
        """Комментарий появился на странице поста post_detail"""
        Comment.objects.create(post_id=self.post.id,
                               author=self.commentator,
                               text='Тестовый коммент'
                               )
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        comments = {
            response.context['comments'][0].text: 'Тестовый коммент',
            response.context['comments'][0].author: self.commentator,
        }
        for value, expected in comments.items():
            self.assertEqual(value, expected)
        self.assertTrue(response.context['form'], 'форма не отображается')
