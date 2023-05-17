from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('', views.index, name='index'),
    # Infinite scroll fetch api
    path('postlist', views.listing_api, name='index_listing_api'),
    path('profile/<str:username_ch>', views.profile_page, name='profile_page'),
    path('settings', views.settings, name='settings'),
    path('newpost', views.newpost, name='newpost'),
    path('post_action/like', views.like, name='like'),
    path('comments/<uuid:post_id>', views.comment, name='like'),
    path('user_action/follow', views.follow, name='follow'),
]
