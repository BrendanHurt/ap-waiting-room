from django.shortcuts import render


#def home(request):
#    username = None
#    context = { "username": username }
#    return render(request, 'home/homepage.html', context)
def home(request):
    return render(request, 'home/homepage.html')

def login(request):
    return render(request, "users/login.html")