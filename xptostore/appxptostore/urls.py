from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    
    path('client-view/',views.clientView,name='client-view'),
    path('admin-view/',views.adminView,name='admin-view'),
    path('comercialOne-view/',views.comercialTypeOneView,name='comercialOne-view'),
    path('comercialTwo-view/',views.comercialTypeTwoView,name='comercialTwo-view'),
    path('partner-view/',views.partnerView,name='partner-view'),
    
    path('auth-login-view/',views.loginView,name='auth-login-view'),
    path('auth-register-view/',views.registerView,name='auth-register-view'),

    path('auth-register-user-type/',views.registerUserByTypeView,name='auth-register-user-type'),
    path('auth-register-user-submit/',views.registerUserByTypeSubmit,name='auth-register-user-submit'),

    path('edit-profile/<int:user_id>/',views.editProfileView,name='edit-profile'),
    path('edit-profile-submit/<int:user_id>/',views.editProfileSubmit,name='edit-profile-submit'),

    path('edit-password/<int:user_id>/',views.editPasswordView,name='edit-password'),
    path('edit-password-submit/<int:user_id>/',views.editPasswordSubmit,name='edit-password-submit'),

    path('create-product/',views.createProductView, name='create-product'),
    path('create-product-submit/', views.submitProduct, name='create-product-submit'), 
    path('edit-product/<int:product_id>/',views.editProductView,name='edit-product-view'),
    path('edit-product-submit/<int:product_id>/',views.editProductSubmit,name='edit-product-submit'),
    path('validate-product/<int:product_id>/',views.validateProduct,name='validate-product'),
    path('update-status-product/<int:product_id>/',views.updateStatusProduct,name='update-status-product'),
    path('delete-product/<int:product_id>/',views.deleteProduct,name='delete-product'),
    path('list-products/',views.listProducts,name='list-products'),


    path('partner-view/create-product/',views.partnerCreateProductView,name='partner-create-product-view'),
    path('partner-view/create-product-submit/',views.partnerCreateProductSubmit,name='partner-create-product-submit'),
    path('partner-view/list-partner/',views.listPartnercomercialTypetwoView,name='list-partner'),
    path('partner-view/partner-details/<int:partner_id>/',views.listPartnerProdcutdetails,name='partner-details'),

    path('partner-view/list-partner-typeOne/',views.listPartnercomercialTypeOneView,name='list-partner-typeOne'),
    path('partner-view/partner-details-typeOne/<int:partner_id>/',views.listPartnerProdcutdetailstypeone,name='partner-details-typeOne'),
 
    path('list-users/',views.listUsers,name='list-users'),
    path('delete-user/<int:user_id>/', views.deleteUser, name='delete-user'),
    path('activate-user/<int:user_id>/', views.activateUser, name='activate-user'),
    
    path('auth-login-autentication/',views.loginAutentication,name='auth-login-autentication'),
    path('auth-client-register-submit/',views.registerClientSubmit,name='auth-client-register-submit'),
    path('auth-logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='auth-logout'),

    path('list-categorys/',views.listCategorys,name='list-categorys'),
    path('create-categorys/',views.createCategory,name='create-categorys'),
    path('create-category-submit/', views.createCategorySubmit, name='create-category-submit'),
    path('validate-category/<int:category_id>/',views.validateCategory,name='validate-category'),
    path('update-status-category/<int:category_id>/',views.updateStatusCategory,name='update-status-category'),
    path('delete-category/<int:category_id>/',views.deleteCategory,name='delete-category'),

    path('create-provider/',views.createProvider,name='create-provider'),
    path('create-provider-submit/', views.createproviderSubmit, name='create-provider-submit'),
    path('list-provider/', views.listProviders, name='list-provider'),
    path('update-provider-status/<int:provider_id>/',views.updateProviderStatus,name='update-provider-status'),
    path('delete-provider/<int:provider_id>/',views.deleteProvider,name='delete-provider'),
    
    
    path('cart-view/',views.cartView,name='cart-view'),
    path('addProductToCart/<int:product_id>/',views.addProductToCart,name='addProductToCart'),
    path('remove_from_cart/<int:product_id>/',views.remove_from_cart,name='remove_from_cart'),
    path('update_cart/<int:product_id>/',views.update_cart,name='update_cart'),
    path('checkout-cart/',views.checkoutCart,name='checkout-cart'),
    path('submitEncomenda/',views.submitEncomenda,name='submitEncomenda'),

    path('client-view/pendingClientOrders/',views.pendingClientOrders,name='pendingClientOrders'),
    path('client-view/concludedClientOrders/',views.concludedClientOrders,name='concludedClientOrders'),
    path('client-view/order-details/<int:order_id>/',views.orderDetails,name='order-details'),
    path('client-view/orderCancel/<int:order_id>/',views.orderCancel,name='order-cancel'),


    path('comercialOne-view/order-details/<int:order_id>/',views.orderDetailscomercialTypeOne,name='comercialOne-order-details'),
    path('comercialOne-view/update-shipped-status/<int:order_id>/',views.setOrderToShipped,name='update-shipped-status'),
    path('comercialOne-view/update-completed-order-status/<int:order_id>/',views.setOrderDelivered,name='update-completed-order-status'),
    
    path('comercialTwo-view/order-details/<int:order_id>/',views.orderDetailscomercialTypeTwo,name='comercialTwo-order-details'),
    path('comercialTwo-view/order-details/',views.listcomercialsTypeTwo,name='list-comercials'),
    path('comercialTwo-view/list-Comercials-details/<int:comercial_id>/',views.listDetailscomercialsTypeTwo,name='comercialTwo-details'),


    path('export/productsJSON/', views.exportproductsJSON, name='exportproductsJSON'),
    path('export/productsXML/', views.exportproductsXML, name='exportproductsXML'),
    path('export/faturaXML/<int:order_id>/', views.exportfatura, name='exportfatura'),



    path('permission_not_granted/',views.permission_not_granted, name='permission_not_granted'),
] +  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
