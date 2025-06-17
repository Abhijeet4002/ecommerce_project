# store/views.py
import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from .utils import cartData
from .forms import CustomUserCreationForm

# --- Storefront and Product Views (Open to all users) ---

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    products = Product.objects.all()
    if category_id:
        products = products.filter(category__id=category_id)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)
    context = {
        'products': products,
        'categories': categories,
        'featured_products': featured_products,
        'cartItems': cartItems,
        'query': query,
        'selected_category': int(category_id) if category_id else None,
    }
    return render(request, 'store/main.html', context)

def product_detail(request, pk):
    data = cartData(request)
    cartItems = data['cartItems']
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.all().order_by('-created_at')
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')
        if rating and review_text:
            ProductReview.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                review_text=review_text
            )
            return redirect('product_detail', pk=pk)
    context = {'product': product, 'reviews': reviews, 'cartItems': cartItems}
    return render(request, 'store/product_detail.html', context)

# --- Cart and Order Logic (Requires Login) ---

@login_required
# store/views.py

# ... (other views before this) ...

@login_required
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    
    # --- THIS IS THE LINE TO FIX ---
    # OLD, WRONG CODE:
    # order, created = Order.objects.get_or_create(customer=customer, complete=False)
    # NEW, CORRECT CODE:
    order, created = Order.objects.get_or_create(customer=customer, status='Pending')
    # --- END OF FIX ---

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    elif action == 'delete':
        orderItem.quantity = 0

    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()
        
    return JsonResponse('Item was updated', safe=False)

# ... (other views after this) ...

@login_required
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

@login_required
def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    if not items:
        return redirect('store')
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

@login_required
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    payment_method = data.get('payment_method')

    # Since user must be logged in, we can safely get their customer profile and order
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer,  status='Pending')
    # Security Check 1: Ensure order total is not zero
    if order.get_cart_total <= 0:
        return JsonResponse({'error': 'Cannot process an order with zero total.'}, status=400)
    
    # Security Check 2: Verify total from frontend matches backend total
    total_from_frontend = float(data['form']['total'])
    if total_from_frontend != order.get_cart_total:
        return JsonResponse({'error': 'Total price mismatch. Please try again.'}, status=400)

    # Security Check 3: Validate shipping and contact info
    shipping_info = data.get('shipping', {})
    if not all([
        shipping_info.get('address'),
        shipping_info.get('city'),
        shipping_info.get('state'),
        shipping_info.get('zipcode'),
        shipping_info.get('mobile_number')
    ]):
        return JsonResponse({'error': 'Shipping and contact information is incomplete.'}, status=400)

    # All checks passed, finalize the order
    order.complete = True
    if payment_method == 'PayPal':
        paypal_data = data.get('paypal_details')
        if not paypal_data:
            return JsonResponse({'error': 'PayPal transaction details not found.'}, status=400)
        
        # Security Check: Verify the payment was actually completed.
        paypal_status = paypal_data.get('status')
        if paypal_status != 'COMPLETED':
            return JsonResponse({'error': f'PayPal payment not completed. Status: {paypal_status}'}, status=400)
        
        # Use the REAL PayPal transaction ID
        order.transaction_id = paypal_data.get('id')
        order.status = 'Completed' # Payment is done, so the order is complete.

    elif payment_method == 'COD':
        # For COD, we just record the order and set it to 'Processing'.
        timestamp = datetime.datetime.now().timestamp()
        order.transaction_id = f"COD-{timestamp}"
        order.status = 'Processing' # The order is now waiting for physical delivery and payment.
    
    else:
        return JsonResponse({'error': 'Invalid payment method specified.'}, status=400)

    order.save()
    
    # Save the final shipping address
    ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=shipping_info['address'],
        city=shipping_info['city'],
        state=shipping_info['state'],
        zipcode=shipping_info['zipcode'],
        mobile_number=shipping_info['mobile_number'],
        alt_mobile_number=shipping_info.get('alt_mobile_number', '')
    )
    
    return JsonResponse({'message': 'Order placed successfully!'})

# --- Authentication and User Views ---

def register_user(request):
    if request.user.is_authenticated:
        return redirect('store')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user, name=user.username, email=user.email)
            login(request, user)
            return redirect('store')
    else:
        form = CustomUserCreationForm() 
    return render(request, 'store/register.html', {'form': form})

def login_user(request):
    if request.user.is_authenticated:
        return redirect('store')
    
    # Capture the 'next' URL from the query parameter
    next_page = request.GET.get('next')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to the 'next' page if it exists, otherwise to the store
                if next_page:
                    return redirect(next_page)
                return redirect('store')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form, 'next': next_page})

def logout_user(request):
    logout(request)
    return redirect('store')

@login_required
def order_history(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    if created:
        customer.name = request.user.username
        customer.email = request.user.email
        customer.save()
        
    data = cartData(request)
    cartItems = data['cartItems']
    # Fetch all orders for the logged-in user, excluding 'Pending' status
    orders = Order.objects.filter(
        customer=request.user.customer
    ).exclude(
        status='Pending'
    ).order_by('-date_ordered')
    
    context = {'orders': orders, 'cartItems': cartItems}
    return render(request, 'store/order_history.html', context)