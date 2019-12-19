from django.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from . import views
route = routers.DefaultRouter()
#route.register(r'web',views.web)
#route.register(r'wv',views.jsondata)
urlpatterns = [
path('',views.home,name='home'),
path("control_panel/",views.control_panel,name='control_panel'),
path('',include(route.urls)), path('',include('rest_framework.urls',namespace="rest_framework")),
path('category/', views.Categories_and_websites),
path('category/<int:id>/',views.categories),
path('wd/',views.websites_data),
path('json/slider/',views.Slider_data),
path('wd/<int:id>/',views.websites_data),
path('wd/<int:id>/<str:subCategory>/',views.websites_data),
path('wv/',views.jsondata),
path("wv/<id>/",views.json_data),
path("Login/",views.Login,name="Login"),
path("Logout/",views.Logout,name="Logout"),
path("contact/",views.contact,name="contact"),
path("contact/<str:type>/",views.contact,name="contact"),
path("websites/<int:pk>/<str:name>/",views.all_websites,name='websites'),
path("websites/",views.all_websites,name='websites'),
path("websites/<int:pk>/<str:name>/<str:sub_category>/",views.all_websites,name='websites'),
path('add_websites/',views.add_websites,name="add_websites"),
path('add_category/',views.add_category,name="add_category"),
path('update_category/<pk>/',views.update_category.as_view(),name="update_category"),
path('update_category/',views.update_category_select,name="update_category"),
path('delete_category/<pk>/',views.delete_category.as_view(),name="delete_category"),
path('delete_category/',views.delete_category_select,name="delete_category_select"),
path('update_website/<pk>/',views.update_websites,name="update_website"),
path('update_website/',views.update_websites_select,name="update_website"),
path('update_single_website/',views.update_single_website_select,name="update_single_website_select"),
path('update_single_website/<pk>/<str:website>/',views.update_website.as_view(),name="update_single_website"),

path('delete_website/',views.delete_websites,name="delete_website"),
]
