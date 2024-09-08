from django.contrib import admin
from core.models import CartOrderProducts, Product, Category,  CartOrder, ProductImages, ProductReview, wishlist_model, Address


class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_editable = ['title', 'price', 'featured', 'product_status']
    list_display = ['user', 'title', 'product_image', 'price',
                    'category',  'featured', 'product_status', 'pid']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image']


class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['paid_status', 'product_status', 'sku']
    list_display = ['user',  'price', 'paid_status',
                    'order_date', 'product_status','billing_address', 'shipping_address', 'sku']
    
    def billing_address(self, CartOrder):
        billing = CartOrder.billing
        return f"{billing.street_address}, {billing.city}, {billing.country}"
    
    def shipping_address(self, CartOrder):
        shipping = CartOrder.shipping
        return f"{shipping.street_address}, {shipping.city}, {shipping.country}"


class CartOrderProductsAdmin(admin.ModelAdmin):
    list_display = ['order', 'invoice_no',
                    'item', 'image', 'qty', 'price', 'total']


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'rating']


class wishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']


class AddressAdmin(admin.ModelAdmin):
    list_editable = ['address', 'status']
    list_display = ['user', 'address', 'status']


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderProducts, CartOrderProductsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(wishlist_model, wishlistAdmin)
admin.site.register(Address, AddressAdmin)
