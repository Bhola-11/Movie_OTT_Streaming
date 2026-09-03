from django.db import models
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
