from django.contrib import messages
from django.shortcuts import render

def index(request):
    messages.debug(request, message="디버그 메시지")
    messages.info(request, message="정보 메시지")
    messages.success(request, message="성공 메시지")
    messages.warning(request, message="경고 메시지")
    messages.error(request, message="에러 메시지")
    
    return render(request, template_name="core/index.html")
