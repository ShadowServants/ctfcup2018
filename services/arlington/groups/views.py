import secrets

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView, DetailView, TemplateView
from django.views import View
from django.contrib.auth.models import Group
from django.urls import reverse

from groups.models import InviteCode
from libs.helpers import optional
from libs.mixins import MembershipRequiredMixin
from libs.cache import cache_decorator


@cache_decorator(lambda code: "invite_" + code, timeout=60 * 5)
def get_group_id_by_code(code):
    return optional(InviteCode.objects.filter(code=code).first()).group_id


class BaseGroupView(LoginRequiredMixin, MembershipRequiredMixin):
    def get_group(self) -> Group:
        return Group.objects.get(id=self.group_id)


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    fields = ["name"]
    template_name = "create.html"

    def form_valid(self, form):
        group = form.save()
        user = self.request.user
        user.groups.add(group)
        code = InviteCode(group=group, code=secrets.token_urlsafe(16))
        code.save()
        return redirect(reverse('groups:group_detail', args=[group.id]))


class GroupListView(LoginRequiredMixin, ListView):
    template_name = "list.html"
    context_object_name = 'groups'

    def get_queryset(self):
        queryset = self.request.user.groups.all().prefetch_related('user_set')
        return queryset


class GroupDetailView(BaseGroupView, DetailView):
    pk_url_kwarg = 'group_id'
    template_name = 'detail.html'
    model = Group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = context['group']
        invite_code = optional(InviteCode.objects.filter(group_id=group.id).first()).code
        context['invite_code'] = invite_code
        return context


class GroupJoinView(LoginRequiredMixin, View):
    def get(self, request, code):
        group_id = get_group_id_by_code(code)
        if group_id:
            group = Group.objects.get(id=group_id)
            request.user.groups.add(group)
            return redirect(reverse('groups:group_list'))
        return HttpResponseNotFound("Group not found")


class GroupSearchView(BaseGroupView, TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        return dict()


class GroupAbout(TemplateView):
    template_name = "about.html"
