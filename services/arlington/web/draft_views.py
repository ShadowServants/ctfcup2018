from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, TemplateView

from web.models import Draft


class DraftCreate(LoginRequiredMixin, CreateView):
    template_name = "draft/create.html"
    model = Draft
    fields = ['title', 'text']

    def form_valid(self, form):
        draft = form.save(commit=False)
        draft.owner_id = self.request.user.id
        draft.save()
        return redirect('/')


class DraftList(LoginRequiredMixin, ListView):
    template_name = 'draft/list.html'
    context_object_name = 'drafts'

    def get_queryset(self):
        return Draft.objects.filter(owner=self.request.user)


# Do we need it, in fact we have ListView ?
class DraftAbout(TemplateView):
    template_name = "draft/about.html"



# Do we need it, in fact we have ListView ?
class DraftDetail(LoginRequiredMixin, DetailView):
    pass


class DraftUpdate(LoginRequiredMixin, UpdateView):
    pass


# Do we need this feature ?
class DraftDelete(LoginRequiredMixin, DeleteView):
    pass
