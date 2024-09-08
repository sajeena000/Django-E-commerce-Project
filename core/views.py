import calendar

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Avg, Count
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from requests import session
from taggit.models import Tag
from django.db.models import Min, Max
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from core.forms import ProductInquiryForm, ProductReviewForm, BillingInfoForm, ShippingInfoForm
from core.models import (
    Address,
    CartOrder,
    CartOrderProducts,
    Category,
    Gift,
    Product,
    ProductImages,
    ProductInquiry,
    ProductReview,
    wishlist_model,
    BillingInfo,
    ShippingInfo
)
from userauths.models import ContactUs, Profile

# Index


def index(request):
    # bannanas = Product.objects.all().order_by("-id")
    products = Product.objects.filter(
        product_status="published", featured=True
    ).order_by("-id")

    context = {"products": products}

    return render(request, "core/index.html", context)

# Product List View


def product_list_view(request):
    products = Product.objects.filter(
        product_status="published").order_by("-id")

    # Get the minimum and maximum price from the available products
    min_max_price = products.aggregate(Min('price'), Max('price'))

    # Get price filter values from the request (default to min and max price if not provided)
    min_price = request.GET.get('min_price', min_max_price['price__min'])
    max_price = request.GET.get('max_price', min_max_price['price__max'])
    # Convert to float for accurate comparison
    try:
        min_price = float(min_price)
        max_price = float(max_price)
    except ValueError:
        min_price = min_max_price['price__min']
        max_price = min_max_price['price__max']

    # Filter products by price range
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    # Get the latest 6 tags
    tags = Tag.objects.all().order_by("-id")[:6]

    context = {
        "products": products,
        "tags": tags,
        "min_max_price": min_max_price,
    }

    return render(request, "core/product-list.html", context)

# Add inquiry
# @login_required


def ajax_add_inquiry(request, pid):
    product = get_object_or_404(Product, pid=pid)
    if request.method == "POST":
        form = ProductInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.user = request.user
            inquiry.product = product
            inquiry.save()
            return redirect("core:product-detail", pid=pid)
    return redirect("core:product-detail", pid=pid)


def category_list_view(request):
    categories = Category.objects.all()

    context = {"categories": categories}
    return render(request, "core/category-list.html", context)


def category_product_list__view(request, cid):

    category = Category.objects.get(cid=cid)  # food, Cosmetics
    products = Product.objects.filter(
        product_status="published", category=category)

    context = {
        "category": category,
        "products": products,
    }
    return render(request, "core/category-product-list.html", context)


# @login_required
def product_detail_view(request, pid):
    product = get_object_or_404(Product, pid=pid)
    products = Product.objects.filter(
        category=product.category).exclude(pid=pid)

    # Get all reviews and inquiries related to the product
    reviews = ProductReview.objects.filter(product=product).order_by("-date")
    inquiries = ProductInquiry.objects.filter(
        product=product).order_by("-created_at")

    # Calculate average rating in the same query
    average_rating = reviews.aggregate(rating=Avg("rating"))

    # Initialize the forms
    review_form = ProductReviewForm()
    inquiry_form = ProductInquiryForm()

    make_review = True
    address = "Login To Continue"

    if request.user.is_authenticated:
        # Try to get the address; handle the case where no address is found
        try:
            address = Address.objects.get(status=True, user=request.user)
        except Address.DoesNotExist:
            address = None

        # Check if the user has already reviewed the product
        user_review_count = reviews.filter(user=request.user).count()
        if user_review_count > 0:
            make_review = False

        if request.method == "POST":
            if "review_submit" in request.POST:
                review_form = ProductReviewForm(request.POST)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.user = (
                        request.user
                    )  # Associate the review with the logged-in user
                    review.product = (
                        product  # Associate the review with the current product
                    )
                    review.save()
                    return redirect("core:product-detail", pid=product.pid)
            elif "inquiry_submit" in request.POST:
                inquiry_form = ProductInquiryForm(request.POST)
                if inquiry_form.is_valid():
                    inquiry = inquiry_form.save(commit=False)
                    inquiry.user = (
                        request.user
                    )  # Associate the inquiry with the logged-in user
                    inquiry.product = (
                        product  # Associate the inquiry with the current product
                    )
                    inquiry.save()
                    return redirect("core:product-detail", pid=product.pid)

    # Get product images
    p_image = product.p_images.all() if product.p_images.exists() else []

    # Prepare context for the template
    context = {
        "p": product,
        "address": address,
        "make_review": make_review,
        "review_form": review_form,
        "inquiry_form": inquiry_form,
        "p_image": p_image,
        "average_rating": average_rating,
        "reviews": reviews,
        "inquiries": inquiries,
        "products": products,
    }

    return render(request, "core/product-detail.html", context)


def tag_list(request, tag_slug=None):

    products = Product.objects.filter(
        product_status="published").order_by("-id")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {"products": products, "tag": tag}

    return render(request, "core/tag.html", context)


def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review=request.POST["review"],
        rating=request.POST["rating"],
    )

    context = {
        "user": user.username,
        "review": request.POST["review"],
        "rating": request.POST["rating"],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(
        rating=Avg("rating")
    )

    return JsonResponse(
        {"bool": True, "context": context, "average_reviews": average_reviews}
    )


def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products": products,
        "query": query,
    }
    return render(request, "core/search.html", context)


def filter_product(request):
    categories = request.GET.getlist("category[]")

    min_price = request.GET["min_price"]
    max_price = request.GET["max_price"]

    products = (
        Product.objects.filter(
            product_status="published").order_by("-id").distinct()
    )

    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()
    else:
        products = (
            Product.objects.filter(product_status="published")
            .order_by("-id")
            .distinct()
        )

    data = render_to_string(
        "core/async/product-list.html", {"products": products})
    return JsonResponse({"data": data})


def add_to_cart(request):
    product_id = str(request.GET.get("id"))
    price = request.GET.get("price", "0").strip()  # Capture price
    pid = request.GET.get("pid", "")  # Capture pid

    try:
        price = float(price)
    except ValueError:
        price = 0  # Handle invalid price

    cart_product = {
        product_id: {
            "title": request.GET.get("title", ""),
            "qty": request.GET.get("qty", "1"),
            "price": price,  # Store the price
            "image": request.GET.get("image", ""),
            "pid": pid,  # Store the pid
        }
    }

    if "cart_data_obj" in request.session:
        cart_data = request.session["cart_data_obj"]
        if product_id in cart_data:
            return JsonResponse(
                {
                    "message": "Product is already in the cart",
                    "data": cart_data,
                    "totalcartitems": len(cart_data),
                }
            )
        else:
            cart_data.update(cart_product)
            request.session["cart_data_obj"] = cart_data
    else:
        request.session["cart_data_obj"] = cart_product

    return JsonResponse(
        {
            "message": "Product added to cart",
            "data": request.session["cart_data_obj"],
            "totalcartitems": len(request.session["cart_data_obj"]),
        }
    )


def cart_view(request):
    cart_total_amount = 0
    cart_data = request.session.get("cart_data_obj", {})
    for p_id, item in cart_data.items():
        print(
            f"Product ID: {p_id}, Price: {
                item['price']}, Quantity: {item['qty']}"
        )  # Debugging line
        try:
            subtotal = int(item["qty"]) * float(item["price"])
            item["subtotal"] = subtotal
            cart_total_amount += subtotal
        except ValueError as e:
            print(f"Error calculating subtotal for product ID {p_id}: {e}")
            item["subtotal"] = "Error"
    return render(
        request,
        "core/cart.html",
        {
            "cart_data": cart_data,
            "totalcartitems": len(cart_data),
            "cart_total_amount": cart_total_amount,
        },
    )


def delete_item_from_cart(request):
    product_id = str(request.GET.get("id"))
    if "cart_data_obj" in request.session:
        cart_data = request.session["cart_data_obj"]
        if product_id in cart_data:
            # Correctly delete the item from cart_data
            del cart_data[product_id]
            request.session["cart_data_obj"] = cart_data  # Update the session
            print(f"Deleted product {product_id} from cart")  # Debugging line
        else:
            print(f"Product {product_id} not found in cart")  # Debugging line

    # Recalculate the total cart amount after deletion
    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for p_id, item in request.session["cart_data_obj"].items():
            try:
                price = float(item["price"])
            except (ValueError, TypeError):
                price = 0  # Handle cases where price is invalid
            cart_total_amount += int(item["qty"]) * price

    context = render_to_string(
        "core/async/cart-list.html",
        {   "currency_icon" : f"<i class='{request.session['currency_icon']}'></i>" if request.session['currency_icon'] else "$",
            "cart_data": request.session["cart_data_obj"],
            "totalcartitems": len(request.session["cart_data_obj"]),
            "cart_total_amount": cart_total_amount,
        },
    )
    return JsonResponse(
        {"data": context, "totalcartitems": len(
            request.session["cart_data_obj"])}
    )


def update_cart(request):
    product_id = str(request.GET["id"])
    product_qty = request.GET["qty"]

    if "cart_data_obj" in request.session:
        if product_id in request.session["cart_data_obj"]:
            cart_data = request.session["cart_data_obj"]
            cart_data[str(request.GET["id"])]["qty"] = product_qty
            request.session["cart_data_obj"] = cart_data

    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for p_id, item in request.session["cart_data_obj"].items():
            cart_total_amount += int(item["qty"]) * float(item["price"])

    context = render_to_string(
        "core/async/cart-list.html",
        {
            "cart_data": request.session["cart_data_obj"],
            "totalcartitems": len(request.session["cart_data_obj"]),
            "cart_total_amount": cart_total_amount,
        },
    )
    return JsonResponse(
        {"data": context, "totalcartitems": len(
            request.session["cart_data_obj"])}
    )
    
    
def update_currency(request, currency_code, currency, exchange_rate, currency_icon):
    
        request.session['currency_code'] = currency_code
        request.session['currency'] = currency
        request.session['exchange_rate'] = exchange_rate
        request.session['currency_icon'] = currency_icon
        
        return redirect(request.META.get('HTTP_REFERER'))
    


@login_required
def place_order_view(request):
    cart_total_amount = 0
    total_amount = 0
    billing_form = BillingInfoForm(prefix='billing')
    shipping_form = ShippingInfoForm(prefix='shipping')

    active_address = Address.objects.filter(
        user=request.user, status=True).first()

    # Getting total amount for Paypal Amount
    for p_id, item in request.session["cart_data_obj"].items():
        total_amount += int(item["qty"]) * float(item["price"])

        # Getting total amount for The Cart
    for p_id, item in request.session["cart_data_obj"].items():
        cart_total_amount += int(item["qty"]) * float(item["price"])

    return render(
        request,
        "core/place-order.html",
        {
            "cart_data": request.session["cart_data_obj"],
            "totalcartitems": len(request.session["cart_data_obj"]),
            "cart_total_amount": cart_total_amount,
            "active_address": active_address,
            "billing_form": billing_form,
            "shipping_form": shipping_form
        },
    )


@login_required
def checkout_view(request):
    if request.method == 'POST':
        cart_total_amount = 0
        total_amount = 0
        order = None
        billing = None
        shipping = None

        # Checking if cart_data_obj session exists
        if "cart_data_obj" in request.session:

            # Getting total amount for Paypal Amount
            for p_id, item in request.session["cart_data_obj"].items():
                total_amount += int(item["qty"]) * float(item["price"])
            
            
            billing_form = BillingInfoForm(request.POST, prefix='billing')
            shipping_form = ShippingInfoForm(request.POST, prefix='shipping')

            forms_valid = all([billing_form.is_valid(), shipping_form.is_valid()])

            if forms_valid:
                try:
                    order = CartOrder.objects.create(
                        user=request.user, price=total_amount)

                    billing = billing_form.save(commit=False)
                    billing.order = order
                    billing.payment_method = "paypal"
                    billing.save()

                    shipping = shipping_form.save(commit=False)
                    shipping.order = order
                    shipping.save()
                   
                except Exception as e:
                    messages.error(request, f"An error occurred: {str(e)}")
            else:
                # Forms are not valid, collect and display errors
                errors = {}
                for form in [billing_form, shipping_form]:
                    for field, error_list in form.errors.items():
                        errors[f"{form.prefix}-{field}"] = error_list


                for field, error_list in errors.items():
                    for error in error_list:
                        messages.error(request, f"{field}: {error}")
                        
                # Or redirect back to the form page
                return redirect(request.META.get('HTTP_REFERER'))

            # Getting total amount for The Cart
            for p_id, item in request.session["cart_data_obj"].items():
                cart_total_amount += int(item["qty"]) * float(item["price"])

                cart_order_products = CartOrderProducts.objects.create(
                    order=order,
                    invoice_no="INVOICE_NO-" + str(order.id),  # INVOICE_NO-5,
                    item=item["title"],
                    image=item["image"],
                    qty=item["qty"],
                    price=item["price"],
                    total=float(item["qty"]) * float(item["price"]),
                )

            host = request.get_host()
            paypal_dict = {
                "business": settings.PAYPAL_RECEIVER_EMAIL,
                "amount": cart_total_amount,
                "item_name": "Order-Item-No-" + str(order.id),
                "invoice": "INVOICE_NO-" + str(order.id),
                "currency_code": request.session['currency_code'] if request.session['currency_code'] else 'USD',
                "notify_url": "http://{}{}".format(host, reverse("core:paypal-ipn")),
                "return_url": "http://{}{}".format(host, reverse("core:payment-completed", kwargs={"order_id": order.id})),
                "cancel_url": "http://{}{}".format(host, reverse("core:payment-failed")),
            }

            paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

            active_address = Address.objects.filter(
                user=request.user, status=True).first()

            return render(
                request,
                "core/checkout.html",
                {
                    "cart_data": request.session["cart_data_obj"],
                    "totalcartitems": len(request.session["cart_data_obj"]),
                    "cart_total_amount": cart_total_amount,
                    "paypal_payment_button": paypal_payment_button,
                    "active_address": active_address,
                    "billing": billing,
                    "shipping": shipping
                },
            )


@login_required
def gift_item(request, item_id):
    # Get the item to gift
    item = get_object_or_404(Product, id=item_id)

    if request.method == "POST":
        # Get recipient details from the form
        receiver_name = request.POST.get("receiver_name")
        receiver_email = request.POST.get("receiver_email")
        receiver_address = request.POST.get("receiver_address")

        # Validate data (if necessary)
        if not (receiver_name and receiver_email and receiver_address):
            messages.error(request, "All recipient details are required.")
            return redirect("gift_item", item_id=item_id)

        # Create Gift object
        gift = Gift.objects.create(
            sender=request.user,
            receiver_name=receiver_name,
            receiver_email=receiver_email,
            receiver_address=receiver_address,
            item=item,
        )

        # Save session data to pass to checkout
        request.session["gift_data"] = {
            "item_id": item_id,
            "receiver_name": receiver_name,
            "receiver_email": receiver_email,
            "receiver_address": receiver_address,
        }

        return redirect("gift_checkout")

    return render(request, "core/gift_form.html", {"item": item})


@login_required
def gift_checkout(request):
    # Retrieve gift data from session
    gift_data = request.session.get("gift_data")

    if not gift_data:
        messages.error(request, "No gift data found.")
        return redirect("core:index")

    # Get the product details for the gifted item
    item = get_object_or_404(Product, id=gift_data["item_id"])

    # Calculate price for the single gifted item
    gift_total_amount = float(item.price)

    # Create an order for the gifted item
    order = CartOrder.objects.create(
        user=request.user, price=gift_total_amount)

    # Create the order products for the gifted item
    cart_order_products = CartOrderProducts.objects.create(
        order=order,
        invoice_no="INVOICE_NO-" + str(order.id),
        item=item.title,
        image=item.image,
        qty=1,
        price=item.price,
        total=gift_total_amount,
    )

    # PayPal setup
    host = request.get_host()
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": gift_total_amount,
        "item_name": "Gifted Item No-" + str(order.id),
        "invoice": "INVOICE_NO-" + str(order.id),
        "currency_code": "USD",
        "notify_url": "http://{}{}".format(host, reverse("core:paypal-ipn")),
        "return_url": "http://{}{}".format(host, reverse("core:payment-completed")),
        "cancel_url": "http://{}{}".format(host, reverse("core:payment-failed")),
    }

    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

    return render(
        request,
        "core/gift_checkout.html",
        {
            "gift_data": gift_data,
            "gift_total_amount": gift_total_amount,
            "paypal_payment_button": paypal_payment_button,
        },
    )


@login_required
def payment_completed_view(request, order_id):
    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for p_id, item in request.session["cart_data_obj"].items():
            cart_total_amount += int(item["qty"]) * float(item["price"])

    # Fetch the order, billing, and shipping info
    order = get_object_or_404(CartOrder, pk=order_id)
    order.paid_status = True
    order.save()

    billing = BillingInfo.objects.filter(order=order).first()
    shipping = ShippingInfo.objects.filter(order=order).first()

    # sending email
    context = {
        "billing": billing,
        "shipping": shipping,
        "cart_data": request.session["cart_data_obj"],
        "totalcartitems": len(request.session["cart_data_obj"]),
        "cart_total_amount": cart_total_amount,
        "currency_code" : request.session["currency_code"] if request.session["currency_code"] else "USD"
    }

    receiver_email = [shipping.email,
                      billing.email if billing.email != shipping.email else '']
    template_name = "mail/invoice-mail.html"
    convert_to_html_content = render_to_string(
        template_name=template_name,
        context=context
    )
    plain_message = strip_tags(convert_to_html_content)

    yo_send_it = send_mail(subject="Order Placed !!",
                           message=plain_message,
                           from_email=settings.EMAIL_HOST_USER,
                           recipient_list=receiver_email,
                           html_message=convert_to_html_content,
                           fail_silently=True
                           )

    return render(
        request,
        "core/payment-completed.html",
        context

    )


@login_required
def payment_failed_view(request):
    return render(request, "core/payment-failed.html")


@login_required
def customer_dashboard(request):
    orders_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)

    orders = (
        CartOrder.objects.annotate(month=ExtractMonth("order_date"))
        .values("month")
        .annotate(count=Count("id"))
        .values("month", "count")
    )
    month = []
    total_orders = []

    for i in orders:
        month.append(calendar.month_name[i["month"]])
        total_orders.append(i["count"])

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
        )
        messages.success(request, "Address Added Successfully.")
        return redirect("core:dashboard")
    else:
        print("Error")

    user_profile = Profile.objects.get(user=request.user)
    print("user profile is: #########################", user_profile)

    context = {
        "user_profile": user_profile,
        "orders": orders,
        "orders_list": orders_list,
        "address": address,
        "month": month,
        "total_orders": total_orders,
    }
    return render(request, "core/dashboard.html", context)


def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderProducts.objects.filter(order=order)

    context = {
        "order_items": order_items,
    }
    return render(request, "core/order-detail.html", context)


def make_address_default(request):
    id = request.GET["id"]
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})


@login_required
def wishlist_view(request):
    wishlist = wishlist_model.objects.all()
    context = {"wishlist": wishlist}
    return render(request, "core/wishlist.html", context)


def add_to_wishlist(request):
    product_id = request.GET["id"]
    product = Product.objects.get(id=product_id)
    print("product id isssssssssssss:" + product_id)

    context = {}

    wishlist_count = wishlist_model.objects.filter(
        product=product, user=request.user
    ).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {"bool": True}
    else:
        new_wishlist = wishlist_model.objects.create(
            user=request.user,
            product=product,
        )
        context = {"bool": True}

    return JsonResponse(context)


def remove_wishlist(request):
    pid = request.GET["id"]
    wishlist = wishlist_model.objects.filter(user=request.user)
    wishlist_d = wishlist_model.objects.get(id=pid)
    delete_product = wishlist_d.delete()

    context = {"bool": True, "w": wishlist}
    wishlist_json = serializers.serialize("json", wishlist)
    t = render_to_string("core/async/wishlist-list.html", context)
    return JsonResponse({"data": t, "w": wishlist_json})


# Other Pages
def contact(request):
    return render(request, "core/contact.html")


def ajax_contact_form(request):
    full_name = request.GET["full_name"]
    email = request.GET["email"]
    phone = request.GET["phone"]
    subject = request.GET["subject"]
    message = request.GET["message"]

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )

    data = {"bool": True, "message": "Message Sent Successfully"}

    return JsonResponse({"data": data})


def about_us(request):
    return render(request, "core/about_us.html")


def purchase_guide(request):
    return render(request, "core/purchase_guide.html")


def privacy_policy(request):
    return render(request, "core/privacy_policy.html")


def terms_of_service(request):
    return render(request, "core/terms_of_service.html")
