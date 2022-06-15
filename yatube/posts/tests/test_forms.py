from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post, Group

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User, Group"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized_user_Oleg')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа Практикума',
            slug='test-practicum-group-slug',
            description='Тестовое описание группы Практикума',
        )
        cls.post = Post.objects.create(text=f'Тестовый текст поста',
                                       author=cls.user,
                                       group=cls.group,
                                       )
        cls.form = PostForm()

    def test_create_post(self):
        """Создаем тестовый пост, проверяем редирект и статус страницы"""
        posts_count = Post.objects.count()
        print(f'Количество постов до создания -{posts_count}-')
        form_data = {
            'text': 'Тестовый текст поста принадлежащий группе Практикум',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        print(f'status code -{response.status_code}-')
        print(f'Количество постов после создания -{Post.objects.count()}-')
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Редактируем созданный пост проверяем редирект и статус страницы"""
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст поста (эта часть добавлена после редактирования)'}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        response_2 = self.authorized_client.get(reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post = response_2.context['post']
        print(f'Текст поста до редактирования -{self.post.text}-')
        print(f'Текст поста после редактирования -{post.text}-')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.text, form_data['text'], 'Проверьте что изменения в посте сохранены')
        self.assertEqual(Post.objects.count(), posts_count, 'Количество постов не соответствует ожидаемому')
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
