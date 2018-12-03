from django.urls import path, include

from web import draft_views, views, auth_views

urlpatterns = [
    path('', views.IndexView.as_view()),
    path('home', views.HomeView.as_view()),
    path('auth/register', auth_views.RegisterView.as_view(), name='register'),
    path('auth/login', auth_views.LoginView.as_view(), name='login'),
    path('auth/logout', auth_views.logout_view, name='logout'),
    path('drafts/create', draft_views.DraftCreate.as_view(), name='draft_create'),
    path('drafts/', draft_views.DraftList.as_view(), name='draft_list'),
    path('drafts_about', draft_views.DraftAbout.as_view(), name='draft_about'),
    path('groups/', include(('groups.urls', 'groups'), namespace='groups'))
]
