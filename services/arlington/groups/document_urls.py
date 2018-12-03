from groups import document_views as views
from django.urls import path

urlpatterns = [
    path('documents/create', views.DocumentCreateView.as_view(), name='document_create'),
    path('documents/search', views.DocumentSearchView.as_view(), name='documents_search'),
    path('documents/list', views.DocumentListView.as_view(), name="documents_list"),
]
