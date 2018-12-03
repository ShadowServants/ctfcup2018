from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseNotFound
from django.views import View


class MembershipRequiredMixin(View, AccessMixin):
    raise_exception = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.group_id = None

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        group_id = self.kwargs.get('group_id')
        if not group_id:
            return self.handle_no_permission()
        if user.groups.filter(pk=group_id).exists():
            self.group_id = group_id
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseNotFound("<h1>404 No such group</h1>")
