from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('This is the index page for yamls')

def add(request):
    return HttpResponse('You have reached the add a yaml page. Please leave your message after the beep... beep')