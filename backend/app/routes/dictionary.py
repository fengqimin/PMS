from flask import Blueprint, jsonify, request
from app import db
from app.models import Dictionary, DictionaryItem
from flask_jwt_extended import jwt_required

# 字典管理路由蓝图
bp = Blueprint('dictionary', __name__, url_prefix='/api/dictionary')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_dictionaries():
    """
    获取所有字典列表
    Returns:
        字典列表的JSON数组
    """
    dictionaries = Dictionary.query.all()
    return jsonify({"code": 200, "message": "success", "data": [d.to_dict() for d in dictionaries]})

@bp.route('/<int:dictionary_id>', methods=['GET'])
@jwt_required()
def get_dictionary(dictionary_id):
    """
    获取单个字典详情
    Args:
        dictionary_id: 字典ID
    Returns:
        字典详情的JSON对象
    """
    dictionary = Dictionary.query.get_or_404(dictionary_id)
    return jsonify({"code": 200, "message": "success", "data": dictionary.to_dict()})

@bp.route('/', methods=['POST'])
@jwt_required()
def create_dictionary():
    """
    创建新字典
    Request Body:
        name: 字典名称(必填)
        code: 字典编码(必填)
        description: 字典描述(可选)
    Returns:
        新创建的字典对象
    """
    data = request.get_json()
    try:
        dictionary = Dictionary(
            name=data['name'],
            code=data['code'],
            description=data.get('description')
        )
        db.session.add(dictionary)
        db.session.commit()
        return jsonify({"code": 201, "message": "created", "data": dictionary.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400

@bp.route('/<int:dictionary_id>', methods=['PUT'])
@jwt_required()
def update_dictionary(dictionary_id):
    """
    更新字典信息
    Args:
        dictionary_id: 要更新的字典ID
    Request Body:
        name: 新字典名称
        code: 新字典编码
        description: 新字典描述(可选)
    Returns:
        更新后的字典对象
    """
    dictionary = Dictionary.query.get_or_404(dictionary_id)
    try:
        data = request.get_json()
        dictionary.name = data['name']
        dictionary.code = data['code']
        dictionary.description = data.get('description')
        db.session.commit()
        return jsonify({"code": 200, "message": "updated", "data": dictionary.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400

@bp.route('/<int:dictionary_id>', methods=['DELETE'])
@jwt_required()
def delete_dictionary(dictionary_id):
    """
    删除字典
    Args:
        dictionary_id: 要删除的字典ID
    Returns:
        操作结果消息
    """
    dictionary = Dictionary.query.get_or_404(dictionary_id)
    try:
        db.session.delete(dictionary)
        db.session.commit()
        return jsonify({"code": 200, "message": "Dictionary deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400

@bp.route('/<int:dictionary_id>/items', methods=['GET'])
@jwt_required()
def get_dictionary_items(dictionary_id):
    """
    获取字典项列表
    Args:
        dictionary_id: 字典ID
    Returns:
        字典项列表的JSON数组
    """
    items = DictionaryItem.query.filter_by(dictionary_id=dictionary_id).all()
    return jsonify({"code": 200, "message": "success", "data": [i.to_dict() for i in items]})

@bp.route('/<int:dictionary_id>/items', methods=['POST'])
@jwt_required()
def create_dictionary_item(dictionary_id):
    """
    创建字典项
    Args:
        dictionary_id: 所属字典ID
    Request Body:
        name: 字典项名称(必填)
        value: 字典项值(必填)
        description: 字典项描述(可选)
    Returns:
        新创建的字典项对象
    """
    data = request.get_json()
    try:
        item = DictionaryItem(
            dictionary_id=dictionary_id,
            name=data['name'],
            value=data['value'],
            description=data.get('description')
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({"code": 201, "message": "created", "data": item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400

@bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_dictionary_item(item_id):
    """
    更新字典项
    Args:
        item_id: 要更新的字典项ID
    Request Body:
        name: 新字典项名称
        value: 新字典项值
        description: 新字典项描述(可选)
    Returns:
        更新后的字典项对象
    """
    item = DictionaryItem.query.get_or_404(item_id)
    try:
        data = request.get_json()
        item.name = data['name']
        item.value = data['value']
        item.description = data.get('description')
        db.session.commit()
        return jsonify({"code": 200, "message": "updated", "data": item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400

@bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_dictionary_item(item_id):
    """
    删除字典项
    Args:
        item_id: 要删除的字典项ID
    Returns:
        操作结果消息
    """
    item = DictionaryItem.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"code": 200, "message": "Dictionary item deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 400, "message": str(e)}), 400