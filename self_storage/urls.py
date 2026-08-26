from django.urls import path
from . import views

app_name = "self_storage"

urlpatterns = [
    path("", views.index, name="index"),
    path("boxes/", views.boxes, name="boxes"),
    path("faq/", views.faq, name="faq"),
    path("my-rent/", views.my_rent, name="my_rent"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path('rental/', views.rental_request, name='rental'),
]
