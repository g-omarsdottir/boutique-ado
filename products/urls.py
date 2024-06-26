from django.urls import path
from . import views

urlpatterns = [
    path("", views.all_products, name="products"),
    path("<int:product_id>/", views.product_detail, name="product_detail"),
    path("add/", views.add_product, name="add_product"),
    path('edit/<int:product_id>/', views.EditProductView.as_view(), name='edit_product'),
    path('delete/<int:product_id>/', views.DeleteProductView.as_view(), name='delete_product'),
]
