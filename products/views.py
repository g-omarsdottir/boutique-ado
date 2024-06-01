from django.shortcuts import render
from .models import Product

# Create your views here.
def all_products(request):
    """ A view to show all products, including sorting and search queries """

    # Return from datbase - here no filtering, returning all products
    products = Product.objects.all()

    # Add products to the context, so the products will be available in the template
    context = {
        'products': products,
    }

    return render(request, 'products/products.html', context)