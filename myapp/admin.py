from decimal import Decimal

from django.contrib import admin
from .models import Topic, Course, Student, Order, Review

def decrease_price(modeladmin, request, queryset):
    for obj in queryset:
        obj.price = obj.price*Decimal(0.9)
        obj.save()

class CourseAdmin(admin.ModelAdmin):
    fields = [('title', 'topic'), ('price', 'num_reviews', 'for_everyone')]
    list_display = ('title', 'topic', 'price')
    actions = [decrease_price]

class OrderAdmin(admin.ModelAdmin):
    fields = ['courses', ('student', 'order_status', 'order_date')]
    list_display = ('id', 'student', 'order_status', 'order_date', 'total_items')

class CourseInline(admin.TabularInline):
    model = Course

class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'length')
    inlines = [CourseInline]

class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'level', 'list_of_registered_courses')

    def list_of_registered_courses(self, obj):
        courses = obj.registered_courses.all()
        list_courses = [c.title for c in courses]
        return list_courses

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'course', 'rating', 'comments', 'date')

admin.site.register(Topic, TopicAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
