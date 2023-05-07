from django.contrib import admin
from product.models import Type, Category, Product, Convenience, Image, Booking, Like, Comment

admin.site.register(Type)
admin.site.register(Category)
admin.site.register(Convenience)
admin.site.register(Image)
admin.site.register(Booking)
admin.site.register(Like)
admin.site.register(Comment)


class ProductImageInline(admin.TabularInline):
    model = Image
    readonly_fields = ('id', 'image_tag')
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price_per_night', 'is_active', 'owner', 'rooms_qty', 'address')
    list_display_links = ('id', 'name')
    list_filter = ('name', 'is_active')
    search_fields = ('id', 'name')
    inlines = [ProductImageInline]
