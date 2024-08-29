from django.urls import path
from texnomart.views import CategoryListAPI, ProductListAPI, CreateCategoryView, DeleteCategoryView, \
    UpdateCategoryView, ProductDetailView, ProductUpdateView, ProductDeleteView, ProductAttribute, AttributeKeyListAPI, \
    AttributeValueListAPI, AllProductsView
from root import custam_token
urlpatterns = [
    path('', AllProductsView.as_view(), name='all_products'),
    #category urls
    path('categories/', CategoryListAPI.as_view(), name='categories'),
    path('category/<slug:category_slug>/', ProductListAPI.as_view(), name='products'),
    path('category/add/category/', CreateCategoryView.as_view(), name='add-category'),
    path('category/<slug:category_slug>/edit', UpdateCategoryView.as_view(), name='update-category'),
    path('category/<slug:category_slug>/delete', DeleteCategoryView.as_view(), name='delete-category'),
    #Product urls
    path('product/detail/<int:id>/', ProductDetailView.as_view()),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view()),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view()),
    #attribute urls
    path('attribute-key/', AttributeKeyListAPI.as_view()),
    path('attribute-value/', AttributeValueListAPI.as_view()),
    # #authentication
    path("login/", custam_token.LoginView.as_view(), name="user_login"),
    path("register/", custam_token.RegisterView.as_view(), name="user_register"),
    path("logout/", custam_token.LogoutView.as_view(), name="user_logout")
]