from django.urls import path
from . import views


app_name = 'transaction_management'

urlpatterns = [
   
    #dashboard#
    path('dashboard', views.dashboard, name="transaction_dashboard"),
    
    #accounts#
    path('accounts', views.all_account),
    path('accounts/add', views.add_account),
    path('accounts/add/processing', views.add_account_processing),
    path('accounts/edit/<int:pk>', views.edit_account),
    path('accounts/view/<int:pk>', views.view_an_acount),
    path('accounts/edit/processing/<int:pk>', views.edit_account_processing),
    path('accounts/delete/<int:pk>', views.delete_an_account),
    
    #transfers#
    path('transfers', views.all_transfer),
    path('transfers/new', views.new_transfer),
    path('transfers/processing', views.new_transfer_processing),
    path('transfer/edit/<int:pk>', views.edit_transfer),
    path('transfer/delete/<int:pk>', views.delete_transfer),
    
]

