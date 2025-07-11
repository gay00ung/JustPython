from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)  # 모든 출처에서 접근 가능하도록 설정

class SimpleNutritionBot:
    def __init__(self):
        # 미리 정의된 응답들
        self.responses = {
            'craving': [
                "물 한 잔 마시고 10분만 기다려보세요! 가짜 배고픔일 수 있어요 💧",
                "지금 {remaining_calories}kcal 남았네요. 가벼운 간식은 어때요?",
                "오늘 {protein}g 단백질 섭취하셨네요! 대단해요 💪",
                "심호흡 3번 하고 산책 어때요? 기분전환이 될 거예요 🚶"
            ],
            'guilt': [
                "괜찮아요! 한 끼로 살이 찌지 않아요. 내일 다시 시작하면 돼요 🌟",
                "즐겁게 먹었다면 그것도 중요해요. 행복도 건강의 일부예요 😊",
                "오늘 총 {calories}kcal 드셨네요. 일주일 평균으로 보면 괜찮을 거예요!",
                "자책하지 마세요. 꾸준함이 완벽함보다 중요해요 💝"
            ],
            'motivation': [
                "오늘도 기록하고 계시네요! 그것만으로도 대단해요 ✨",
                "목표까지 {days_left}일 남았어요! 할 수 있어요!",
                "이번 주 평균 {avg_calories}kcal 유지 중! 잘하고 있어요 📊",
                "작은 변화가 큰 결과를 만들어요. 계속 화이팅! 🎯"
            ],
            'general': [
                "건강한 식습관을 만들어가고 계시네요! 👍",
                "오늘 하루는 어떠셨나요? 🌈",
                "꾸준히 기록하는 것만으로도 큰 발전이에요! 📝",
                "함께 건강한 삶을 만들어가요! 💚"
            ]
        }

    def analyze_intent(self, user_input):
        """사용자 의도 파악"""
        keywords = {
            'craving': ['먹고싶', '배고', '야식', '간식', '치킨', '피자', '떡볶이', '라면'],
            'guilt': ['죄책감', '많이 먹었', '폭식', '실패', '후회', '미안'],
            'motivation': ['동기부여', '응원', '힘들어', '포기', '어려워', '못하겠']
        }
        
        user_input_lower = user_input.lower()
        
        for intent, words in keywords.items():
            if any(word in user_input for word in words):
                return intent
        
        return 'general'

    def generate_response(self, user_input, user_data=None):
        """응답 생성"""
        intent = self.analyze_intent(user_input)
        
        if intent in self.responses:
            response_template = random.choice(self.responses[intent])
            
            # 사용자 데이터로 템플릿 채우기
            if user_data:
                try:
                    response = response_template.format(**user_data)
                except:
                    # 데이터가 없는 경우 중괄호 제거
                    response = response_template
                    for key in ['{remaining_calories}', '{protein}', '{calories}', '{days_left}', '{avg_calories}']:
                        response = response.replace(key, '')
            else:
                # 데이터가 없으면 중괄호 제거
                response = response_template
                for key in ['{remaining_calories}', '{protein}', '{calories}', '{days_left}', '{avg_calories}']:
                    response = response.replace(key, '')
            
            return response.strip()
        else:
            return "계속 기록하면서 건강한 습관을 만들어가요! 화이팅 💪"

bot = SimpleNutritionBot()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message', '')
        user_data = data.get('user_data', {})
        
        response = bot.generate_response(user_input, user_data)
        
        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)