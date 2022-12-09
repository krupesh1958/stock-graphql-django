from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(User)
class studentadmin(admin.ModelAdmin):
    list_display = ['id','user_Name','user_Last_Name']

@admin.register(Total_stocks)
class totalstocks(admin.ModelAdmin):
    list_display = ['stock_Name','stock_Type']

@admin.register(User_wallet)
class suerwallet(admin.ModelAdmin):
    list_display = ['user_Wallet']

@admin.register(User_Buy)
class userwallet(admin.ModelAdmin):
    list_display = ['sto_Name']

@admin.register(User_Token)
class usertoken(admin.ModelAdmin):
    list_display = ['id']