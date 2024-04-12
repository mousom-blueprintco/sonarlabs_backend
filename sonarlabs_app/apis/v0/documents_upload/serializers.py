from rest_framework import serializers
from sonarlabs_app.models import File, Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'  

class FileSerializer(serializers.ModelSerializer):
    project = ProjectSerializer() 
    class Meta:
        model = File
        fields = '__all__'  
