from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from uuid import uuid4
from rest_framework.views import APIView
from .helpers import save_file_s3
from .services import add_new_file,get_uploaded_files,add_new_project,update_project_files_count,get_user_projects,get_project,get_file_url
from .serializers import FileSerializer,ProjectSerializer
from sonarlabs_app.apis.v0.user.services import get_user_by_id
class AddProject(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        user = get_user_by_id(request.user.id)
        created_by =  user.email
        project_name = request.data.get('project_name')

        if not all([created_by, project_name]):
            return Response({'error': 'Incomplete data provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            project_id = uuid4().hex
            add_new_project(project_id,project_name,created_by)
            return Response({'data': project_id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class FileUpload(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def post(self, request):

        user = get_user_by_id(request.user.id)
        file_name = request.data.get('file_name')
        file_type = request.data.get('file_type')
        dir = request.data.get('dir')
        file_obj = request.FILES.get('file')
        project_id = request.data.get('project_id')
        uploaded_by = user.email
        
        if not all([uploaded_by, file_name, file_type, dir, file_obj,project_id]):
            return Response({'error': 'Incomplete data provided'}, status=status.HTTP_400_BAD_REQUEST)
          
        try:
            file_id = uuid4().hex
            file_dir=project_id+f"/{dir}"
            signed_url= save_file_s3(file_dir,file_id,file_obj)
            
            project = get_project(project_id)

            add_new_file(file_id,uploaded_by,file_name,file_type,signed_url,file_dir,project)
          
            update_project_files_count(project_id)
            return Response({'s3_url': signed_url}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class GetUserUploadedFiles(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self,request):

        user = get_user_by_id(request.user.id)
        email = user.email
        project_id = request.GET['project_id']

        try:
            files = get_uploaded_files(email,project_id)
            serializer = FileSerializer(files, many=True)
            uploaded_files = serializer.data

            return Response({'files': uploaded_files}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
class GetUserProjects(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self,request):

        # email = request.GET['created_by']
        user = get_user_by_id(request.user.id)
        email = user.email

        if not email:
            return Response({'error': 'Incomplete data provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            projects = get_user_projects(email)
            serializer = ProjectSerializer(projects, many=True)
            user_projects = serializer.data

            return Response({'projects': user_projects}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class GetFileUrl(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self,request):
        file_id = request.GET['file_id']

        if not file_id:
            return Response({'error': 'Incomplete data provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            file_url = get_file_url(file_id)

            return Response({'file_url': file_url}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
