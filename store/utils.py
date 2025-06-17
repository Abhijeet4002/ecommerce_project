# store/utils.py
import json
from .models import *

# def cookieCart(request):
#     # ... (This function remains unchanged) ...
#     try:
#         cart = json.loads(request.COOKIES['cart'])
#     except:
#         cart = {}
    
#     items = []
#     order = {'get_cart_total': 0, 'get_cart_items': 0}
#     cartItems = order['get_cart_items']

#     for i in cart:
#         try:
#             cartItems += cart[i]['quantity']
#             product = Product.objects.get(id=i)
#             total = (product.price * cart[i]['quantity'])
#             order['get_cart_total'] += total
#             order['get_cart_items'] += cart[i]['quantity']
            
#             item = {
#                 'product': {
#                     'id': product.id,
#                     'name': product.name,
#                     'price': product.price,
#                     'imageURL': product.imageURL
#                 },
#                 'quantity': cart[i]['quantity'],
#                 'get_total': total
#             }
#             items.append(item)
#         except:
#             pass
#     return {'cartItems': cartItems, 'order': order, 'items': items}
# store/utils.py

# cookieCart is no longer used by the views, you can even remove the whole function.
# I'll leave it here for reference, but it's now dead code.
# def cookieCart(request):
#     # ...
#     pass
# store/utils.py
from .models import * # Your other imports

def cartData(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        if created:
            customer.name = request.user.username
            customer.email = request.user.email
            customer.save()
        
        # --- THIS IS THE LINE TO FIX ---
        # OLD,  WRONG CODE: order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # NEW, CORRECT CODE: We look for an order that is still 'Pending'.
        order, created = Order.objects.get_or_create(customer=customer, status='Pending')
        # --- END OF FIX ---

        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # This part is for non-logged-in users, which we don't use for cart actions,
        # but it's good to have it return a consistent structure.
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0

    return {'cartItems': cartItems, 'order': order, 'items': items}