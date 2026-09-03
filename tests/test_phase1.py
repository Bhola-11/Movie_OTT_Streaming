import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import UserProfile, UserDevice, LoginHistory, SecurityLog
from genres.models import Genre, Category, Mood, Tag
from people.models import Person, Profession, PersonAward

User = get_user_model()

@pytest.mark.django_db
def test_create_user_and_profile_signal():
    user = User.objects.create_user(
        email='streamer@cineverse.io',
        password='TestPassword123!',
        first_name='Alex',
        last_name='Rivers'
    )
    assert user.email == 'streamer@cineverse.io'
    assert user.check_password('TestPassword123!')
    assert user.role == User.RoleChoices.VIEWER
    # Test signal created profile
    assert hasattr(user, 'profile')
    assert user.profile.preferred_quality == UserProfile.QualityChoices.AUTO

@pytest.mark.django_db
def test_create_superuser():
    admin_user = User.objects.create_superuser(
        email='admin@cineverse.io',
        password='SuperAdminPass123!'
    )
    assert admin_user.is_staff is True
    assert admin_user.is_superuser is True
    assert admin_user.role == User.RoleChoices.ADMIN
    assert admin_user.is_admin is True

@pytest.mark.django_db
def test_device_registration_and_security():
    user = User.objects.create_user(email='device.test@cineverse.io', password='PassWord123!')
    device = UserDevice.objects.create(
        user=user,
        device_id='device-abc-123',
        device_name='Living Room Smart TV',
        device_type='SmartTV',
        ip_address='192.168.1.100'
    )
    assert user.devices.count() == 1
    assert device.device_name == 'Living Room Smart TV'

    SecurityLog.objects.create(
        user=user,
        event_type='PASSWORD_CHANGED',
        description='Test security log event',
        ip_address='192.168.1.100'
    )
    assert user.security_logs.count() == 1

@pytest.mark.django_db
def test_genres_and_taxonomies():
    genre = Genre.objects.create(name='Sci-Fi & Cyberpunk', description='Futuristic technology and neon dystopias')
    assert genre.slug == 'sci-fi-cyberpunk'
    assert str(genre) == 'Sci-Fi & Cyberpunk'

    cat = Category.objects.create(name='Original Series', category_type=Category.CategoryType.SERIES)
    assert cat.slug == 'original-series'

    mood = Mood.objects.create(name='Adrenaline Rush', color_gradient='from-red-900 to-orange-900')
    assert mood.slug == 'adrenaline-rush'

    tag = Tag.objects.create(name='Oscar Winner')
    assert tag.slug == 'oscar-winner'

@pytest.mark.django_db
def test_people_and_awards():
    prof = Profession.objects.create(name='Director')
    person = Person.objects.create(
        full_name='Christopher Nolan',
        primary_profession=prof,
        biography='Renowned filmmaker recognized for non-linear storytelling.'
    )
    assert person.slug == 'christopher-nolan'

    award = PersonAward.objects.create(
        person=person,
        award_name='Academy Award',
        year=2024,
        category='Best Director',
        work_title='Oppenheimer',
        is_winner=True
    )
    assert 'Won' in str(award)

@pytest.mark.django_db
def test_auth_views_and_status(client):
    # Registration page
    reg_url = reverse('accounts:register')
    res_reg = client.get(reg_url)
    assert res_reg.status_code == 200
    assert 'Start Streaming' in res_reg.content.decode()

    # Login page
    login_url = reverse('accounts:login')
    res_login = client.get(login_url)
    assert res_login.status_code == 200

    # User registration submit
    client.post(reg_url, {
        'email': 'newviewer@cineverse.io',
        'first_name': 'Sarah',
        'last_name': 'Connor',
        'password': 'StrongPassword99!',
        'password_confirm': 'StrongPassword99!',
        'terms_accepted': True
    })
    user_created = User.objects.filter(email='newviewer@cineverse.io').exists()
    assert user_created is True

@pytest.mark.django_db
def test_genre_and_people_views(client):
    Genre.objects.create(name='Action Thriller', description='High stakes')
    Person.objects.create(full_name='Keanu Reeves')

    res_genres = client.get(reverse('genres:list'))
    assert res_genres.status_code == 200
    assert 'Action Thriller' in res_genres.content.decode()

    res_people = client.get(reverse('people:list'))
    assert res_people.status_code == 200
    assert 'Keanu Reeves' in res_people.content.decode()
