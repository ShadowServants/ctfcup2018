from django.urls import path, include

from groups import views

urlpatterns = [
    path('create', views.GroupCreateView.as_view(), name='group_create'),
    path('', views.GroupListView.as_view(), name='group_list'),
    path('join/<slug:code>/', views.GroupJoinView.as_view(), name='group_join'),
    path('<int:group_id>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('<int:group_id>/', include('groups.document_urls')),
    path('about', views.GroupAbout.as_view(), name='group_about')
]
