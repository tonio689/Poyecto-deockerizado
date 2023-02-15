import stripe

from locale import currency
from re import template
from django.conf import settings

from django.http import HttpResponse
from django.http import HttpRequest

from django.shortcuts import render, redirect
from AppProyectoF.models import Producto
from AppProyectoF.Carrito import Carrito
from AppProyectoF.forms import FormularioProducto

from django.contrib import messages
from django.contrib.auth.models import User
from .forms import *

from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
import requests
import json

# Create your views here.
stripe.api_key = 'sk_test_51KVzWjCoJ9ZBxLROdijHJEdnwZ2ENSsWKhEzSshMfnd8AbR0Regm3QoE2uOMUxaikttWo67dy62WduNmfdP9lUkj00Ya9eB8Sc'


def pagPrincipal(request):
    productos = Producto.objects.all()
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    return render(request, "index.html", {'data': location_data,'productos': productos })


def pagCarrito(request):
    return render(request, "cart.html", {})


def pagContactos(request):
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    return render(request, "contactos.html", {'data': location_data})


def pagPagos(request):
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    return render(request, "checkout.html", {'data': location_data})


def pagServicios(request):
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    return render(request, "servicios.html", {'data': location_data})


def pagProductoUnico(request):
    return render(request, "single-product.html", {})


def pagDetalles(request, id):
    producto = Producto.objects.get(id=id)
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    return render(request, "detalles.html",  {'data': location_data, 'form': producto})


def registrarProducto(request):
    datos = {
        'form': FormularioProducto()
    }
    if request.method == "POST":
        formulario = FormularioProducto(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            datos["mensaje"] = "Producto añadida exitosamente"
        else:
            datos["mensaje"] = "No se pudo añadir el Producto"

    return render(request, "productoIngreso.html", datos)


def modificarProducto(request, id):

    producto = Producto.objects.get(id=id)

    datos = {
        'form': FormularioProducto(instance=producto)
    }
    if request.method == "POST":
        formulario = FormularioProducto(
            data=request.POST, instance=producto, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            datos["mensaje"] = "Producto modificado exitosamente"
        else:
            datos["mensaje"] = "No se pudo modificar el Producto"

        datos["form"] = FormularioProducto(
            instance=Producto.objects.get(id=id))

    return render(request, "modificarProducto.html", datos)


def eliminarProducto(request, id):

    producto = Producto.objects.get(id=id)
    producto.delete()

    return redirect(to="listadoProductos")


def listadoProductos(request):
    productos = Producto.objects.all()

    data = {
        'productos': productos
    }
    return render(request, "listadoProductos.html", data)


def carrito_view(request):
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    return render(request, "carrito.html", {'data': location_data} )


def agregar_producto(request, producto_id):
    productos = Producto.objects.all()
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.agregar(producto)
    return redirect(to="pagPrincipal")


def sumar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.agregar(producto)
    return redirect("carrito")


def eliminar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.eliminar(producto)
    return redirect("carrito")


def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.restar(producto)
    return redirect("carrito")


def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect("carrito")


def pagar_view(request):
    if request.POST:

        cantidad = request.POST['valorAPagar']
        nombre = request.POST['nombre']
        email = request.POST['email']
        cantidad = int(float(cantidad))
        customer = stripe.Customer.create(
            email=email,
            name=nombre,
            source=request.POST['stripeToken']
        )
        charge = stripe.Charge.create(
            customer=customer,
            amount=cantidad*100,
            currency='usd',
            description='Compra online'
        )
        enviar_correo(email, request)
        limpiar_carrito(request)
        return redirect('pagPrincipal')
    else:
        return redirect('carrito')


def enviar_correo(mail, request):

    context = {
        'mail': mail,
    }
    template = get_template('correo.html')
    content = template.render(context, request)
    email = EmailMultiAlternatives(
        'Comprobante de compra ',
        'Pidelo pero Ya!',
        settings.EMAIL_HOST_USER,
        [mail]
    )

    email.attach_alternative(content, 'text/html')
    email.send()


def registrar(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            messages.success(request, f'Usuario {username} creado')
            return redirect('registrar')
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, 'registrar.html', context)
