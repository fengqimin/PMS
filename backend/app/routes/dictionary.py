from flask import Blueprint, jsonify, request
from app import db
from app.models import Dictionary, DictionaryItem
from flask_jwt_extended import jwt_required

bp = Blueprint('dictionary', __name__, url_prefix='/api/dictionary')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_dictionaries():
    dictionaries = Dictionary.query.all()
    return jsonify([d.to_dict() for d in dictionaries])

@bp.route('/<int:dictionary_id>', methods=['GET'])
@jwt_required()
def get_dictionary(dictionary_id):
    dictionary = Dictionary.query.get_or_404(dictionary_id)
    return jsonify(dictionary.to_dict())

@bp.route('/', methods=['POST'])
@jwt_required()
def create_dictionary():
    data = request.get_json()
    dictionary = Dictionary(
        name=data['name'],
        code=data['code'],
        description=data.get('description')
    )
    db.session.add(dictionary)
    db.session.commit()
    return jsonify(dictionary.to_dict()), 201

@bp.route('/<int:dictionary_id>', methods=['PUT'])
@jwt_required()
def update_dictionary(dictionary_id):
    dictionary = Dictionary.query.get_or_404(dictionary_id)
    data = request.get_json()
    dictionary.name = data['name']
    dictionary.code = data['code']
    dictionary.description = data.get('description')
    db.session.commit()
    return jsonify(dictionary.to_dict())

@bp.route('/<int:dictionary_id>', methods=['DELETE'])
@jwt_required()
def delete_dictionary(dictionary_id):
    dictionary = Dictionary.query.get_or_404(dictionary_id)
    db.session.delete(dictionary)
    db.session.commit()
    return jsonify({'message': 'Dictionary deleted'}), 200

@bp.route('/<int:dictionary_id>/items', methods=['GET'])
@jwt_required()
def get_dictionary_items(dictionary_id):
    items = DictionaryItem.query.filter_by(dictionary_id=dictionary_id).all()
    return jsonify([i.to_dict() for i in items])

@bp.route('/<int:dictionary_id>/items', methods=['POST'])
@jwt_required()
def create_dictionary_item(dictionary_id):
    data = request.get_json()
    item = DictionaryItem(
        dictionary_id=dictionary_id,
        name=data['name'],
        value=data['value'],
        description=data.get('description')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_dictionary_item(item_id):
    item = DictionaryItem.query.get_or_404(item_id)
    data = request.get_json()
    item.name = data['name']
    item.value = data['value']
    item.description = data.get('description')
    db.session.commit()
    return jsonify(item.to_dict())

@bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_dictionary_item(item_id):
    item = DictionaryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Dictionary item deleted'}), 200