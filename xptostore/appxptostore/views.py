import json
import xml.etree.ElementTree as ET
from django.db import models
from django.db import connections
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from psycopg2 import ProgrammingError
from django.contrib.auth import update_session_auth_hash
from .forms import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.http import HttpResponse
from .models import *

# Verificação de tipo de utilizador 
def check_Admin(user):
    return user.isAdmin

def check_Client(user):
    return user.isClient

def check_ComercialTypeOne(user):
    return user.isComercialTypeOne

def check_ComercialTypeTwo(user):
    return user.isComercialTypeTwo

def check_Partner(user):
    return user.isPartner

def check_can_edit_product(user):
    return user.isAdmin or user.isComercialTypeOne or user.isComercialTypeTwo

def check_can_list_product(user):
    return user.isAdmin or user.isComercialTypeOne or user.isComercialTypeTwo

def chech_if_can_create_product(user):
    return user.isAdmin or user.isComercialTypeOne

def check_can_list_edit_create_category(user):
    return user.isAdmin or user.isComercialTypeOne or user.isComercialTypeTwo

def check_can_export_invoice(user):
    return user.isClient or user.isComercialTypeOne or user.isComercialTypeTwo

def permission_not_granted(request):
    context = {}
    return render(request, 'error-pages/permission-error.html', context)

# ------------------------------------------------------------------------------------------

# Renderizar página de index
def index(request):
    cursor = connections['comercialTwo'].cursor()

    cursor.execute("SELECT * FROM getlistBestProduct")
    listBestProducts=cursor.fetchall()

    product_ids = [tuple[0] for tuple in listBestProducts]

    # Filter the products by the list of IDs
    listProducts = Product.objects.filter(validated__in=[True], status__in=[True], id__in=product_ids).all()
    listCategories = Category.objects.filter(validated__in=[True], status__in=[True]).all()

    categoryProducts = Product.objects.filter(validated__in=[True],status__in=[True]).order_by('-id')[:4]
    if request.method == 'POST':
        cat = request.POST['categoria']
        if cat == "Selecione a categoria":
            categoryProducts = Product.objects.filter(validated__in=[True],status__in=[True]).order_by('-id')[:4]
        else:
            categoryProducts = Product.objects.filter(validated__in=[True],status__in=[True],procuctCategory=cat)

    context = {
        'listIndexProduct': Product.objects.filter(validated__in = [True], status__in = [True]).all(),
        'bestProducts': listProducts,
        'listCategories': listCategories,
        'listOfProductsByCategory': categoryProducts
    }
    return render(request, 'index.html', context)

# Renderizar página de autenticação
def loginView(request):
    context = {}
    return render(request, 'autentication/auth-login.html', context)

#Pagina Parceiros
@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def listPartnercomercialTypeOneView(request):
    
    listPartner = Utilizadores.objects.filter( isPartner__in=[True]).all()
    context={
        'listPartner': listPartner
    }
    return render(request, 'comercialTypeOne/list-partner.html',context)

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def listPartnerProdcutdetailstypeone(request,partner_id):
    cursor = connections['comercialTwo'].cursor()
    listproduct = Product.objects.filter(productOnwer=partner_id).all()
    partner_name = Utilizadores.objects.filter(id=partner_id).all()
    listTimesSell=[]
    for p in listproduct:
        print("p",p.id)            
        cursor.execute("SELECT * FROM getPartnerProductSells(%s)", [str(p.id)])
        productTimeSell = cursor.fetchone() 
        if productTimeSell is not None:
            product = Product.objects.filter(productOnwer=partner_id,id=productTimeSell[0]).all()
            partnerProductdata  = {
                'name':product[0].name,
                'quantity': product[0].quantity,
                'description':product[0].description,
                'price':product[0].price,
                'numeroVendas':productTimeSell[1]

            }
            listTimesSell.append(partnerProductdata) 
        else:
            product = Product.objects.filter(productOnwer=partner_id,id=p.id).all()    
            partnerProductdata  = {
                'name':product[0].name,
                'quantity': product[0].quantity,
                'description':product[0].description,
                'price':product[0].price,
                'numeroVendas':"Sem Vendas"
            }
            listTimesSell.append(partnerProductdata) 
    cursor.close()

    context={
         'listproduct': listTimesSell,
         'partner_name':partner_name[0]
    }
    return render(request, 'comercialTypeOne/partner-detail.html',context)






# Renderizar página comercial tipo 1
@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def comercialTypeOneView(request):
    cursor = connections['comercialOne'].cursor()
    x=0
    cursor.execute("SELECT * FROM allOrdersOrder")
    allorders=cursor.fetchall()
    
    cursor.execute("SELECT * FROM allOrdersOrderCanceled")
    allordersCanceled=cursor.fetchall()

    cursor.execute("SELECT * FROM getBestProduct")
    productBest = cursor.fetchone()
    if productBest is not None:
        bestP=Product.objects.filter(id=productBest[0])
    else:
        x=1    
    
    cursor.execute("SELECT * FROM getWorstProduct")
    productWorst= cursor.fetchone()
    if productWorst is not None:
        worstP=Product.objects.filter(id=productWorst[0])
    else:
        x=1

    cursor.execute("SELECT * FROM getBestClient")
    bestClient= cursor.fetchone()
    if bestClient is not None:
        clientB=Utilizadores.objects.filter(id=bestClient[0])
    else:
        x=1

    cursor.execute("SELECT * FROM getTotalProfit")
    totalProfit= cursor.fetchone()

    cursor.close()
    client=[]
    clientCanceled=[]
   
    
    
    # Encomendas não canceladas 
    for order in allorders:
        user=Utilizadores.objects.filter(id=order[1])
        clientdata  = {
            'id':order[0],
            'client_name': user[0].first_name+" "+user[0].last_name,
            'client_address':order[2],
            'payment_info':order[3],
            'order_data':order[4],
            'shipped_data':order[5],
            'shipped_status':order[6],
            'order_completed':order[7],
            'total_price':order[8]
        }
        client.append(clientdata)
    # Encomendas Canceladas
    for order in allordersCanceled:
        user=Utilizadores.objects.filter(id=order[1])
        clientdatacanceled  = {
            'id':order[0],
            'client_name': user[0].first_name+" "+user[0].last_name,
            'client_address':order[2],
            'payment_info':order[3],
            'order_data':order[4],
            'shipped_data':order[5],
            'shipped_status':order[6],
            'order_completed':order[7],
            'total_price':order[8]
        }
        clientCanceled.append(clientdatacanceled)
    print(x)
    if x==1:
        context = {
            'clientdata':client,
            'clientdatacanceled':clientCanceled,
            'bestProduct':"sem produto",
            'worstProduct':"sem produto",
            'bestClient':"sem cliente",
            'profit':totalProfit
        }
    else:   
        context = {
            'clientdata':client,
            'clientdatacanceled':clientCanceled,
            'bestProduct':bestP[0].name,
            'worstProduct':worstP[0].name,
            'bestClient':clientB[0].first_name+" "+clientB[0].last_name,
            'profit':totalProfit
        }
    return render(request, 'comercialTypeOne/comercialOne.html', context)

# Renderizar página comercial tipo 2
@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeTwo, login_url='/appxptostore/permission_not_granted/')
def comercialTypeTwoView(request):
    cursor = connections['comercialOne'].cursor()
    cursor.execute("SELECT * FROM allOrdersOrder")
    allorders=cursor.fetchall()
    
    cursor.execute("SELECT * FROM allOrdersOrderCanceled")
    allordersCanceled=cursor.fetchall()
    
    cursor.execute("SELECT * FROM lastHourOrders")
    lastHour=cursor.fetchone()
   
    cursor.execute("SELECT * FROM todayOrders")
    todayOrders=cursor.fetchone()

    cursor.execute("SELECT * FROM lastWeekOrders")
    lastWeekOrder=cursor.fetchone()

    cursor.execute("SELECT * FROM lastMonthOrders")
    lastMonthOrder=cursor.fetchone()   
    startDate=''
    endDate=''
    nOrderInRangecontext=''
    totalPriceRangecontext=''
    nOrderInRange=[]
    
    if request.method == 'POST':
        startDate = request.POST['startDate']
        endDate=request.POST['endDate']
        print("data",startDate,endDate)
        if startDate != '' and endDate != '':
            cursor.execute("SELECT * FROM GetNOrdersDataRange(%s,%s)", (startDate,endDate))
            nOrderInRange = cursor.fetchall()
    
        if nOrderInRange!=[]:
            nOrderInRangecontext= "Encomendas " + str(nOrderInRange[0][0])
            totalPriceRangecontext=" Lucro "+str(nOrderInRange[0][1])+ " €"
        else:
            nOrderInRangecontext= "Sem Encomendas"
            totalPriceRangecontext=""
      
  

    cursor.close()
    client=[]
    clientCanceled=[]
    
    # Encomendas não canceladas 
    for order in allorders:
        user=Utilizadores.objects.filter(id=order[1])
        clientdata  = {
            'id':order[0],
            'client_name': user[0].first_name+" "+user[0].last_name,
            'client_address':order[2],
            'payment_info':order[3],
            'order_data':order[4],
            'shipped_data':order[5],
            'shipped_status':order[6],
            'order_completed':order[7],
            'total_price':order[8]
        }
        client.append(clientdata)
    # Encomendas Canceladas
    for order in allordersCanceled:
        user=Utilizadores.objects.filter(id=order[1])
        clientdatacanceled  = {
            'id':order[0],
            'client_name': user[0].first_name+" "+user[0].last_name,
            'client_address':order[2],
            'payment_info':order[3],
            'order_data':order[4],
            'shipped_data':order[5],
            'shipped_status':order[6],
            'order_completed':order[7],
            'total_price':order[8]
        }
        clientCanceled.append(clientdatacanceled)

    context = {
        'clientdata':client,
        'clientdatacanceled':clientCanceled,
        'lastHour':lastHour,
        'todayOrders':todayOrders,
        'lastWeekOrder':lastWeekOrder,
        'lastMonthOrder':lastMonthOrder,
        'startDate':startDate,
        'endDate':endDate,
        'nOrderInRange':nOrderInRangecontext,
        'totalPriceRange':totalPriceRangecontext

        }
    return render(request, 'comercialTypeTwo/comercialtwo.html', context)


#Pagina Parceiros
@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeTwo, login_url='/appxptostore/permission_not_granted/')
def listPartnercomercialTypetwoView(request):
    
    listPartner = Utilizadores.objects.filter( isPartner__in=[True]).all()
    
    context={
        'listPartner': listPartner
    }
    return render(request, 'comercialTypeTwo/list-partner.html',context)

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeTwo, login_url='/appxptostore/permission_not_granted/')
def listPartnerProdcutdetails(request,partner_id):
    cursor = connections['comercialTwo'].cursor()
    listproduct = Product.objects.filter(productOnwer=partner_id).all()
    partner_name = Utilizadores.objects.filter(id=partner_id).all()
    listTimesSell=[]
    for p in listproduct:
        print("p",p.id)            
        cursor.execute("SELECT * FROM getPartnerProductSells(%s)", [str(p.id)])
        print("1")
        productTimeSell = cursor.fetchone() 
        print("2")
        if productTimeSell is not None:
            product = Product.objects.filter(productOnwer=partner_id,id=productTimeSell[0]).all()
            partnerProductdata  = {
                'name':product[0].name,
                'quantity': product[0].quantity,
                'description':product[0].description,
                'price':product[0].price,
                'numeroVendas':productTimeSell[1]

            }
            listTimesSell.append(partnerProductdata) 
        else:
            product = Product.objects.filter(productOnwer=partner_id,id=p.id).all()    
            partnerProductdata  = {
                'name':product[0].name,
                'quantity': product[0].quantity,
                'description':product[0].description,
                'price':product[0].price,
                'numeroVendas':"Sem Vendas"
            }
            listTimesSell.append(partnerProductdata) 
    cursor.close()

    context={
         'listproduct': listTimesSell,
         'partner_name':partner_name[0]
    }
    return render(request, 'comercialTypeTwo/partner-detail.html',context)



# Renderizar página de registro de utilizadores
def registerView(request):
    context = {}
    return render(request, 'autentication/auth-register.html', context)

# Renderizar página de registro de produtos
@user_passes_test(chech_if_can_create_product, login_url='/appxptostore/permission_not_granted/')
def createProductView(request):
    context = { 
        'categorys': Category.objects.all().filter(status__in= [True],validated__in = [True]),
        'providers': Fornecedores.objects.all().filter(status__in= [True])
    }
    return render(request, 'products/create-product.html', context)

# Validar autenticação + permissões para aceder à página de Cliente
@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Client, login_url='/appxptostore/permission_not_granted/')
def clientView(request):
    cursor = connections['clientUser'].cursor()

    cursor.execute("SELECT * FROM getNOrderByclient(%s)", [str(request.user.id)])
    nOrders = cursor.fetchall()

    cursor.execute("SELECT * FROM getNweekOrderByClient(%s)", [str(request.user.id)])
    nOrdersthisweek = cursor.fetchall()

    cursor.execute("SELECT * FROM getOrderMostExpensiveByclient(%s)", [str(request.user.id)])
    orderexp = cursor.fetchone()

    cursor.execute("SELECT * FROM getTotalspentByclient(%s)", [str(request.user.id)])
    vlrtotal = cursor.fetchone()

    cursor.close()

    context = {
        'totalOrder': nOrders,
        'nOrdersthisweek':nOrdersthisweek,
        'orderexp': orderexp,
        'vlrtotal':vlrtotal
    }
    return render(request, 'client/cliente.html', context)

# Validar autenticação + permissões para aceder à página de Administrador
@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Admin, login_url='/appxptostore/permission_not_granted/')
def adminView(request):
    context = {
        'clientsCount' : Utilizadores.getTotalClientCount(),
        'adminCount' : Utilizadores.getTotalAdminCount(),
        'comercialOneCount' : Utilizadores.getTotalComercialOneCount(),
        'comecialTwoCount' : Utilizadores.getTotalComercialTwoCount(),
        'productcount' : Product.getTotalProductCount(),
    }
    return render(request, 'administrator/administrator.html', context)

# Autenticação de Utilizadores e redirecionamento dos mesmos
def loginAutentication(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None and user.isAdmin:
                login(request, user)
                return redirect('/appxptostore/admin-view/')
            elif user is not None and user.isClient:
                login(request, user)
                return redirect('/appxptostore/client-view/')
            elif user is not None and user.isComercialTypeOne:
                login(request, user)
                return redirect('/appxptostore/comercialOne-view/')
            elif user is not None and user.isComercialTypeTwo:
                login(request, user)
                return redirect('/appxptostore/comercialTwo-view/')
            elif user is not None and user.isPartner:
                login(request, user)
                return redirect('/appxptostore/partner-view/')
            else:
                messages.warning(request,"Credenciais inválidas / Conta desativa. Contacte o suporte se necessário.")
        else:
            messages.warning(request,"Preencha os campos corretamente")
    return render(request, 'autentication/auth-login.html', {'form': form})

# Criação de Utilizador (Cliente)
def registerClientSubmit(request):
    if request.method == 'POST':
        form = RegisterClientForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.isClient = True
            form.save()
            messages.success(request,"Cliente criado com sucesso")
            return redirect('/appxptostore/auth-login-view/')
        else:
            print(form.errors.as_data())
            messages.warning(request,"Preencha os campos corretamente")
    else:
        form = RegisterClientForm()
    return render(request, 'autentication/auth-register.html', {'form': form })

def registerUserByTypeView(request):
    options = [
        {'value': 'isAdmin',            'label': 'Administrador'}, 
        {'value': 'isClient',           'label': 'Cliente'}, 
        {'value': 'isComercialTypeOne', 'label': 'Comercial Tipo Um'},
        {'value': 'isComercialTypeTwo', 'label': 'Comercial Tipo Dois'},
        {'value': 'isPartner',          'label': 'Parceiro'}
    ]
    return render(request, 'autentication/auth-register-user-bytype.html', { 'options' :  options})

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Admin, login_url='/appxptostore/permission_not_granted/')
def registerUserByTypeSubmit(request):
    if request.method == 'POST':
        form = RegisterClientForm(request.POST)
        if form.is_valid():
            
            selected_option = request.POST['select']

            # Validar a opção selecionada no menu
            if selected_option == 'Escolha o tipo de Utilizador':
                messages.warning(request,"Tem de escolher um tipo de utilizador")
                return redirect('/appxptostore/auth-register-user-type/')
            
            # Guardar temporariamente os valores introduzidos no form
            User = form.save(commit=False)

            # Aceder ao atributo do objeto diretamente e alterar o seu valor
            setattr(User, selected_option, True)

            # Commit final após alteração do atributo
            form.save()
            messages.success(request,"Utilizador criado com sucesso")
        else:
            messages.warning(request,"Preencha todo os dados corretamente")
            print(form.errors.as_data())
    else:
        form = RegisterClientForm()
        print(form.errors.as_data())
    return redirect('/appxptostore/auth-register-user-type/')

@login_required(login_url=reverse_lazy("auth-login-view"))
def listProducts(request):
    context = { 'listProducts': Product.objects.all() }
    return render(request, 'products/list-products.html', context)

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_list_product, login_url='/appxptostore/permission_not_granted/')
def listCurrentUserProducts(request):
    filteredProduct = Product.objects.filter(id__in = request.user.id).all()
    context = {
        'listProducts': filteredProduct
    }
    return render(request, 'products/list-products.html', context)

@login_required(login_url=reverse_lazy("auth-login-view"))
def listUsers(request):
    options = [
        {'value': 'isAdmin',            'label': 'Administrador'}, 
        {'value': 'isClient',           'label': 'Cliente'}, 
        {'value': 'isComercialTypeOne', 'label': 'Comercial Tipo Um'},
        {'value': 'isComercialTypeTwo', 'label': 'Comercial Tipo Dois'},
        {'value': 'isPartner',          'label': 'Parceiro'}
    ]
  
    if request.method == 'POST':
        role = request.POST['role']
        print("role",role)
        if role=='isAdmin':
             users = Utilizadores.objects.filter(isAdmin__in=[True])
        elif role=='isClient':
             users = Utilizadores.objects.filter(isClient__in=[True])
        elif role=='isComercialTypeOne':
             users = Utilizadores.objects.filter(isComercialTypeOne__in=[True])
        elif role=='isComercialTypeTwo':
             users = Utilizadores.objects.filter(isComercialTypeTwo__in=[True])
        elif role=='isPartner':
             users = Utilizadores.objects.filter(isPartner__in=[True])
        else:
            users=Utilizadores.objects.all()

        context = {
            'users': users,
            'options' :  options,
        }
        return render(request, 'administrator/list-users.html', context)
    else:
        context = {
            'users': Utilizadores.objects.all(),
            'options' :  options
        }
        return render(request, 'administrator/list-users.html', context)
    
    
 

@login_required(login_url=reverse_lazy("auth-login-view"))
def activateUser(request, user_id):
    user = Utilizadores.objects.filter(id=user_id)
    if request.method == 'POST':
        if user[0].is_active is True:
            user.update(is_active=False)
        elif user[0].is_active is False:
            user.update(is_active=True)
    return redirect('/appxptostore/list-users/')

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Admin, login_url='/appxptostore/permission_not_granted/')
def deleteUser(request, user_id):

    # Caso o user se tentar eliminar a si próprio
    if request.user.id == user_id:
        messages.warning(request,"Não te podes eliminar a ti próprio")
        return redirect('/appxptostore/list-users/')

    user = Utilizadores.objects.get(id=user_id)
    user.delete()
    messages.success(request,"Utilizador eliminado com sucesso")
    return redirect('/appxptostore/list-users/')

# Editar perfil 
@login_required(login_url=reverse_lazy("auth-login-view"))
def editProfileView(request,user_id):
    if request.user.id != user_id:
        return redirect('/appxptostore/permission_not_granted/')
    return render(request, 'generic-views/edit-profile.html', None) 

@login_required(login_url=reverse_lazy("auth-login-view"))
def editProfileSubmit(request,user_id):
    user = Utilizadores.objects.get(id= user_id)

    # Validar se o user do request é o autenticado
    if request.user.id != user_id:
        return redirect('/appxptostore/permission_not_granted/')

    if request.method == "POST":
        user.username       = request.POST.get('username')
        user.first_name     = request.POST.get('first_name')
        user.last_name      = request.POST.get('last_name')
        user.email          = request.POST.get('email')
        user.birthDate      = request.POST.get('birthDate')
        user.save()
        messages.success(request, "Perfil atualizado com sucesso")
    else:
        messages.warning(request, "Erro ao atualizar perfil")
    return redirect('/appxptostore/edit-profile/'+ str(user_id) + "/")

@login_required(login_url=reverse_lazy("auth-login-view"))
def editPasswordView(request,user_id):

    # Validar se o user do request é o autenticado
    if request.user.id != user_id:
        return redirect('/appxptostore/permission_not_granted/')
    return render(request, 'generic-views/edit-password.html', None) 

@login_required(login_url=reverse_lazy("auth-login-view"))
def editPasswordSubmit(request,user_id):
    user = Utilizadores.objects.get(id= user_id)

    # Validar se o user do request é o autenticado
    if request.user.id != user_id:
        return redirect('/appxptostore/permission_not_granted/')

    if request.method == "POST":
        new_password    = request.POST.get('password1')
        conf_password   = request.POST.get('password2')

        if new_password == conf_password:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # De modo a não ser preciso autenticar de novo
            messages.success(request, "Password atualizada com sucesso")
        else:
            messages.warning(request, "Passwords têm de ser iguais")
    else:
        messages.warning(request, "Erro ao atualizar perfil")
    return redirect('/appxptostore/edit-password/'+ str(user_id) + "/")

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def validateProduct(request, product_id):
    product = Product.objects.filter(id=product_id)
    if request.method == 'POST':
        if product[0].validated is True:
            product.update(validated=False)
        elif product[0].validated is False:
            product.update(validated=True)
    return redirect('/appxptostore/list-products/')

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def updateStatusProduct(request, product_id):
    product = Product.objects.filter(id=product_id)
    if request.method == 'POST':
        if product[0].status is True:
            product.update(status=False)
        elif product[0].status is False:
            product.update(status=True)
    return redirect('/appxptostore/list-products/')

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_edit_product, login_url='/appxptostore/permission_not_granted/')
def editProductView(request,product_id):
    context = {
        'product': Product.objects.get(id= product_id),
        'categorys': Category.objects.all().filter(status__in= [True],validated__in = [True]),
        'providers': Fornecedores.objects.all().filter(status__in= [True]),
    }
    return render(request, 'products/edit-product.html', context)
    
@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_edit_product, login_url='/appxptostore/permission_not_granted/')
def editProductSubmit(request,product_id):
    product     = Product.objects.get(id=product_id)

    if request.method == "POST":
        form = CreateProductForm(request.POST)
        
        if form.is_valid():

            if len(request.FILES) != 0:
                if len(product.image) > 0:
                    os.remove(product.image.path)
                product.image       = request.FILES['image']

            selected_option         = request.POST['select']
            selectedProvider_option = request.POST['selectfornecedor']

            if selected_option == 'Escolha a categoria':
                messages.warning(request, "Tem de escolher uma categoria")
                return redirect('/appxptostore/create-product/')

            if selectedProvider_option == 'Escolha o fornecedor':
                messages.warning(request, "Tem de escolher um fornecedor")
                return redirect('/appxptostore/create-product/')

            product.name                = form.cleaned_data.get('name')
            product.quantity            = form.cleaned_data.get('quantity')
            product.description         = form.cleaned_data.get('description')
            product.price               = form.cleaned_data.get('price')
            product.promo_price         = form.cleaned_data.get('promo_price')
            product.procuctCategory     = selected_option
            product.productFornecedor   = selectedProvider_option

            # Atualizar produto
            # product._state.using = 'readPerm'
            product.save()
            
            messages.success(request, "Produto atualizado com sucesso")
            return redirect('/appxptostore/edit-product/' + str(product_id) + "/")
        else:
            messages.warning(request, "Preencha os campos corretamente")
    else:
        messages.warning(request, "Erro ao atualizar o produto")
        return redirect('/appxptostore/edit-product/' + str(product_id) + "/")
    return render(request, 'products/edit-product.html', None)


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def deleteProduct(request, product_id):
    product = Product.objects.get(id=product_id)
    # Eliminar imagem
    if len(product.image) > 0:
        os.remove(product.image.path)
    product.delete()
    return redirect('/appxptostore/list-products/')

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(chech_if_can_create_product, login_url='/appxptostore/permission_not_granted/')
def submitProduct(request):
    if request.method == "POST":
        form = CreateProductForm(request.POST)
        if form.is_valid():
            Produtos                = form.save(commit=False)
            Produtos.name           = form.cleaned_data.get('name')
            Produtos.quantity       = form.cleaned_data.get('quantity')
            Produtos.description    = form.cleaned_data.get('description')
            Produtos.price          = form.cleaned_data.get('price')
            Produtos.promo_price    = form.cleaned_data.get('promo_price')

            if len(request.FILES) != 0:
                Produtos.image = request.FILES['image']

            selectedCategory_option = request.POST['select']
            selectedProvider_option = request.POST['selectfornecedor']
            
            # Validar a opção selecionada no menu
            if selectedCategory_option == 'Escolha a categoria':
                messages.warning(request, "Tem de escolher uma categoria")
                return redirect('/appxptostore/create-product/')

            # Validar a opção selecionada no menu
            if selectedProvider_option == 'Escolha o fornecedor':
                messages.warning(request, "Tem de escolher um fornecedor")
                return redirect('/appxptostore/create-product/')

            # Guardar produto no mongodb
            Produtos.productOnwer       = request.user.id
            Produtos.procuctCategory    = selectedCategory_option
            Produtos.productFornecedor  = selectedProvider_option
            Produtos.save()

            messages.success(request,"Produto criado com sucesso")
        else:
            print(form.errors.as_data())
            messages.warning(request,"Preencha os campos corretamente")
            return redirect('/appxptostore/create-product/')
    else:
        form = RegisterClientForm()
        print(form.errors.as_data())
    return redirect('/appxptostore/create-product/')

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_list_edit_create_category, login_url='/appxptostore/permission_not_granted/')
def listCategorys(request):
    context = {
        'categorys': Category.objects.all()
    }
    return render(request, 'category/list-category.html', context)

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_list_edit_create_category, login_url='/appxptostore/permission_not_granted/')
def createCategory(request):
    context = {}
    return render(request, 'category/create-category.html', context)

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_list_edit_create_category, login_url='/appxptostore/permission_not_granted/')
def deleteCategory(request,category_id):
    category = Category.objects.get(id=category_id)
    category.delete()
    messages.success(request,"Categoria eliminada com sucesso")
    return redirect('/appxptostore/list-categorys/')


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_list_edit_create_category, login_url='/appxptostore/permission_not_granted/')
def createCategorySubmit(request):
    if request.method == 'POST':
        category = CreateCategoryForm(request.POST)
        if category.is_valid():
            category.save()
            messages.success(request, "Categoria criada com sucesso")
            return redirect('/appxptostore/create-categorys/')
        else:
            print(category.errors.as_data())
            messages.warning(request, "Preencha os campos corretamente")
    else:
        messages.warning(request, "Erro ao criar categoria")
    return redirect('/appxptostore/create-categorys/')

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def validateCategory(request, category_id):
    category = Category.objects.filter(id=category_id)
    if request.method == 'POST':
        if category[0].validated is True:
            category.update(validated=False)
        elif category[0].validated is False:
            category.update(validated=True)
    return redirect('/appxptostore/list-categorys/')

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def updateStatusCategory(request, category_id):
    category = Category.objects.filter(id=category_id)
    if request.method == 'POST':
        if category[0].status is True:
            category.update(status=False)
        elif category[0].status is False:
            category.update(status=True)
    return redirect('/appxptostore/list-categorys/')


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_list_edit_create_category, login_url='/appxptostore/permission_not_granted/')
def createProvider(request):
    context = {}
    return render(request, 'providers/create-provider.html', context)


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_list_edit_create_category, login_url='/appxptostore/permission_not_granted/')
def createproviderSubmit(request):
    if request.method == 'POST':
        category = RegisterProviderForm(request.POST)
        if category.is_valid():
            category.save()
            messages.success(request, "Fornecedor criado com sucesso")
            return redirect('/appxptostore/create-provider')
        else:
            print(category.errors.as_data())
            messages.warning(request, "Preencha os campos corretamente")
    else:
        messages.warning(request, "Erro ao criar Fornecedor")
    return redirect('/appxptostore/create-provider/')


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_list_edit_create_category, login_url='/appxptostore/permission_not_granted/')
def listProviders(request):
    context = {
        'providers': Fornecedores.objects.all()
    }
    return render(request, 'providers/list-provider.html', context)

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def deleteProvider(request,provider_id):
    provider = Fornecedores.objects.get(id=provider_id)
    provider.delete()
    messages.success(request,"Fornecedor eliminado com sucesso")
    return redirect('/appxptostore/list-provider/')


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def updateProviderStatus(request, provider_id):
    provider = Fornecedores.objects.filter(id=provider_id)
    if request.method == 'POST':
        if provider[0].status is True:
            provider.update(status=False)
        elif provider[0].status is False:
            provider.update(status=True)
    return redirect('/appxptostore/list-provider/')

# Funcionalidades Carrinho de Compras

def cartView(request):
    # Display the shopping cart
    cart = request.session.get('cart', {})
    products = [item['product'] for item in cart.values()]      # Get the product objects

    totalPrice = 0
    for product in products:
        productQt = float(product['price'])* int(product['productQuantity'])
        totalPrice += productQt

    context = {
        'products': products,
        'totalPrice': totalPrice
    }
    return render(request, 'carrinho/list-cart.html', context)

def getCartTotalPrice(request):
    cart = request.session.get('cart', {})
    products = [item['product'] for item in cart.values()]      # Get the product objects

    totalPrice = 0
    for product in products:
        productQt = float(product['price'])* int(product['productQuantity'])
        totalPrice += productQt
    return totalPrice

def addProductToCart(request,product_id):
    # Add the product to the shopping cart
    quantity = request.POST['quantity']
    if quantity == '' or quantity == '0': quantity = 1

    product = get_object_or_404(Product, pk=product_id)

    cart = request.session.get('cart', {})

    if product_id in cart:
        print("PRODUTO JÁ EXISTE NO CARRINHO")
        # Caso já exista no carrinho apenas atualiza a quantidade e o total
        currentQT = cart[str(product_id)].get('product').get('productQuantity') 
        currentTotal = cart[str(product_id)].get('product').get('productTotal') 
        cart[str(product_id)]['product']['productQuantity'] = int(currentQT) + int(quantity)
        cart[str(product_id)]['product']['productTotal'] = int(currentTotal) * int(quantity)
    else: 
        print("PRODUTO NOVO NO CARRINHO")
        if product.promo_price > 0 and request.user.is_authenticated: 
            price = product.promo_price 
        else: price = product.price

        # Senão existir adiciona ao carrinho
        product_dict = {
            'id': product.id,
            'name': product.name,
            'price': str(price),   
            'image': product.image.url,               
            'validated' : product.validated,          
            'status': product.status,              
            'productOnwer': product.productOnwer,        
            'procuctCategory': product.procuctCategory,     
            'productFornecedor': product.productFornecedor,
            'productQuantity': quantity,
            'productTotal': str(price * float(quantity)),
        }
        cart[product_id] = {'product': product_dict }
    request.session['cart'] = cart
    return redirect('/appxptostore/cart-view/')

def remove_from_cart(request, product_id):
    # Remove a product from the shopping cart
    cart = request.session.get('cart', {})
    if cart[str(product_id)]:
        del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('/appxptostore/cart-view/')

def update_cart(request,product_id):
    cart = request.session.get('cart', {})

    quantity = request.POST['newQuantity']
    if quantity == '' or quantity == '0': quantity = 1

    if cart[str(product_id)]:
        # Se existir no carrinho atualizamos a sua quantidade  e o total
        cart[str(product_id)]['product']['productQuantity'] = quantity
        price = cart[str(product_id)].get('product').get('price') 
        cart[str(product_id)]['product']['productTotal'] = float(price) * float(quantity)
    request.session['cart'] = cart
    return redirect('/appxptostore/cart-view/')


# Exportar dados para JSON / XML

def exportproductsJSON(request):
    products = Product.objects.all()

    product_list = [product.to_dict() for product in products]

    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="products.json"'

    for product in product_list:
        json.dump(product, response)
        response.write('\n')

    return response

def exportproductsXML(request):
    products = Product.objects.all()

    root = ET.Element('products')

    for product in products:
        product_element = ET.SubElement(root, 'product')
        ET.SubElement(product_element, 'id').text                   = str(product.id)
        ET.SubElement(product_element, 'name').text                 = product.name
        ET.SubElement(product_element, 'quantity').text             = str(product.price)
        ET.SubElement(product_element, 'description').text          = product.description
        ET.SubElement(product_element, 'price').text                = str(product.price)
        ET.SubElement(product_element, 'promo_price').text          = str(product.promo_price)
        ET.SubElement(product_element, 'image').text                = product.image.url
        ET.SubElement(product_element, 'validated').text            = str(product.validated)
        ET.SubElement(product_element, 'status').text               = str(product.status)
        ET.SubElement(product_element, 'productOnwer').text         = str(product.productOnwer)
        ET.SubElement(product_element, 'procuctCategory').text      = str(product.procuctCategory)
        ET.SubElement(product_element, 'productFornecedor').text    = str(product.productFornecedor)

    data = ET.tostring(root, encoding='utf-8')

    response = HttpResponse(data, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="products.xml"'

    return response

@login_required(login_url=reverse_lazy("auth-login-view"))
def checkoutCart(request):
    context = {}  
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request,"Tem de ter produtos no carrinho")
        return redirect('/appxptostore/cart-view/')
    return render(request, 'carrinho/checkout.html', context)

@login_required(login_url=reverse_lazy("auth-login-view"))
def submitEncomenda(request):
    context = {}
    
    # Obter cliente logado
    user = request.user.id

    # Obter produtos do carrinho
    cart = request.session.get('cart', {})

    # Chamar o procedimento para criar a encomenda 
    # ( clientid)
    user = request.user.id

    # ( adress inserido)
    inputAdress = request.POST['adress']
    
    # ( cc inserido)
    inputCC = request.POST['inputCC']

    # total price, obtem-se do carrinho
    totalprice = getCartTotalPrice(request)

    if request.user.isAdmin:
        cursor = connections['adminUser'].cursor()
        print("isAdmin")
    elif request.user.isClient:
        cursor = connections['clientUser'].cursor()
        print("isClient")
    elif request.user.isPartner:
        cursor = connections['comercialTwo'].cursor()
        print("isPartner")
    elif request.user.isComercialTypeOne:
        cursor = connections['comercialOne'].cursor()
        print("isComercialTypeOne")
    elif request.user.isComercialTypeTwo:
        cursor = connections['comercialTwo'].cursor()
        print("isComercialTypeTwo")

    # Chamar o procedimento para criar a encomenda
    output = 0
    try:
        cursor.execute('call insertNewOrder(%s, %s, %s, %s, %s)', (str(user), str(inputAdress), str(inputCC), str(totalprice), str(output)))      
    except Exception as e:
        print(f"An error occurred: {e}")
        return redirect('/appxptostore/permission_not_granted/')
    
    order_id = cursor.fetchone()[0]

    # Obter produtos do carrinho
    products = [item['product'] for item in cart.values()]   
    for product in products:
        id              = product['id']
        productQuantity = product['productQuantity']
        price           = product['price']

        # Atualizar quantidades de produtos ao MONGODB
        productObj = Product.objects.using('default').filter(id = id)
        newQuantity = int(productObj[0].quantity) - int(productQuantity)

        # Validar se existe quantidade suficiente para a encomenda
        if newQuantity < 0:
            messages.warning(request,"Não existe quantidade suficiente de produtos para a sua encomenda")
            cursor.execute('call deleteOrderByID(%s)', (str(order_id)))
            return redirect('/appxptostore/cart-view/')

        # Chamar o procedimento para criar items associados à encomenda
        try:
            cursor.execute('call insertProductOrderDetails(%s, %s, %s, %s)', (str(id), str(productQuantity), str(price),str(order_id)))
        except:
            return redirect('/appxptostore/permission_not_granted/')

        # Atualizar quantidades de produtos ao MONGODB
        product = Product.objects.using('default').filter(id = id)
        newQuantity = int(product[0].quantity) - int(productQuantity)

        product.update(quantity = newQuantity)

    cursor.close()

    # Clear the cart
    request.session.pop('cart', None)
    
    return redirect('/appxptostore/cart-view/')

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Client, login_url='/appxptostore/permission_not_granted/')
def pendingClientOrders(request):
    cursor = connections['clientUser'].cursor()
    cursor.execute("SELECT * FROM getPendingOrderById(%s)", [str(request.user.id)])
    orders = cursor.fetchall()
    cursor.close()
    context = {
        'pendingorders': orders
    }
    return render(request, 'client/pending-orders.html', context)

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Client, login_url='/appxptostore/permission_not_granted/')
def concludedClientOrders(request):
    cursor = connections['clientUser'].cursor()
    cursor.execute("SELECT * FROM getConcludedOrderById(%s)", [str(request.user.id)])
    orders = cursor.fetchall()
    cursor.close()
    context = {
        'concludedorders': orders
    }
    return render(request, 'client/concluded-orders.html', context)

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Client, login_url='/appxptostore/permission_not_granted/')
def orderDetails(request,order_id):
    print("order_id",order_id)

    # Devolver os ids dos produtos associadas a essa encomenda, quantidade, preço
    cursor = connections['clientUser'].cursor()
    cursor.execute("SELECT * FROM getProductByOrder(%s)", [str(order_id)])
    orders = cursor.fetchall()
    print("orders",orders)
    cursor.close()
    
    products = []
    totalPrice = 0
    for data in orders:
        productInfo = Product.objects.using('default').get(id = data[0])
        product = {
            'id': data[0], 
            'name': productInfo.name,
            'image': productInfo.image.url,
            'quantity': data[1], 
            'price': data[2],
            'productTotal': float(data[2]) * float(data[1]),
        }
        totalPrice = data[3]
        products.append(product)
    
    print("products",products)
    
    context = {
        'order_id': order_id,
        'orderProduct': products,
        'totalPrice': totalPrice
    }
    return render(request, 'client/order-details.html', context)


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def orderDetailscomercialTypeOne(request,order_id):
    # Devolver os ids dos produtos associadas a essa encomenda, quantidade, preço
    cursor = connections['comercialOne'].cursor()

    cursor.execute("SELECT * FROM getProductByOrder(%s)", [str(order_id)])
    orders = cursor.fetchall()
    
    products = []
    totalPrice = 0
    for data in orders:
        productInfo = Product.objects.using('default').get(id = data[0])
        product = {
            'id': data[0], 
            'name': productInfo.name,
            'image': productInfo.image.url,
            'quantity': data[1], 
            'price': data[2],
            'productTotal': float(data[2]) * float(data[1]),
        }
        totalPrice = data[3]
        products.append(product)
    
    context = {
        'order_id': order_id,
        'orderProduct': products,
        'totalPrice': totalPrice
    }
    return render(request, 'comercialTypeOne/order-details.html', context)


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeTwo, login_url='/appxptostore/permission_not_granted/')
def orderDetailscomercialTypeTwo(request,order_id):
    # Devolver os ids dos produtos associadas a essa encomenda, quantidade, preço
    cursor = connections['comercialTwo'].cursor()

    cursor.execute("SELECT * FROM getProductByOrder(%s)", [str(order_id)])
    orders = cursor.fetchall()
    
    products = []
    totalPrice = 0
    for data in orders:
        productInfo = Product.objects.using('default').get(id = data[0])
        product = {
            'id': data[0], 
            'name': productInfo.name,
            'image': productInfo.image.url,
            'quantity': data[1], 
            'price': data[2],
            'productTotal': float(data[2]) * float(data[1]),
        }
        totalPrice = data[3]
        products.append(product)
    
    
    context = {
        'order_id': order_id,
        'orderProduct': products,
        'totalPrice': totalPrice
    }
    return render(request, 'comercialTypeTwo/order-details.html', context)


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def setOrderToShipped(request,order_id):
    cursor = connections['comercialOne'].cursor()
    cursor.execute('call UpdateStatusShipped(%s)', [str(order_id)])
    return redirect('/appxptostore/comercialOne-view/')

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeOne, login_url='/appxptostore/permission_not_granted/')
def setOrderDelivered(request,order_id):
    cursor = connections['comercialOne'].cursor()
    cursor.execute('call setCompletedOrder(%s)', [str(order_id)])
    return redirect('/appxptostore/comercialOne-view/')


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Client, login_url='/appxptostore/permission_not_granted/')
def orderCancel(request,order_id):
    cursor = connections['clientUser'].cursor()
    cursor.execute('call setCanceledOrder(%s)', [str(order_id)])
    return redirect('/appxptostore/client-view/pendingClientOrders/')


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeTwo, login_url='/appxptostore/permission_not_granted/')
def listcomercialsTypeTwo(request):
     
    context = {
        'listUsers': Utilizadores.objects.filter(isComercialTypeOne__in=[True]).all()
        }    
    return render(request, 'comercialTypeTwo/list-Comercials.html', context)


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_ComercialTypeTwo, login_url='/appxptostore/permission_not_granted/')
def listDetailscomercialsTypeTwo(request,comercial_id):
    cursor = connections['comercialTwo'].cursor()

    user = Utilizadores.objects.filter(id__in=str(comercial_id)).all()
    products = []

    productsIDs = Product.objects.filter(productOnwer= comercial_id).all()
    print(productsIDs)
    if productsIDs is not None:
        morequantity = Product.objects.filter(productOnwer=comercial_id).order_by('-quantity').first()
        minessquantity = Product.objects.filter(productOnwer=comercial_id).order_by('quantity').first()

        for data in productsIDs:
            cursor.execute("SELECT * FROM getTimesProduct(%s)", [str(data.id)])
            orders = cursor.fetchall()
            if len(orders)!=0:   
                product = {
                    'productID':orders[0][0],
                    'id':data.id,
                    'name':data.name,
                    'soldN':orders[0][1],
                    'url':data.image.url,
                    'price':data.price,
                    'quantity':data.quantity,
                    'image':data.image.url
                }
                products.append(product)
      
        context = {
            'comercialName':user[0].first_name + ' ' + user[0].last_name,
            'listProduct': products,
            'allProducts':productsIDs,
            'lastLogin':user[0].last_login,
            'date_joined':user[0].date_joined,
            'minessquantity':minessquantity,
            'morequantity':morequantity
        }
    else:
       context = {
            'comercialName':user[0].first_name + ' ' + user[0].last_name,
            'listProduct': "sem produtos",
            'allProducts':"sem produtos",
            'lastLogin':user[0].last_login,
            'date_joined':user[0].date_joined,
            'minessquantity':"sem produtos",
            'morequantity':"sem produtos"
        }     
    return render(request, 'comercialTypeTwo/list-Comercials-details.html', context)


@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Partner, login_url='/appxptostore/permission_not_granted/')
def partnerView(request):
    filteredProduct = Product.objects.filter(productOnwer = request.user.id).all()
    context = {
        'listProducts': filteredProduct
    }
    return render(request, 'partner/partner.html', context)

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Partner, login_url='/appxptostore/permission_not_granted/')
def partnerCreateProductView(request):
    context = { 
        'categorys': Category.objects.all().filter(status__in= [True],validated__in = [True]),
        'providers': Fornecedores.objects.all().filter(status__in= [True])
    }
    return render(request, 'partner/create-product.html', context)

@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_Partner, login_url='/appxptostore/permission_not_granted/')
def partnerCreateProductSubmit(request):
    print("VOU SUBMETER")
    if request.method == "POST":
        form = CreateProductForm(request.POST)
        if form.is_valid():
            Produtos                = form.save(commit=False)
            Produtos.name           = form.cleaned_data.get('name')
            Produtos.quantity       = form.cleaned_data.get('quantity')
            Produtos.description    = form.cleaned_data.get('description')
            Produtos.price          = form.cleaned_data.get('price')
            Produtos.promo_price    = form.cleaned_data.get('promo_price')

            if len(request.FILES) != 0:
                Produtos.image = request.FILES['image']

            selectedCategory_option = request.POST['select']
            selectedProvider_option = request.POST['selectfornecedor']
            
            # Validar a opção selecionada no menu
            if selectedCategory_option == 'Escolha a categoria':
                messages.warning(request, "Tem de escolher uma categoria")
                return redirect('/appxptostore/partner-view/create-product/')

            # Validar a opção selecionada no menu
            if selectedProvider_option == 'Escolha o fornecedor':
                messages.warning(request, "Tem de escolher um fornecedor")
                return redirect('/appxptostore/partner-view/create-product/')

            # Guardar produto no mongodb
            Produtos.productOnwer       = request.user.id
            Produtos.procuctCategory    = selectedCategory_option
            Produtos.productFornecedor  = selectedProvider_option
            Produtos.save()

            messages.success(request,"Produto criado com sucesso")
        else:
            print(form.errors.as_data())
            messages.warning(request,"Preencha os campos corretamente")
            return redirect('/appxptostore/partner-view/create-product/')
    else:
        form = RegisterClientForm()
        print(form.errors.as_data())
    return redirect('/appxptostore/partner-view/create-product/')

from xml.etree import ElementTree as ET
@login_required(login_url=reverse_lazy("auth-login-view"))
@user_passes_test(check_can_export_invoice, login_url='/appxptostore/permission_not_granted/')
def exportfatura(request, order_id):
    cursor = connections['clientUser'].cursor()
    cursor.execute("SELECT export_xml_order(%s)", [order_id])
    rows = cursor.fetchone()[0]
    root = ET.fromstring(rows)
    data = ET.tostring(root, encoding='utf-8')

    response = HttpResponse(data, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="order.xml"'

    return response


