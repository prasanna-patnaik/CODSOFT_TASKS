from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
from datetime import date

from .models import Student
from .serializers import StudentSerializer


def create_student(**kwargs):
    defaults = {
        'student_id': 'STU-001',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'date_of_birth': date(2000, 1, 15),
        'enrollment_date': date(2024, 9, 1),
    }
    defaults.update(kwargs)
    return Student.objects.create(**defaults)


def create_user(username='testuser', password='TestPass123!'):
    user = User.objects.create_user(username=username, password=password)
    Token.objects.create(user=user)
    return user


class StudentModelTest(TestCase):

    def test_create_student(self):
        student = create_student()
        self.assertEqual(Student.objects.count(), 1)
        self.assertEqual(student.student_id, 'STU-001')

    def test_str_representation(self):
        student = create_student()
        self.assertEqual(str(student), 'John Doe (STU-001)')

    def test_full_name_property(self):
        student = create_student()
        self.assertEqual(student.full_name, 'John Doe')

    def test_is_active_default_true(self):
        student = create_student()
        self.assertTrue(student.is_active)

    def test_unique_student_id(self):
        create_student(student_id='STU-001')
        with self.assertRaises(IntegrityError):
            create_student(student_id='STU-001', email='other@example.com')

    def test_unique_email(self):
        create_student(email='john@example.com')
        with self.assertRaises(IntegrityError):
            create_student(student_id='STU-002', email='john@example.com')

    def test_blank_optional_fields(self):
        student = create_student()
        self.assertEqual(student.phone, '')
        self.assertEqual(student.address, '')

    def test_ordering(self):
        create_student(student_id='STU-001', email='a@example.com')
        create_student(student_id='STU-002', email='b@example.com')
        students = list(Student.objects.values_list('student_id', flat=True))
        self.assertEqual(students, ['STU-002', 'STU-001'])


class StudentSerializerTest(TestCase):

    def test_serialization(self):
        student = create_student()
        serializer = StudentSerializer(student)
        data = serializer.data
        self.assertEqual(data['student_id'], 'STU-001')
        self.assertEqual(data['full_name'], 'John Doe')
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_deserialization_valid(self):
        payload = {
            'student_id': 'STU-100',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'date_of_birth': '1999-05-20',
            'enrollment_date': '2024-09-01',
        }
        serializer = StudentSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_duplicate_student_id_validation(self):
        create_student(student_id='STU-001')
        serializer = StudentSerializer(data={
            'student_id': 'STU-001',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'date_of_birth': '1999-05-20',
            'enrollment_date': '2024-09-01',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('student_id', serializer.errors)

    def test_duplicate_email_validation(self):
        create_student(email='john@example.com')
        serializer = StudentSerializer(data={
            'student_id': 'STU-002',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'john@example.com',
            'date_of_birth': '1999-05-20',
            'enrollment_date': '2024-09-01',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_update_same_instance_no_conflict(self):
        student = create_student(student_id='STU-001', email='john@example.com')
        serializer = StudentSerializer(
            student,
            data={'student_id': 'STU-001', 'email': 'john@example.com'},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_read_only_fields(self):
        student = create_student()
        serializer = StudentSerializer(student)
        self.assertIn('id', serializer.data)
        self.assertIn('created_at', serializer.data)
        self.assertIn('updated_at', serializer.data)
        self.assertTrue(StudentSerializer().fields['id'].read_only)
        self.assertTrue(StudentSerializer().fields['created_at'].read_only)
        self.assertTrue(StudentSerializer().fields['updated_at'].read_only)


class HomeAPITest(APITestCase):

    def test_home_endpoint(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Welcome to Student Record Management API')
        self.assertIn('endpoints', response.data)


class AuthRegisterTest(APITestCase):

    def test_register_success(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        create_user(username='existing')
        response = self.client.post('/api/auth/register/', {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': '123',
            'password_confirm': '123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthLoginTest(APITestCase):

    def setUp(self):
        self.user = create_user(username='logintest', password='LoginPass123!')

    def test_login_success(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'logintest',
            'password': 'LoginPass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'logintest')

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'logintest',
            'password': 'WrongPassword!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'nobody',
            'password': 'Whatever123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthLogoutTest(APITestCase):

    def setUp(self):
        self.user = create_user()
        self.token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_logout_success(self):
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_logout_unauthenticated(self):
        self.client.credentials()
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthProfileTest(APITestCase):

    def setUp(self):
        self.user = create_user()
        self.token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_get_profile(self):
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_profile(self):
        response = self.client.patch('/api/auth/profile/', {
            'first_name': 'Updated',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_profile_unauthenticated(self):
        self.client.credentials()
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthChangePasswordTest(APITestCase):

    def setUp(self):
        self.user = create_user(password='OldPass123!')
        self.token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_change_password_success(self):
        response = self.client.post('/api/auth/change-password/', {
            'old_password': 'OldPass123!',
            'new_password': 'NewSecure456!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecure456!'))

    def test_change_password_wrong_old(self):
        response = self.client.post('/api/auth/change-password/', {
            'old_password': 'WrongOld!',
            'new_password': 'NewSecure456!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_weak_new(self):
        response = self.client.post('/api/auth/change-password/', {
            'old_password': 'OldPass123!',
            'new_password': '123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StudentAPIAuthTest(APITestCase):

    def setUp(self):
        self.user = create_user()
        self.token = Token.objects.get(user=self.user)
        self.student_data = {
            'student_id': 'STU-001',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'date_of_birth': '2000-01-15',
            'enrollment_date': '2024-09-01',
        }

    def test_unauthenticated_read_allowed(self):
        create_student()
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_create_denied(self):
        response = self.client.post('/api/students/', self.student_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_update_denied(self):
        student = create_student()
        response = self.client.put(f'/api/students/{student.id}/', self.student_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_delete_denied(self):
        student = create_student()
        response = self.client.delete(f'/api/students/{student.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_create_allowed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/api/students/', self.student_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authenticated_update_allowed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        student = create_student()
        updated_data = {**self.student_data, 'first_name': 'Jonathan'}
        response = self.client.put(f'/api/students/{student.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_delete_allowed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        student = create_student()
        response = self.client.delete(f'/api/students/{student.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_based_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/api/students/', self.student_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class StudentAPICrudTest(APITestCase):

    def setUp(self):
        self.user = create_user()
        self.token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.student_data = {
            'student_id': 'STU-001',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'date_of_birth': '2000-01-15',
            'enrollment_date': '2024-09-01',
        }

    def test_create_student(self):
        response = self.client.post('/api/students/', self.student_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student_id'], 'STU-001')
        self.assertEqual(response.data['full_name'], 'John Doe')
        self.assertTrue(response.data['is_active'])

    def test_list_students(self):
        create_student()
        create_student(student_id='STU-002', email='jane@example.com', first_name='Jane')
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_student(self):
        student = create_student()
        response = self.client.get(f'/api/students/{student.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], 'STU-001')

    def test_retrieve_nonexistent(self):
        response = self.client.get('/api/students/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_student(self):
        student = create_student()
        updated_data = {**self.student_data, 'first_name': 'Jonathan'}
        response = self.client.put(f'/api/students/{student.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        student.refresh_from_db()
        self.assertEqual(student.first_name, 'Jonathan')

    def test_partial_update_student(self):
        student = create_student()
        response = self.client.patch(f'/api/students/{student.id}/', {'last_name': 'Smith'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        student.refresh_from_db()
        self.assertEqual(student.last_name, 'Smith')

    def test_soft_delete_student(self):
        student = create_student()
        response = self.client.delete(f'/api/students/{student.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        student.refresh_from_db()
        self.assertFalse(student.is_active)
        self.assertEqual(Student.objects.count(), 1)

    def test_create_invalid_data(self):
        response = self.client.post('/api/students/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_student_id(self):
        create_student(student_id='STU-001')
        data = {**self.student_data, 'email': 'other@example.com'}
        response = self.client.post('/api/students/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StudentAPIFilterTest(APITestCase):

    def setUp(self):
        self.user = create_user()
        self.token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        create_student(student_id='STU-001', email='a@example.com', first_name='Alice', is_active=True)
        create_student(student_id='STU-002', email='b@example.com', first_name='Bob', is_active=False)
        create_student(student_id='STU-003', email='c@example.com', first_name='Charlie', is_active=True)

    def test_filter_by_is_active(self):
        response = self.client.get('/api/students/?is_active=true')
        self.assertEqual(response.data['count'], 2)
        response = self.client.get('/api/students/?is_active=false')
        self.assertEqual(response.data['count'], 1)

    def test_search_by_name(self):
        response = self.client.get('/api/students/?search=Ali')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Alice')

    def test_search_by_email(self):
        response = self.client.get('/api/students/?search=b@example.com')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['email'], 'b@example.com')

    def test_search_by_student_id(self):
        response = self.client.get('/api/students/?search=STU-003')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['student_id'], 'STU-003')

    def test_ordering_by_last_name(self):
        response = self.client.get('/api/students/?ordering=last_name')
        names = [s['first_name'] for s in response.data['results']]
        self.assertEqual(names, ['Alice', 'Bob', 'Charlie'])

    def test_ordering_by_created_at_desc(self):
        response = self.client.get('/api/students/?ordering=-created_at')
        ids = [s['id'] for s in response.data['results']]
        self.assertEqual(ids, sorted(ids, reverse=True))


class StudentAPIPaginationTest(APITestCase):

    def setUp(self):
        self.user = create_user()
        self.token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_pagination(self):
        for i in range(25):
            create_student(student_id=f'STU-{i:03d}', email=f's{i}@example.com')
        response = self.client.get('/api/students/')
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(len(response.data['results']), 20)
        self.assertIsNotNone(response.data['next'])

    def test_pagination_page_two(self):
        for i in range(25):
            create_student(student_id=f'STU-{i:03d}', email=f's{i}@example.com')
        response = self.client.get('/api/students/?page=2')
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNone(response.data['next'])
