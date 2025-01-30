import requests
from flask import current_app
import json
import re
from datetime import datetime
from zhdate import ZhDate

class AIService:
    def __init__(self):
        self.deepseek_api_key = None
        self.ollama_url = None
    
    def update_settings(self, deepseek_key=None, ollama_url=None):
        if deepseek_key:
            self.deepseek_api_key = deepseek_key
        if ollama_url:
            self.ollama_url = ollama_url
    
    def get_recommendations(self, location, preferences, local_foods, ai_type='deepseek', use_solar_term=True):
        print(f"location: {location},ai_type: {ai_type}")
        prompt = self._create_prompt(location, preferences, local_foods, use_solar_term)
        
        if ai_type == 'deepseek':
            return self._call_deepseek(prompt)
        else:
            return self._call_ollama(prompt)
    
    def get_current_solar_term(self):
        """获取当前节气"""
        try:
            today = datetime.now()
            
            # 二十四节气列表及其大致日期
            solar_terms = {
                (2, 3): "立春", (2, 18): "雨水",
                (3, 5): "惊蛰", (3, 20): "春分",
                (4, 4): "清明", (4, 19): "谷雨",
                (5, 5): "立夏", (5, 20): "小满",
                (6, 5): "芒种", (6, 21): "夏至",
                (7, 6): "小暑", (7, 22): "大暑",
                (8, 7): "立秋", (8, 22): "处暑",
                (9, 7): "白露", (9, 22): "秋分",
                (10, 8): "寒露", (10, 23): "霜降",
                (11, 7): "立冬", (11, 22): "小雪",
                (12, 6): "大雪", (12, 21): "冬至",
                (1, 5): "小寒", (1, 20): "大寒"
            }
            
            current_month = today.month
            current_day = today.day
            
            # 找到最接近的节气
            closest_term = None
            min_diff = float('inf')
            
            for (month, day), term in solar_terms.items():
                # 计算日期差异
                if month == current_month:
                    diff = abs(day - current_day)
                elif month == current_month - 1:
                    diff = abs(day - current_day + 30)
                elif month == current_month + 1:
                    diff = abs(day - current_day - 30)
                else:
                    continue
                
                if diff < min_diff:
                    min_diff = diff
                    closest_term = term
            
            return closest_term if closest_term else "未知"
            
        except Exception as e:
            print(f"获取节气出错: {str(e)}")
            return "未知"

    def _create_prompt(self, location, preferences, local_foods, use_solar_term=True):
        # 获取当前节气
        current_term = self.get_current_solar_term() if use_solar_term else None
        solar_term_info = f"当前节气：{current_term}" if current_term else "用户选择不按节气推荐"
        
        # 分析用户偏好
        preference_analysis = self._analyze_preferences(preferences)
        
        return f"""作为一个专业的美食推荐专家，请根据用户的具体偏好和节气特点提供定制化的用餐方案。

背景信息：
- 用户所在城市：{location}
- 当地特色美食：{', '.join(local_foods)}
- 用户的饮食偏好：{', '.join(preferences) if preferences else '暂无特别偏好'}
- {solar_term_info}

# 用户偏好分析（必须）：
{preference_analysis}

请严格按照以下要求提供3个符合用户偏好的推荐方案：

推荐：
- 推荐理由：[结合用户偏好和时令特色说明]
- 符合偏好：[说明如何满足用户的具体偏好]

注意事项：
1. 必须严格遵循用户的具体偏好
2. 每个推荐都要明确说明如何满足用户偏好
3. 如果用户喜欢特定口味（如甜食），至少一个推荐必须完全满足该口味
4. 如果用户想吃特定类型（如面食），推荐应以该类型为主
5. 推荐要考虑节气特点和当季食材
6. 建议要实际可行，价格合理

# 示例输出
## 用户输入：
- 城市：苏州
- 偏好：低糖、春季时令、2人用餐
- 特殊需求：控血糖

## 推荐方案1：碧螺春虾仁
🥢 核心亮点：苏州非遗茶膳，低GI高蛋白
📌 推荐理由：
- 节气关联：清明茶鲜，碧螺春茶多酚辅助控血糖
- 偏好匹配：河虾仁蛋白质替代红肉，茶香替代糖提鲜
- 本地特色：苏州松鹤楼经典菜改良版

💡 行动建议：
- 家庭版：现剥太湖虾仁+冷泡碧螺春去涩（成本¥40/2人）
- 外食版：得月楼（¥¥）提供少油版本，需提前预约
"""

    def _analyze_preferences(self, preferences):
        """分析用户偏好，生成具体的偏好要求"""
        if not preferences:
            return "用户未指定特别偏好，可以推荐多样化的美食。"
        
        analysis = []
        for pref in preferences:
            # 口味偏好
            if "甜" in pref:
                analysis.append("- 用户喜欢甜食，必须包含甜品或甜口味的菜品")
            elif "辣" in pref:
                analysis.append("- 用户喜欢辣味，建议推荐适当辣度的菜品")
            elif "咸" in pref:
                analysis.append("- 用户喜欢咸味，可以推荐适中咸度的菜品")
            
            # 食材类型
            if "面" in pref or "面食" in pref:
                analysis.append("- 用户想吃面食，推荐应以面食为主")
            elif "肉" in pref:
                analysis.append("- 用户想吃肉类，确保推荐包含优质肉类菜品")
            elif "海鲜" in pref:
                analysis.append("- 用户想吃海鲜，建议推荐新鲜海鲜菜品")
            elif "素" in pref or "蔬菜" in pref:
                analysis.append("- 用户偏好素食或蔬菜，推荐应以植物性食材为主")
            
            # 烹饪方式
            if "炒" in pref:
                analysis.append("- 用户喜欢炒菜，可以推荐清炒类菜品")
            elif "煮" in pref or "汤" in pref:
                analysis.append("- 用户想喝汤或煮品，建议搭配养生汤品")
            elif "烤" in pref:
                analysis.append("- 用户喜欢烤制食物，可以推荐烧烤类美食")
            
        # 如果没有匹配到具体分类，作为通用偏好处理
        if not analysis:
            analysis.append(f"- 用户表达了对{', '.join(preferences)}的偏好，推荐应考虑这些要素")
        
        return "\n".join(analysis)

    def _clean_ai_response(self, text):
        """清理AI返回的文本，去掉<think>标签及其内容"""
        # 去掉<think>标签及其内容
        cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # 清理多余的空行
        cleaned_text = '\n'.join(line for line in cleaned_text.split('\n') if line.strip())
        return cleaned_text

    def _call_deepseek(self, prompt):
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                response_text = self._clean_ai_response(response_data['choices'][0]['message']['content'])
                recommendations = response_text.split('\n\n')
                # 过滤掉空行并清理格式
                return [rec.strip() for rec in recommendations if rec.strip() and rec.startswith('推荐')]
            else:
                return [f"DeepSeek API 调用失败: {response.status_code}", "请检查API密钥是否正确"]
                
        except Exception as e:
            return [f"DeepSeek API 调用出错: {str(e)}", "请确保网络连接正常且API密钥有效"]

    def _call_ollama(self, prompt):
        print(f"ollama_url: {self.ollama_url}")
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "deepseek-r1:8b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 1000,  # 增加输出长度限制
                        "stop": ["Human:", "Assistant:"]  # 添加停止标记
                    }
                }
            )
            
            if response.status_code == 200:
                response_text = self._clean_ai_response(response.json()['response'])
                print(f"AI原始响应: {response_text}")  # 添加调试输出
                
                # 更严格的推荐提取
                recommendations = []
                current_rec = []
                
                for line in response_text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith('推荐'):
                        if current_rec:
                            recommendations.append('\n'.join(current_rec))
                            current_rec = []
                        current_rec.append(line)
                    elif current_rec:
                        current_rec.append(line)
                
                # 添加最后一个推荐
                if current_rec:
                    recommendations.append('\n'.join(current_rec))
                
                # 确保至少返回一个有效推荐
                if not recommendations:
                    print("未能提取到有效推荐，尝试重新格式化响应")
                    # 如果没有提取到标准格式的推荐，尝试将整个响应作为一个推荐
                    cleaned_response = response_text.strip()
                    if cleaned_response:
                        recommendations = [f"推荐：\n{cleaned_response}"]
                    else:
                        recommendations = ["抱歉，暂时无法生成推荐，请重试"]
                
                print(f"处理后的推荐: {recommendations}")  # 添加调试输出
                return recommendations
            else:
                print(f"API调用失败: {response.status_code}")  # 添加调试输出
                return [f"AI服务暂时不可用 (状态码: {response.status_code})", "请稍后重试"]
                
        except Exception as e:
            print(f"发生异常: {str(e)}")  # 添加调试输出
            return [f"推荐服务出错: {str(e)}", "请检查网络连接并重试"] 