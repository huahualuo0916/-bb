import os
import jieba
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_models import ChatZhipuAI

os.environ["ZHIPUAI_API_KEY"] = "1a7e2f28ddac1b8a605bbec350b4119b.oTspfqr879MO91dC"  # 替换为你的 API 密钥

llm = ChatZhipuAI(model="glm-4-flash", temperature=0)
app = Flask(__name__)
CORS(app)
city = None
# 读取并处理历史记录文件
chat_history = []
try:
    with open("chat_history.txt", "r", encoding="utf-8") as file:
        chat_text = file.readlines()
        for i in range(0, len(chat_text) - 1, 2):
            chat_history.append(HumanMessage(content=chat_text[i].strip()))
            chat_history.append(AIMessage(content=chat_text[i + 1].strip()))
except FileNotFoundError:
    print("未找到历史记录文件，初始化新的聊天记录。")

# 加载天津文化文档
# def load_culture_document(filename):
#     with open(filename, 'r', encoding='utf-8') as file:
#         return file.read()

# # 文档词汇索引
# def build_word_index(document_text):
#     words = jieba.lcut(document_text)
#     return set(words)

# # 检查相关
# def is_related_to_document(question, word_index):
#     question_words = jieba.lcut(question)
#     return any(word in word_index for word in question_words)

# 保存记录
def text_save(filename, data):
    with open(filename, 'a+', encoding="utf-8") as file:
        for message in data:
            s = message.content + '\n'
            file.write(s)

# 问答系统主逻辑
def answering_system(question, chat_history):
    try:
        # if not is_related_to_document(question, word_index):
        #     return "我只能回答与天津传统文化有关的问题，请重新提问。"
        messages = chat_history + [HumanMessage(content=question)]
        response = llm.invoke(messages)
        ai_message_content = response.content.strip()
        ai_message = AIMessage(content=ai_message_content)
        chat_history.append(HumanMessage(content=question))
        chat_history.append(ai_message)
        return ai_message_content
    except Exception as e:
        return f"处理问题时出错: {str(e)}"

# Flask 路由
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({'answer': '没有提供问题。'})
    answer = answering_system(question, chat_history)
    text_save("chat_history.txt", chat_history)
    return jsonify({'answer': answer})

@app.route('/set-city', methods=['POST'])
def set_city():
    global city
    data = request.json
    city = data.get('City')
    if not city:
        return jsonify({'message': '未提供城市信息。'}), 400
    if not isinstance(city, str):
        return jsonify({'message': '城市信息必须是字符串。'}), 400
    if city not in ['北京市', '天津市', '河北省']:  # 添加你支持的城市列表
        return jsonify({'message': '不支持该城市。'}), 400
    return jsonify({'message': '您可以向我提问有关'+city+'的信息啦'})

if __name__ == "__main__":
    # document_content = load_culture_document('tianjin_culture.txt')
    # word_index = build_word_index(document_content)
    app.run(host='0.0.0.0', port=5000)