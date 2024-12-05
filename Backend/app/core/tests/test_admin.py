# """
# Tests for the Django admin modifications.
# """
# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from django.urls import reverse
# from django.test import Client


# class AdminSiteTests(TestCase):
#     """Tests for Django admin."""

#     def setUp(self):
#         """Create user and client."""
#         self.client = Client()
#         self.admin_user = get_user_model().objects.create_superuser(
#             email='admin@example.com',
#             password='testpass123',
#         )
#         self.client.force_login(self.admin_user)
#         self.user = get_user_model().objects.create_user(
#             email='user@example.com',
#             password='testpass123',
#             name='Test User'
#         )

#     def test_user_list(self):
#         """Test that users are listed on page."""
#         # Generate the URL for the changelist page of the 'core_user' model in the Django admin  # noqa
#         url = reverse('admin:core_user_changelist')
#         res = self.client.get(url)

#         # Assert that response contains name and email since that is what
#         # we're testing: a list of fileds in the admin site.
#         self.assertContains(res, self.user.name)
#         self.assertContains(res, self.user.email)

#     def test_edit_user_page(self):
#         """Test the edit user page works."""
#         # Generate the URL for the 'change' page of the specific 'core_user' instance in the Django admin, using the user's ID  # noqa
#         # i.e: retrieves user/1/change, it means retrieve user 1.  # noqa
#         url = reverse('admin:core_user_change', args=[self.user.id])
#         res = self.client.get(url)

#         self.assertEqual(res.status_code, 200)

#     def test_create_user_page(self):
#         """Test the create user page works."""
#         url = reverse('admin:core_user_add')
#         res = self.client.get(url)

#         self.assertEqual(res.status_code, 200)