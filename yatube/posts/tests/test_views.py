from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms as django_forms

from ..models import Post, Group

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User, Group, Post"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized_user')
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
        cls.post = []
        for x in range(15):
            new_post = Post.objects.create(text=f'Тестовый текст поста {x}',
                                           author=cls.user,
                                           group=cls.group,
                                           )
            cls.post.insert(0, new_post)  # Insert добавляет в запись в начало начиная с 0
        cls.form_fields = {
            'text': django_forms.fields.CharField,
            'group': django_forms.fields.ChoiceField,
        }

    def test_page_uses_correct_template(self):
        """URL-адрес использует правильный шаблон"""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post[0].id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post[0].id}): 'posts/post_create.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template, f'Шаблон {template} не соответствует адресу {reverse_name}')

    def test_post_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        #  print(response.context['page_obj'].paginator.count)
        #  print(response.context['page_obj'].object_list)
        post_id_0 = first_object.id
        post_text_0 = first_object.text
        post_user_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post[0].text)
        self.assertEqual(post_user_0, self.post[0].author)
        self.assertEqual(post_group_0, self.post[0].group)
        self.assertEqual(post_id_0, self.post[0].id, 'id поста переданного в context не соответствует ожидаемому')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        post_id_0 = first_object.id
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_id_0, self.post[0].id, 'id поста переданного в context не соответствует ожидаемому')
        self.assertEqual(post_text_0, self.post[0].text)
        self.assertEqual(post_group_0, self.group.title)
        self.assertNotEqual(post_group_0, self.group_2.title, 'Созданный пост находится не в указанной группе')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:profile', kwargs={'username': self.user}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, self.post[0].text)
        self.assertEqual(post_author_0, self.post[0].author)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail', kwargs={'post_id': self.post[0].id}))
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
        response = self.authorized_client.get(reverse('posts:post_edit', kwargs={'post_id': self.post[0].id}))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


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
            cls.post.insert(0, new_post)  # Insert добавляет в запись в начало начиная с 0
        cls.templates_page_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user}),
        }

    def test_paginator_first_page(self):
        """Количество постов на первой странице равно 10"""
        for page_name in self.templates_page_names:
            response = self.client.get(page_name)
            self.assertEqual(len(response.context['page_obj'].object_list), 10,
                             f'Paginator вывел не 10 постов на первой странице {page_name}')

    def test_paginator_second_page(self):
        """Количество постов на второй странице равно 5"""
        for page_name in self.templates_page_names:
            response = self.client.get(page_name + '?page=2')
            self.assertEqual(len(response.context['page_obj'].object_list), 5,
                             f'Paginator вывел не 5 постов на второй странице {page_name}' + '?page=2')
