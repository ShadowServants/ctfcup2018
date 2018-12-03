from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, TemplateView, DetailView, ListView

from groups.libs.elastic import Collection, SearchResult
from groups.models import Document
from groups.views import BaseGroupView
from groups.tasks import render_document


class DocumentCreateView(BaseGroupView, CreateView):
    fields = ['title', 'text']
    model = Document
    template_name = 'documents/create.html'

    def form_valid(self, form):
        document = form.save(commit=False)
        group = self.get_group()
        document.owner = group
        document.save()
        elastic = Collection("documents")
        elastic.create(document.id, document.to_elastic())
        render_document.delay(document.id)
        return redirect(reverse('groups:documents_list', args=[self.group_id]))


class DocumentSearchView(BaseGroupView, TemplateView):
    template_name = "documents/search_result.html"

    def get_context_data(self, **kwargs):
        q = self.request.GET.get('q', None)
        if not q or q == '':
            return dict(docs=None, message="Empty search query")

        elastic = Collection("documents")

        res, no_error = elastic.find(f"(title:'{q}' OR text:'{q}') AND group_id:{self.group_id}",sort_by='-id')
        if not no_error:
            raise Exception("Elastic error")
        return dict(docs=(SearchResult(x) for x in res), group_id=self.group_id)


class DocumentDetailView(BaseGroupView, DetailView):
    template_name = 'documents/detail.html'
    model = Document
    pk_url_kwarg = 'id'


class DocumentListView(BaseGroupView, ListView):
    template_name = "documents/list.html"
    context_object_name = "docs"

    def get_queryset(self):
        return Document.objects.filter(owner_id=self.group_id)
