from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect,get_object_or_404
from django.contrib import messages
from .models import User
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
def login_page(request):
    if request.method == 'POST':
        next_url = request.POST.get('next')
        username =request.POST.get('username')
        password =request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            if next_url:
                return redirect(next_url)
            else:                
                return redirect('/')
        else:
            messages.warning(request, 'No te has podido identificar :)')
    return render(request, 'auth/login.html')


def register_page(request):    
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            messages.success(request, 'Te has registrado correctamente')
            return redirect('/') 
    else:
        # Se instancia un formulario vacío cuando la petición es GET
        register_form = RegisterForm()

    return render(request, 'auth/register.html', {
        'register_form': register_form, 'tipo_doc_choices': User.TipoDocumento.choices
    })

# Create your views here.
@login_required
def home(request):
    return render(request,'home.html')