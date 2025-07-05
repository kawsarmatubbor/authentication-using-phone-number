from django.urls import path
from .views import (
    sign_up_view,
    sign_in_view,
    logout_view,
    forgot_password_view,
    verification_view,
    reset_password_view
)

urlpatterns = [
    path('sign-up/', sign_up_view, name='sign-up'),
    path('sign-in/', sign_in_view, name='sign-in'),
    path('logout/', logout_view, name='logout' ),
    path('forgot-password/', forgot_password_view, name='forgot-password'),
    path('verification/', verification_view, name='verification'),
    path('reset-password/', reset_password_view, name='reset-password'),
]
