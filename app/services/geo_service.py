import requests

class GeoService:
    def __init__(self):
        self.city_prompt = """作为一个本地美食专家，请列出以下城市的特色美食。
要求：
1. 只需列出4-6个最具代表性的美食名称
2. 只返回美食名称，用逗号分隔
3. 不要包含任何解释或描述
4. 如果是不认识的城市，返回"暂无当地特色美食信息"

城市：{location}"""

    def get_local_foods(self, location):
        try:
            return self._get_foods_from_ollama(location)
        except Exception as e:
            return ["暂无当地特色美食信息"]


    def _get_foods_from_ollama(self, location):
        print(f"_get_foods_from_ollama location: {location},prompt: {self.city_prompt.format(location=location)}")
        try:
            response = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "deepseek-r1:8b",
                    "prompt": self.city_prompt.format(location=location),
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9
                    }
                }
            )
            print(f"response: {response}")
            if response.status_code == 200:
                # 清理AI返回的文本
                foods_text = response.json()['response'].strip()
                # 去掉<think>标签及其内容
                import re
                foods_text = re.sub(r'<think>.*?</think>', '', foods_text, flags=re.DOTALL)
                # 清理并分割结果
                foods = [
                    food.strip() 
                    for food in foods_text.split(',') 
                    if food.strip() and food.strip() != "暂无当地特色美食信息"
                ]
                return foods if foods else ["暂无当地特色美食信息"]
            else:
                return ["暂无当地特色美食信息"]
                
        except Exception as e:
            return ["暂无当地特色美食信息"] 