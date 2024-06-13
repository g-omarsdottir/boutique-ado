from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm

from django.views.generic import (
    #CreateView,
    #ListView,
    #DetailView,
    DeleteView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin # either this or messages
from django.urls import reverse_lazy

# Create your views here.
def all_products(request):
    """A view to show all products, including sorting and search queries"""

    # Return from datbase - here no filtering, returning all products
    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if "sort" in request.GET:
            sortkey = request.GET["sort"]
            sort = sortkey
            if sortkey == "name":
                sortkey = "lower_name"
                products = products.annotate(lower_name=Lower("name"))
            if sortkey == "category":
                sortkey = "category__name"

            if "direction" in request.GET:
                direction = request.GET["direction"]
                if direction == "desc":
                    sortkey = f"-{sortkey}"
            products = products.order_by(sortkey)

        if "category" in request.GET:
            categories = request.GET["category"].split(",")
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if "q" in request.GET:
            query = request.GET["q"]
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse("products"))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    # return the current sorting methodology to the template
    current_sorting = f"{sort}_{direction}"

    # Add products to the context, so the products will be available in the template
    context = {
        "products": products,
        "search_term": query,
        "current_categories": categories,
        "current_sorting": current_sorting,
    }

    return render(request, "products/products.html", context)


def product_detail(request, product_id):
    """A view to show individual product details"""

    # Return from datbase - here no filtering, returning all products
    product = get_object_or_404(Product, pk=product_id)

    # Add products to the context, so the products will be available in the template
    context = {
        "product": product,
    }

    return render(request, "products/product_detail.html", context)

@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


class EditProductView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/edit_product.html'
    pk_url_kwarg = 'product_id'
    success_message = 'Successfully updated product!'
    error_message = 'Failed to update product. Please ensure the form is valid.'

    def test_func(self):
        """ Only allow the owner of the product to edit it """
        """
        Required for UserPassesTextMixin.
        Returns True if user passes test: is staff or superuser.
        Returns False if user is not is staff or superuser and throws 403 error.
        """
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.object
        messages.info(self.request, f'You are editing {self.object.name}')
        return context

    def get_success_url(self):
        return reverse_lazy('product_detail', args=[self.object.id])


class DeleteProductView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'products/delete_product.html'
    pk_url_kwarg = 'product_id'
    success_url = reverse_lazy('products')
    success_message = 'Product deleted!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        # Add your custom logic here to determine if the user should be allowed to delete the product
        return self.request.user.is_superuser or self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('product')