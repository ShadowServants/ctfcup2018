from django.shortcuts import redirect
from django.views.generic import TemplateView

from web.models import Draft


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/home')
        return super().get(request, *args, **kwargs)


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        last_draft = Draft.objects.filter(owner=self.request.user).order_by('-id').first()
        drafts_count = Draft.objects.filter(owner=self.request.user).count()

        groups = self.request.user.groups.all()

        last_draft_text_short = last_draft.text if last_draft is not None else ""
        last_draft_text_short = last_draft_text_short if len(last_draft_text_short) < 30 else last_draft_text_short[:20] + "..."

        return {
            'last_draft': last_draft,
            'last_draft_text_short': last_draft_text_short,
            'drafts_count': drafts_count,
            'groups_count': len(groups),
            'last_group': groups[len(groups) - 1] if len(groups) > 0 else None
        }
