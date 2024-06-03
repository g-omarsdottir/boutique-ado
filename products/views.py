from django.shortcuts import render, get_object_or_404
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


def product_detail(request, product_id):
    """ A view to show individual product details """

    # Return from datbase - here no filtering, returning all products
    product = get_object_or_404(Product, pk=product_id)

    # Add products to the context, so the products will be available in the template
    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)