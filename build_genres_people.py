import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created: {filepath}")

# ==============================================================================
# GENRES APP
# ==============================================================================

write('genres/apps.py', '''from django.apps import AppConfig

class GenresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'genres'
    verbose_name = 'Content Genres & Taxonomies'
''')

write('genres/models.py', '''from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Genre(models.Model):
    """
    Primary cinematic genres (Action, Sci-Fi, Thriller, Romance, Drama, Animation, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Editorial synopsis of the genre.")
    icon_svg = models.TextField(blank=True, help_text="Inline SVG path or icon name")
    backdrop_image = models.ImageField(upload_to='genres/backdrops/', null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    meta_keywords = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('genres:detail', kwargs={'slug': self.slug})


class Category(models.Model):
    """
    Broad streaming classifications (Feature Films, Web Series, Documentaries, Anime, Stand-up Specials).
    """
    class CategoryType(models.TextChoices):
        MOVIE = 'MOVIE', 'Movie'
        SERIES = 'SERIES', 'TV Series'
        DOCUMENTARY = 'DOCUMENTARY', 'Documentary'
        ANIME = 'ANIME', 'Anime'
        STANDUP = 'STANDUP', 'Stand-Up Comedy'
        SHORT = 'SHORT', 'Short Film'

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    category_type = models.CharField(max_length=20, choices=CategoryType.choices, default=CategoryType.MOVIE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('genres:category_detail', kwargs={'slug': self.slug})


class Mood(models.Model):
    """
    Experiential filters for discovery (Adrenaline Rush, Mind-Bending, Heartwarming, Spine-Chilling).
    """
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    color_gradient = models.CharField(max_length=100, default='from-purple-900 to-indigo-900', help_text="CSS gradient identifiers")
    icon = models.CharField(max_length=50, default='sparkles')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """
    Fine-grained thematic keywords (Time Travel, Cyberpunk, Based on True Story, Oscar Winner).
    """
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    is_trending = models.BooleanField(default=False)

    def __str__(self):
        return f"#{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
''')

write('genres/forms.py', '''from django import forms
from .models import Genre, Category, Mood, Tag

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'slug', 'description', 'backdrop_image', 'is_featured', 'display_order', 'meta_keywords']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-input'}),
        }

class MoodForm(forms.ModelForm):
    class Meta:
        model = Mood
        fields = ['name', 'slug', 'description', 'color_gradient', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.TextInput(attrs={'class': 'form-input'}),
        }
''')

write('genres/services.py', '''from .models import Genre, Category, Mood, Tag

class GenreService:
    @staticmethod
    def get_featured_genres():
        return Genre.objects.filter(is_featured=True).order_by('display_order')

    @staticmethod
    def get_active_categories():
        return Category.objects.filter(is_active=True).order_by('order')

    @staticmethod
    def get_all_moods():
        return Mood.objects.all().order_by('name')
''')

write('genres/templatetags/__init__.py', '')
write('genres/templatetags/genre_tags.py', '''from django import template
from genres.models import Genre, Mood

register = template.Library()

@register.inclusion_tag('genres/components/genre_pills.html')
def render_genre_pills(active_genre=None):
    return {
        'genres': Genre.objects.all()[:12],
        'active_genre': active_genre
    }

@register.inclusion_tag('genres/components/mood_chips.html')
def render_mood_chips():
    return {
        'moods': Mood.objects.all()[:8]
    }
''')

write('genres/views.py', '''from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Genre, Category, Mood, Tag

class GenreListView(ListView):
    model = Genre
    template_name = 'genres/genre_list.html'
    context_object_name = 'genres'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.filter(is_active=True)
        ctx['moods'] = Mood.objects.all()
        return ctx

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'genres/genre_detail.html'
    context_object_name = 'genre'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        genre = self.get_object()
        # Movies and Series associated with this genre
        ctx['movies'] = genre.movies.filter(is_published=True)[:24] if hasattr(genre, 'movies') else []
        ctx['series_list'] = genre.series.filter(is_published=True)[:24] if hasattr(genre, 'series') else []
        return ctx

class CategoryListView(ListView):
    model = Category
    template_name = 'genres/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'genres/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'

class MoodExploreView(ListView):
    model = Mood
    template_name = 'genres/mood_explore.html'
    context_object_name = 'moods'
''')

write('genres/urls.py', '''from django.urls import path
from . import views

app_name = 'genres'

urlpatterns = [
    path('', views.GenreListView.as_view(), name='list'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('moods/', views.MoodExploreView.as_view(), name='moods'),
    path('<slug:slug>/', views.GenreDetailView.as_view(), name='detail'),
]
''')

write('genres/admin.py', '''from django.contrib import admin
from .models import Genre, Category, Mood, Tag

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_featured', 'display_order', 'created_at')
    list_editable = ('is_featured', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category_type', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_gradient', 'icon')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_trending')
    list_editable = ('is_trending',)
    prepopulated_fields = {'slug': ('name',)}
''')

# ==============================================================================
# PEOPLE APP
# ==============================================================================

write('people/apps.py', '''from django.apps import AppConfig

class PeopleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'people'
    verbose_name = 'Cast, Crew & Creators'
''')

write('people/models.py', '''from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Profession(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Person(models.Model):
    """
    Cinematic personality (Actor, Director, Screenwriter, Composer, Producer).
    """
    class GenderChoices(models.TextChoices):
        FEMALE = 'F', 'Female'
        MALE = 'M', 'Male'
        NON_BINARY = 'NB', 'Non-Binary'
        OTHER = 'O', 'Other / Prefer not to say'

    full_name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    stage_name = models.CharField(max_length=150, blank=True)
    biography = models.TextField(blank=True)
    photo = models.ImageField(upload_to='people/photos/%Y/', null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=150, blank=True)
    gender = models.CharField(max_length=5, choices=GenderChoices.choices, default=GenderChoices.OTHER)
    primary_profession = models.ForeignKey(Profession, on_delete=models.SET_NULL, null=True, blank=True, related_name='practitioners')
    
    imdb_id = models.CharField(max_length=30, blank=True)
    tmdb_id = models.CharField(max_length=30, blank=True)
    instagram_handle = models.CharField(max_length=80, blank=True)
    twitter_handle = models.CharField(max_length=80, blank=True)

    is_featured = models.BooleanField(default=False)
    popularity_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-popularity_score', 'full_name']
        verbose_name_plural = 'People'

    def __str__(self):
        return self.stage_name if self.stage_name else self.full_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.full_name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('people:detail', kwargs={'slug': self.slug})


class PersonAward(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='awards')
    award_name = models.CharField(max_length=150)
    year = models.PositiveSmallIntegerField()
    category = models.CharField(max_length=150)
    work_title = models.CharField(max_length=200, blank=True)
    is_winner = models.BooleanField(default=True)

    class Meta:
        ordering = ['-year', 'award_name']

    def __str__(self):
        status = "Won" if self.is_winner else "Nominated"
        return f"{self.person} - {self.award_name} ({self.year}) [{status}]"
''')

write('people/forms.py', '''from django import forms
from .models import Person, PersonAward

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            'full_name', 'stage_name', 'slug', 'primary_profession', 'biography',
            'birth_date', 'place_of_birth', 'gender', 'photo', 'imdb_id',
            'instagram_handle', 'twitter_handle', 'is_featured', 'popularity_score'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'stage_name': forms.TextInput(attrs={'class': 'form-input'}),
            'biography': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
            'birth_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'place_of_birth': forms.TextInput(attrs={'class': 'form-input'}),
        }
''')

write('people/services.py', '''from .models import Person

class PeopleService:
    @staticmethod
    def get_trending_actors():
        return Person.objects.filter(primary_profession__slug='actor').order_by('-popularity_score')[:12]

    @staticmethod
    def get_acclaimed_directors():
        return Person.objects.filter(primary_profession__slug='director').order_by('-popularity_score')[:12]
''')

write('people/templatetags/__init__.py', '')
write('people/templatetags/people_tags.py', '''from django import template

register = template.Library()

@register.filter(name='person_avatar')
def person_avatar(person):
    if person and person.photo:
        return person.photo.url
    return f"https://api.dicebear.com/7.x/initials/svg?seed={getattr(person, 'full_name', 'Star')}&backgroundColor=1f2330"
''')

write('people/views.py', '''from django.views.generic import ListView, DetailView
from .models import Person, Profession

class PersonListView(ListView):
    model = Person
    template_name = 'people/person_list.html'
    context_object_name = 'people'
    paginate_by = 24

    def get_queryset(self):
        qs = Person.objects.select_related('primary_profession').all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(full_name__icontains=q)
        profession = self.request.GET.get('profession')
        if profession:
            qs = qs.filter(primary_profession__slug=profession)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['professions'] = Profession.objects.all()
        ctx['selected_profession'] = self.request.GET.get('profession', '')
        return ctx

class PersonDetailView(DetailView):
    model = Person
    template_name = 'people/person_detail.html'
    context_object_name = 'person'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        person = self.get_object()
        ctx['awards'] = person.awards.all()
        # Related movies directed or acted
        ctx['directed_movies'] = person.directed_movies.all() if hasattr(person, 'directed_movies') else []
        ctx['acted_movies'] = person.acted_movies.all() if hasattr(person, 'acted_movies') else []
        return ctx

class DirectorDirectoryView(ListView):
    model = Person
    template_name = 'people/directors.html'
    context_object_name = 'directors'

    def get_queryset(self):
        return Person.objects.filter(primary_profession__slug='director').order_by('-popularity_score')
''')

write('people/urls.py', '''from django.urls import path
from . import views

app_name = 'people'

urlpatterns = [
    path('', views.PersonListView.as_view(), name='list'),
    path('directors/', views.DirectorDirectoryView.as_view(), name='directors'),
    path('<slug:slug>/', views.PersonDetailView.as_view(), name='detail'),
]
''')

write('people/admin.py', '''from django.contrib import admin
from .models import Person, Profession, PersonAward

class PersonAwardInline(admin.TabularInline):
    model = PersonAward
    extra = 1

@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'stage_name', 'primary_profession', 'popularity_score', 'is_featured')
    list_filter = ('primary_profession', 'is_featured', 'gender')
    search_fields = ('full_name', 'stage_name', 'biography')
    prepopulated_fields = {'slug': ('full_name',)}
    inlines = [PersonAwardInline]

@admin.register(PersonAward)
class PersonAwardAdmin(admin.ModelAdmin):
    list_display = ('person', 'award_name', 'year', 'is_winner')
    list_filter = ('is_winner', 'year')
    search_fields = ('person__full_name', 'award_name', 'work_title')
''')

print("genres and people apps built successfully.")
