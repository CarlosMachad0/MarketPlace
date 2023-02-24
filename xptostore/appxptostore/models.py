from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
import os

import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('in_db',)

def filepath(request, filename):
    old_filename = filename
    timeNow = datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
    filename = "%s%s" % (timeNow, old_filename)
    return os.path.join('images/', filename)

# Mongo DB Models
class Utilizadores(AbstractUser):
    birthDate           = models.DateField()
    isAdmin             = models.BooleanField(default=False)
    isClient            = models.BooleanField(default=False)
    isComercialTypeOne  = models.BooleanField(default=False)
    isComercialTypeTwo  = models.BooleanField(default=False)
    isPartner           = models.BooleanField(default=False)
    
    @staticmethod
    def getTotalClientCount():
        return Utilizadores.objects.filter(isClient__in=[True]).count()
    
    @staticmethod
    def getTotalAdminCount():
        return Utilizadores.objects.filter(isAdmin__in=[True]).count()
    
    @staticmethod
    def getTotalComercialOneCount():
        return Utilizadores.objects.filter(isComercialTypeOne__in=[True]).count()
   
    @staticmethod
    def getTotalComercialTwoCount():
        return Utilizadores.objects.filter(isComercialTypeTwo__in=[True]).count()
    
    
class Category(models.Model):
    name                = models.CharField(max_length=100)
    description         = models.CharField(max_length=200)
    validated           = models.BooleanField(null=True,default=False) # validada pelo admin
    status              = models.BooleanField(null=True,default=True) # ativa / desativa
    
class Fornecedores(models.Model):
    name                = models.CharField(max_length=100)
    email               = models.EmailField(max_length=100)
    telephone           = models.CharField(max_length=17)
    adress              = models.CharField(max_length=100)
    nif                 = models.CharField(max_length=100)
    status              = models.BooleanField(null=True, default=True)  # ativo / desativo
    
class Product(models.Model):
    name                = models.CharField(max_length=100)
    quantity            = models.IntegerField(default=0)
    description         = models.CharField(max_length=255)
    price               = models.FloatField() # valor sem promoção
    promo_price         = models.FloatField() # valor definido com promoção
    image               = models.ImageField(upload_to=filepath, null=True, blank=True)
    validated           = models.BooleanField(null=True,default=False) # validado pelo admin
    status              = models.BooleanField(null=True,default=True) # ativo / desativo
    productOnwer        = models.IntegerField(default=0)
    procuctCategory     = models.IntegerField(default=0)
    productFornecedor   = models.IntegerField(default=0)

    # Converter objeto para dicionario
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': str(self.quantity),
            'description': self.description,
            'price': str(self.price),
            'promo_price': str(self.promo_price),
            'image': self.image.url,
            'validated': self.validated,
            'status': self.status,
            'productOnwer': self.productOnwer,
            'procuctCategory': self.procuctCategory,
            'productFornecedor': self.productFornecedor,
        }

    # Retorna nome do Utilizador que criou o produto
    def getProductOwnerFullName(self):
        productowner    = Product.objects.get(id= self.id)
        user            = Utilizadores.objects.get(id = productowner.productOnwer)
        return user.first_name + " " + user.last_name

    # Retorna categoria associada ao produto
    def getProductCategory(self):
        productCategory = Product.objects.get(id = self.id)
        category        = Category.objects.get(id= productCategory.procuctCategory)
        return category.name

    # Retorna o tipo de utilizador que criou o produto
    def getProductCreatorType(self):
        productowner    = Product.objects.get(id= self.id)
        user            = Utilizadores.objects.get(id = productowner.productOnwer)
        if user.isAdmin:
            return "Administrador"
        elif user.isClient:
            return "Cliente"
        elif user.isComercialTypeOne:
            return "Comercial Tipo 1"
        elif user.isComercialTypeTwo:
            return "Comercial Tipo 2"
        elif user.isPartner:
            return "Parceiro"
        

    def getProductProvider(self):
        product         = Product.objects.get(id = self.id)
        provider        = Fornecedores.objects.get(id= product.productFornecedor)
        return provider.name

    # Retorna o numero de produtos em bd
    @staticmethod
    def getTotalProductCount():
        return Product.objects.count()

# ------------------------------- // ------------------------------- // ------------------------------- #
# Postgres SQL Models

class Order(models.Model):
    client_id           = models.IntegerField()                                        
    client_address      = models.CharField(max_length=100)                                
    payment_info        = models.CharField(max_length=100)                                  
    order_data          = models.DateTimeField(null=True)                                   
    shipped_date        = models.DateTimeField(null=True)                                   
    shipped_status      = models.BooleanField(default=False)                                
    order_completed     = models.BooleanField(default=False)                               
    total_price         = models.FloatField()    
    isCanceled          = models.BooleanField(default=False) 
    
class OrderDetails(models.Model):
    orderID             = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id          = models.IntegerField()
    quantity            = models.IntegerField()
    price               = models.FloatField()     # Produto pode estar em desconto

class Faturas(models.Model):
    orderID             = models.ForeignKey(Order, on_delete=models.CASCADE)
    nr_fatura           = models.CharField(max_length=100, unique=True)
    data_fatura         = models.DateTimeField(null=True)  
    iva                 = models.IntegerField(default=23)
    isCanceled          = models.BooleanField(default=False)

