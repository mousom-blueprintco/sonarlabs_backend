from django.urls import path

from .views import FileUpload,GetUserUploadedFiles,AddProject,GetUserProjects,GetFileUrl

urlpatterns = [
    path("upload-file/", FileUpload.as_view(), name="File Upload"),
    path("list-uploaded-files/", GetUserUploadedFiles.as_view(), name="Uploaded Files List"),
    path("add-project/", AddProject.as_view(), name="Add Project "),
    path("list-user-projects/", GetUserProjects.as_view(), name="List User Projects "),
    path("get-file-url/", GetFileUrl.as_view(), name="Get File Url "),
  
]
