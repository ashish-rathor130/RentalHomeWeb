
from django.shortcuts import render
from properties.models import Property

def home(request):
    properties = Property.objects.all()
    
    # Get filter values from URL
    location = request.GET.get('location')
    price = request.GET.get('price')

    # Apply filters
    if location:
        properties = properties.filter(location__icontains=location)

    if price:
        properties = properties.filter(price__lte=price)

    context = {
        'rooms': properties
    }

    return render(request, 'index.html', context)