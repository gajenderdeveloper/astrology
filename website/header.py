from .models import *
def header(request):
    horoscope = Horoscope.objects.order_by('created_at')
   
    #print(horoscope)
    return {
        'header' : horoscope,
        'horoscope_slug' :'inner'
        }