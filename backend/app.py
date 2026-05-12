# ============================================================
# مشروع فرصتي - Flask API
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')

import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# ===== Gemini Chatbot Setup =====
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("GEMINI KEY EXISTS:", GEMINI_API_KEY is not None)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    system_instruction = """أنت مساعد فرصتي، خبير بأحياء الرياض التجارية.
أجب بالعربية أو الإنجليزية حسب لغة المستخدم.
إذا سُئلت عن شيء خارج نطاق أحياء الرياض، اعتذر بلطف.
عدد الأحياء: 60 حياً، عدد الفئات التجارية: 28 فئة."""
    
    gemini_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    chat_sessions = {}
else:
    gemini_model = None
    chat_sessions = {}

# ===== اتصال قاعدة البيانات =====
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT,
                rating INTEGER DEFAULT 5,
                comment TEXT NOT NULL,
                date TIMESTAMP DEFAULT NOW()
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                msg TEXT NOT NULL,
                date TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print('✅ Database initialized')
    except Exception as e:
        print(f'⚠️ DB init error: {e}')

def load_reviews():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM reviews ORDER BY date DESC LIMIT 50")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f'load_reviews error: {e}')
        return []

def save_review(review):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO reviews (name, role, rating, comment) VALUES (%s, %s, %s, %s)",
            (review['name'], review.get('role', ''), review.get('rating', 5), review['comment'])
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f'save_review error: {e}')

def save_contact(contact):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contacts (name, email, msg) VALUES (%s, %s, %s)",
            (contact['name'], contact['email'], contact['msg'])
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f'save_contact error: {e}')

app = Flask(__name__)
CORS(app)
init_db()

# ===== تحميل النموذج =====
print('Loading model...')
with open('forsati_model_v2.pkl', 'rb') as f:
    saved = pickle.load(f)

xgboost_model = saved['model']
feature_cols = saved['features']

df = pd.read_csv('forsati_final_dataset.csv')

# Feature Engineering
df['category_share'] = df['category_count'] / (df['total_businesses'] + 1)
df['pop_per_business'] = df['Population'] / (df['total_businesses'] + 1)
df['transport_index'] = df['metro'] + df['bus'] + df['public_station']
df['nearby_competition_density'] = df['nearby_same_category'] / (df['nearby_all_businesses'] + 1)
df['economic_index'] = df['annual_transactions'] / (df['Population'] + 1)
df['pop_density_per_km2'] = df['Population'] / (df['Area_km2'] + 0.01)

# Target Encoding
neighborhood_success_rate = df.groupby('neighborhood')['success'].mean()
df['neighborhood_success_rate'] = df['neighborhood'].map(neighborhood_success_rate).fillna(df['success'].mean())

category_success_rate = df.groupby('category_en')['success'].mean()
df['category_success_rate'] = df['category_en'].map(category_success_rate).fillna(df['success'].mean())

# Centroid dict and other mappings (keep your existing ones)
# ... (أضيفي centroid_dict, neighborhood_en_to_ar, categoryArabic, categoryKeywords هنا)

le = LabelEncoder()
df['category_encoded'] = le.fit_transform(df['category_en'])

region_map = {0: 'Central', 1: 'East', 2: 'North', 3: 'South', 4: 'West'}
df['region'] = df['region_encoded'].map(region_map)
region_dummies = pd.get_dummies(df['region'], prefix='region')
df = pd.concat([df, region_dummies], axis=1)

print('Model loaded successfully!')

# ===== دوال مساعدة =====
def convert_to_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    return obj

def normalize_value(value, min_value, max_value):
    if max_value == min_value:
        return 0.5
    return (value - min_value) / (max_value - min_value)

def build_candidate_row(category_name, neighborhood_name):
    # ... (حافظي على الـ function حقك)
    pass

def calculate_score(category_name, neighborhood_name):
    # ... (حافظي على الـ function حقك)
    pass

# ===== API Routes =====
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Forsati API is running!'})

@app.route('/api/neighborhoods', methods=['GET'])
def get_neighborhoods():
    return jsonify({'neighborhoods': sorted(df['neighborhood'].unique().tolist())})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify({'categories': sorted(df['category_en'].unique().tolist())})

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    # ... (حافظي على الـ function حقك)
    pass

@app.route('/api/rank', methods=['POST'])
def rank():
    # ... (حافظي على الـ function حقك)
    pass

@app.route('/api/map/<category>', methods=['GET'])
def get_map(category):
    # ... (حافظي على الـ function حقك)
    pass

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    reviews = load_reviews()
    return jsonify({'reviews': reviews})

@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json
    name = data.get('name', '').strip()
    rating = data.get('rating', 5)
    comment = data.get('comment', '').strip()
    role = data.get('role', '').strip()

    if not name or not comment:
        return jsonify({'error': 'name and comment required'}), 400

    review = {
        'name': name,
        'role': role,
        'rating': rating,
        'comment': comment,
    }
    save_review(review)
    return jsonify({'success': True})

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    msg = data.get('msg', '').strip()

    if not name or not email or not msg:
        return jsonify({'error': 'all fields required'}), 400

    contact_entry = {
        'name': name,
        'email': email,
        'msg': msg,
    }
    save_contact(contact_entry)
    return jsonify({'success': True})

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts ORDER BY date DESC LIMIT 50")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({'contacts': [dict(r) for r in rows]})
    except Exception as e:
        print(f'get_contacts error: {e}')
        return jsonify({'contacts': []})

# ===== Chatbot Route =====
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question", "").strip()
    lang = data.get("lang", "ar")
    session_id = data.get("session_id", "default")

    if not question:
        return jsonify({"answer": "الرجاء كتابة سؤال 😊"})

    # استخدام Gemini إذا متاح
    if gemini_model:
        try:
            if session_id not in chat_sessions:
                chat_sessions[session_id] = gemini_model.start_chat(history=[])
            chat = chat_sessions[session_id]
            response = chat.send_message(question)
            return jsonify({"answer": response.text})
        except Exception as e:
            print(f"Gemini error: {e}")

    # Fallback إلى نظام القواعد
    # ... (أضيفي منطق القواعد الأساسي هنا)

    return jsonify({"answer": "عذراً، حدث خطأ 😅"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)