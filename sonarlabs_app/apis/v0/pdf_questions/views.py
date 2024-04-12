import os
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
import re
from rest_framework import status
from .helpers import get_pdf_chunks,open_ai_callback_response,get_top_pages,higlighted_data_result,get_uploaded_pdf_filename

class QuestionSuggestionsPDF(APIView):

    def post(self,request):

        user_question = "Generate a list of 4 questions based on the content of the provided PDF document as an array"
        # file_url = request.data['file_url']
        # file_id = request.data['file_id']

        try:
            file_name = f"Project Specifications.pdf"
            chunks,page_dict,pdf_document,file_name,result = get_pdf_chunks(file_name)

            response = open_ai_callback_response(chunks, user_question,file_name)
    
            questions = re.findall(r'\d+\. (.+)', response)
            
            # os.remove(file_name)
            return Response({"questions": questions},status=status.HTTP_200_OK)
        
        except:
            return Response({"message": "Could not process the pdf"},status=status.HTTP_400_BAD_REQUEST)
        
class UserQuestionPDF(APIView):

    def post(self,request):

        user_question = request.data['user_question']

        try:
            file_name = f"Project Specifications.pdf"

            chunks,page_dict,pdf_document,file_name,result = get_pdf_chunks(file_name)
        
            response = open_ai_callback_response(chunks, user_question,file_name)

            if response.lower() == "there isn't enough information.":
                return Response({"response": response},status=status.HTTP_200_OK)
            
            top_pages = get_top_pages(page_dict,response)

            result = higlighted_data_result(top_pages,pdf_document,response,result)

            # os.remove(file_name)

            return Response({"response": response, "result_data": result},status=status.HTTP_200_OK)
        
        except:
            return Response({"message": "Could not process the pdf"},status=status.HTTP_400_BAD_REQUEST)
class AuthQuestionSuggestionsPDF(APIView):

    def post(self,request):

        user_question = "Generate a list of 4 questions based on the content of the provided PDF document as an array"
        file_url = request.data['file_url']
        file_id = request.data['file_id']

        try:
            file_name = get_uploaded_pdf_filename(file_url,file_id)
            chunks,page_dict,pdf_document,file_name,result = get_pdf_chunks(file_name)

            response = open_ai_callback_response(chunks, user_question,file_name)
    
            questions = re.findall(r'\d+\. (.+)', response)
            
            os.remove(file_name)
            return Response({"questions": questions},status=status.HTTP_200_OK)
        
        except:
            return Response({"message": "Could not process the pdf"},status=status.HTTP_400_BAD_REQUEST)

        
class AuthUserQuestionPDF(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def post(self,request):

        user_question = request.data['user_question']
        file_url= request.data['file_url']
        file_id = request.data['file_id']

        try:
            file_name = get_uploaded_pdf_filename(file_url,file_id)

            chunks,page_dict,pdf_document,file_name,result = get_pdf_chunks(file_name)
        
            response = open_ai_callback_response(chunks, user_question,file_name)

            if response.lower() == "there isn't enough information.":
                return Response({"response": response},status=status.HTTP_200_OK)
            
            top_pages = get_top_pages(page_dict,response)

            result = higlighted_data_result(top_pages,pdf_document,response,result)

            os.remove(file_name)

            return Response({"response": response, "result_data": result},status=status.HTTP_200_OK)
        
        except:
            return Response({"message": "Could not process the pdf"},status=status.HTTP_400_BAD_REQUEST)
        