from sonarlabs_app.models import File,Project

def add_new_file(file_id,uploaded_by,file_name,file_type,signed_url,dir,project):
    file = File(
            file_id=file_id,
            uploaded_by=uploaded_by,
            file_name=file_name,
            file_type=file_type,
            dir=dir,
            project=project,
            s3_url=signed_url
        )
    file.save()

def get_uploaded_files(email,project_id):
    try:
        files = File.objects.filter(project__project_id=project_id,uploaded_by=email,)
        return files
    except:
        return  []
    
def add_new_project(project_id,project_name,created_by):
    project = Project(
            project_id = project_id,
            project_name = project_name,
            created_by = created_by,
        )
    project.save()

def update_project_files_count(project_id):
    project =Project.objects.get(project_id=project_id)
    total_count = project.total_files_count
    project.total_files_count = total_count+1
    project.save()
    return project

def get_user_projects(email):
    try:
        projects = Project.objects.filter(created_by=email)
        return projects
    except:
        return  []
    
def get_project(project_id):
    project =Project.objects.get(project_id=project_id)
    return project

def get_file_url(file_id):
    file = File.objects.get(file_id = file_id)
    file_url = file.s3_url
    return file_url