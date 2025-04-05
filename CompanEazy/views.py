from django.shortcuts import render
import random



def index(request):
    message = "Oops! The page you are looking for is lost in space."
    error = random.randint(400, 451)
    return render(request, 'index.html', {'message': message, "error": error})

