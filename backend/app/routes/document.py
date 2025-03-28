"""项目文档管理功能
    实现文件上传和文档管理API
"""
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import ProjectDocument
from auth import jwt_required as token_required

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def document_routes(app):
    @app.route('/api/projects/<int:project_id>/documents', methods=['POST'])
    @token_required
    def upload_document(current_user, project_id):
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            document = ProjectDocument(
                project_id=project_id,
                name=request.form.get('name', filename),
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                file_type=filename.rsplit('.', 1)[1].lower(),
                description=request.form.get('description', ''),
                uploaded_by=current_user.id
            )
            db.session.add(document)
            db.session.commit()
            
            return jsonify(document.to_dict()), 201
        else:
            return jsonify({'error': 'File type not allowed'}), 400
    
    @app.route('/api/projects/<int:project_id>/documents', methods=['GET'])
    @token_required
    def get_project_documents(current_user, project_id):
        documents = ProjectDocument.query.filter_by(project_id=project_id).all()
        return jsonify([doc.to_dict() for doc in documents])
    
    @app.route('/api/projects/<int:project_id>/documents/<int:document_id>', methods=['GET'])
    @token_required
    def get_document(current_user, project_id, document_id):
        document = ProjectDocument.query.filter_by(id=document_id, project_id=project_id).first()
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        return jsonify(document.to_dict())
    
    @app.route('/api/projects/<int:project_id>/documents/<int:document_id>', methods=['DELETE'])
    @token_required
    def delete_document(current_user, project_id, document_id):
        document = ProjectDocument.query.filter_by(id=document_id, project_id=project_id).first()
        if not document:
            return jsonify({'error': 'Document not found'}), 404
            
        try:
            os.remove(document.file_path)
        except OSError:
            pass
            
        db.session.delete(document)
        db.session.commit()
        return jsonify({'message': 'Document deleted successfully'})