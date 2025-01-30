from flask import Blueprint, render_template, request, jsonify
from app.services.ai_service import AIService
from app.services.geo_service import GeoService

main = Blueprint('main', __name__)
ai_service = AIService()
geo_service = GeoService()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/solar-term', methods=['GET'])
def get_solar_term():
    try:
        ai_service = AIService()
        term = ai_service.get_current_solar_term()
        return jsonify({
            'term': term,
            'success': True
        })
    except Exception as e:
        print(f"节气获取异常: {str(e)}")
        return jsonify({
            'term': '未知',
            'success': False,
            'error': str(e)
        })

@main.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    location = data.get('location')
    preferences = data.get('preferences', [])
    use_solar_term = data.get('use_solar_term', True)  # 添加节气选项
    
    ai_service = AIService()
    # 设置 AI 服务配置
    ai_settings = data.get('ai_settings', {})
    ai_service.update_settings(
        deepseek_key=ai_settings.get('deepseek_key'),
        ollama_url=ai_settings.get('ollama_url')
    )
    
    # 获取本地特色美食
    geo_service = GeoService()
    local_foods = geo_service.get_local_foods(location)
    
    # 获取 AI 推荐
    recommendations = ai_service.get_recommendations(
        location, 
        preferences, 
        local_foods,
        data.get('ai_type', 'deepseek'),
        use_solar_term  # 传递节气选项
    )
    
    return jsonify({
        'local_foods': local_foods,
        'ai_recommendations': recommendations
    }) 