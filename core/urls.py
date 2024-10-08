from django.urls import include, path

from core.views import (
    about_us,
    add_to_cart,
    add_to_wishlist,
    ajax_add_inquiry,
    ajax_add_review,
    ajax_contact_form,
    cart_view,
    category_list_view,
    category_product_list__view,
    place_order_view,
    checkout_view,
    contact,
    customer_dashboard,
    delete_item_from_cart,
    filter_product,
    gift_checkout,
    index,
    make_address_default,
    order_detail,
    payment_completed_view,
    payment_failed_view,
    privacy_policy,
    product_detail_view,
    product_list_view,
    purchase_guide,
    remove_wishlist,
    search_view,
    tag_list,
    terms_of_service,
    update_currency,
    update_cart,
    wishlist_view,
)

app_name = "core"

urlpatterns = [
    
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("product/<pid>/", product_detail_view, name="product-detail"),
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list__view, name="category-product-list"),
    path("products/tag/<slug:tag_slug>/", tag_list, name="tags"),
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),
    path("search/", search_view, name="search"),
    path("gift/", gift_checkout, name="gift_checkout"),
    path("gift_checkout/", gift_checkout, name="gift_checkout"),
    path("filter-products/", filter_product, name="filter-product"),
    path("add-to-cart/", add_to_cart, name="add-to-cart"),
    path("cart/", cart_view, name="cart"),
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),
    path("update-currency/<str:currency_code>/<str:currency>/<str:exchange_rate>/<str:currency_icon>", update_currency, name="update-currency"),
    path("update-cart/", update_cart, name="update-cart"),
    path("place-an-order/", place_order_view, name="place-an-order"),
    path("checkout/", checkout_view, name="checkout"),
    # Paypal URL
    path("paypal/", include("paypal.standard.ipn.urls")),
    path("payment-completed/<int:order_id>", payment_completed_view, name="payment-completed"),
    path("payment-failed/", payment_failed_view, name="payment-failed"),
    path("dashboard/", customer_dashboard, name="dashboard"),
    path("dashboard/order/<int:id>/", order_detail, name="order-detail"),
    path("make-default-address/", make_address_default, name="make-default-address"),
    path("wishlist/", wishlist_view, name="wishlist"),
    path("add-to-wishlist/", add_to_wishlist, name="add-to-wishlist"),
    path("remove-from-wishlist/", remove_wishlist, name="remove-from-wishlist"),
    path("contact/", contact, name="contact"),
    path("ajax-contact-form/", ajax_contact_form, name="ajax-contact-form"),
    path("about_us/", about_us, name="about_us"),
    path("purchase_guide/", purchase_guide, name="purchase_guide"),
    path("privacy_policy/", privacy_policy, name="privacy_policy"),
    path("terms_of_service/", terms_of_service, name="terms_of_service"),
    path("product/<pid>/", product_detail_view, name="product-detail"),
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),
    path("ajax-add-inquiry/<int:pid>/", ajax_add_inquiry, name="ajax-add-inquiry"),
]
