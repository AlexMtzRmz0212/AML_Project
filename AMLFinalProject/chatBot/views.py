from django.shortcuts import render
import requests
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from fpdf import FPDF
from io import BytesIO
# from docx import Document as DocxDocument
from .rag_pipeline import qa_chain  # Import the QA chain set up in rag_pipeline.py

def chat_view(request):
    return render(request, 'chat/chat.html')

def api_call(request):
    if request.method == "POST":
        user_input = request.POST.get('message')
        # response = requests.post('https://api.example.com/chat', json={"message": user_input})        
        # return JsonResponse(response.json())
        return JsonResponse({"response": "This is a hardcoded response for testing"})

def home(request):
    return HttpResponse("Hello, world!")

@csrf_exempt
def chat_response(request):
    if request.method == "POST":

        if not request.body:
            return JsonResponse({"error": "Empty request body"}, status=400)

        data = json.loads(request.body)
        user_query = data.get("message", "")
        
        # Run the user query through the RetrievalQA chain
        answer = qa_chain.run(user_query)
        
        # Check if a PDF is requested
        if data.get("pdf"):
            print("Generating PDF...")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            # Use multi_cell to support long text with automatic line breaks
            pdf.multi_cell(0, 10, answer)
            
            # Get the PDF as a string and encode it to bytes
            pdf_output = pdf.output(dest="S").encode("latin1")
            
            response = HttpResponse(pdf_output, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="response.pdf"'
            print("PDF Generated!")
            return response
        
        # Check if a Word document is requested
        # elif data.get("word"):
        #     print("Generating Word document...")
        #     doc = DocxDocument()
        #     doc.add_paragraph(answer)
            
        #     word_buffer = BytesIO()
        #     doc.save(word_buffer)
        #     word_data = word_buffer.getvalue()
            
        #     response = HttpResponse(word_data, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        #     response["Content-Disposition"] = 'attachment; filename="response.docx"'
        #     print("Word document generated!")
        #     return response
        
        # Default: return JSON response
        return JsonResponse({"response": answer})
    
    return JsonResponse({"error": "Invalid request"}, status=400)
