from django.shortcuts import render
from django.http import JsonResponse
import requests

def chat_view(request):
    return render(request, 'chat/chat.html')

def api_call(request):
    if request.method == "POST":
        user_input = request.POST.get('message')
        # response = requests.post('https://api.example.com/chat', json={"message": user_input})        
        # return JsonResponse(response.json())
        return JsonResponse({"response": "This is a hardcoded response for testing"})

