from django.urls import path
from . import views

app_name = "market_ai"

urlpatterns = [
    path("price_suggest/", views.price_suggest, name="price_suggest"),
    path("chat/", views.ai_chat, name="ai_chat"),
    path("recommend/<int:pk>/", views.recommend_similar, name="recommend_similar"),
]