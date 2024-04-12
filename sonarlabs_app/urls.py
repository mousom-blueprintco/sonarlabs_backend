from django.urls import path, include
from .apis.v0.user.urls import urlpatterns as user_v0_urls
from .apis.v0.documents_upload.urls import urlpatterns as documents_upload_v0_urls
from .apis.v0.pdf_questions.urls import urlpatterns as pdf_questions_v0_urls

urlpatterns = [
    path("", include(user_v0_urls), name='sonar user'),
    path("", include(documents_upload_v0_urls), name='sonar file upload'),
    path("", include(pdf_questions_v0_urls), name='sonar pdf questions'),
]