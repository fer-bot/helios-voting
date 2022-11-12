from django.http import HttpResponse
from django.template import loader


def homepage(request):
    template = loader.get_template('helios/homepage.html')
    return HttpResponse(template.render({}, request))
