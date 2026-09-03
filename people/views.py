from django.views.generic import ListView, DetailView
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
