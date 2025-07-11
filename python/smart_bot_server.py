# smart_bot_server.py - 수정된 버전
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re

app = Flask(__name__)

print("AI 모델 로딩 중...")
tokenizer = AutoTokenizer.from_pretrained("skt/kogpt2-base-v2")
model = AutoModelForCausalLM.from_pretrained("skt/kogpt2-base-v2")
tokenizer.pad_token = tokenizer.eos_token

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message', '')
        
        print(f"받은 메시지: {user_input}")
        
        # 더 간단한 프롬프트
        prompt = f"사용자: {user_input}\n상담사:"
        
        inputs = tokenizer.encode(prompt, return_tensors='pt', max_length=100, truncation=True)
        
        # attention mask 추가
        attention_mask = torch.ones(inputs.shape, dtype=torch.long)
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                attention_mask=attention_mask,
                max_new_tokens=30,  # 더 짧게
                min_new_tokens=5,   # 최소 길이 보장
                temperature=0.7,    # 더 안정적으로
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                no_repeat_ngram_size=3,  # 반복 방지
                early_stopping=True
            )
        
        # 전체 생성된 텍스트
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"전체 생성: {full_response}")
        
        # "상담사:" 이후의 텍스트만 추출
        if "상담사:" in full_response:
            response = full_response.split("상담사:")[-1].strip()
        else:
            response = full_response.replace(prompt, "").strip()
        
        # 이상한 텍스트 정리
        response = response.split('\n')[0]  # 첫 줄만
        response = re.sub(r'사용자:|상담사:', '', response)  # 역할 표시 제거
        response = response.strip()
        
        # 응답이 너무 짧거나 비어있으면 기본 응답
        if len(response) < 3:
            fallback_responses = [
                "그런 마음이 드시는군요. 더 자세히 말씀해주시겠어요?",
                "이해합니다. 어떤 점이 가장 힘드신가요?",
                "그렇군요. 제가 도와드릴 수 있는 부분이 있을까요?"
            ]
            import random
            response = random.choice(fallback_responses)
        
        print(f"최종 응답: {response}")
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        print(f"에러: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)