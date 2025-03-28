from django.shortcuts import render
from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .rag_pipeline import qa_chain  # Import the QA chain set up in rag_pipeline.py

# Create your views here.

def home(request):
    return HttpResponse("Hello, world!")

@csrf_exempt
def chat_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_query = data.get("message", "")
        # Run the user query through the RetrievalQA chain
        answer = qa_chain.run(user_query)
        return JsonResponse({"response": answer})
    return JsonResponse({"error": "Invalid request"}, status=400)