from django.urls import path

from .views import UserQuestionPDF,QuestionSuggestionsPDF,AuthQuestionSuggestionsPDF,AuthUserQuestionPDF

urlpatterns = [
    path("suggestion-questions/", QuestionSuggestionsPDF.as_view(), name="Suggestion Questions"),
    path("user-questions/", UserQuestionPDF.as_view(), name="User Questions"),
    path("suggestion-questions-auth/", AuthQuestionSuggestionsPDF.as_view(), name="Auth User Suggestion Questions"),
    path("user-questions-auth/", AuthUserQuestionPDF.as_view(), name="Auth User Questions"),
]
