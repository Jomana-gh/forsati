# ============================================================
# مشروع فرصتي - Flask API مع Gemini
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
import psycopg2
from psycopg2.extras import RealDictCursor
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("KEY:", GEMINI_API_KEY[:10] if GEMINI_API_KEY else "NO KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None

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

print('Loading model...')
with open('forsati_model_v2.pkl', 'rb') as f:
    saved = pickle.load(f)

xgboost_model = saved['model']
feature_cols = saved['features']

df = pd.read_csv('forsati_final_dataset.csv')

df['category_share'] = df['category_count'] / (df['total_businesses'] + 1)
df['pop_per_business'] = df['Population'] / (df['total_businesses'] + 1)
df['transport_index'] = df['metro'] + df['bus'] + df['public_station']
df['nearby_competition_density'] = df['nearby_same_category'] / (df['nearby_all_businesses'] + 1)
df['economic_index'] = df['annual_transactions'] / (df['Population'] + 1)
df['pop_density_per_km2'] = df['Population'] / (df['Area_km2'] + 0.01)

neighborhood_success_rate = df.groupby('neighborhood')['success'].mean()
df['neighborhood_success_rate'] = df['neighborhood'].map(neighborhood_success_rate).fillna(df['success'].mean())

category_success_rate = df.groupby('category_en')['success'].mean()
df['category_success_rate'] = df['category_en'].map(category_success_rate).fillna(df['success'].mean())

centroid_dict = {
    "الجرادية": (24.615341, 46.698203), "الدريهمية": (24.589588, 46.696444),
    "الشميسي": (24.624860, 46.699920), "الصالحية": (24.638578, 46.732876),
    "الصفا": (24.666518, 46.765194), "الضباط": (24.700599, 46.717772),
    "العزيزية": (24.588807, 46.769314), "العمل": (24.645886, 46.722836),
    "الفوطة": (24.641439, 46.710134), "المربع": (24.659888, 46.708374),
    "المرقب": (24.635705, 46.723309), "المعذر": (24.667454, 46.672583),
    "الملز": (24.662696, 46.734810), "المنصورة": (24.608786, 46.742449),
    "الوزارات": (24.678218, 46.713781), "الوشام": (24.642024, 46.697774),
    "اليمامة": (24.595363, 46.716657), "عليشة": (24.631765, 46.685586),
    "منفوحة": (24.599812, 46.728630), "الحمراء": (24.775513, 46.752748),
    "الخليج": (24.776760, 46.803989), "الروضة": (24.734541, 46.767540),
    "السعادة": (24.695791, 46.840067), "السلام": (24.707175, 46.811314),
    "السلي": (24.650190, 46.844559), "الفيحاء": (24.682143, 46.811571),
    "القدس": (24.755042, 46.754837), "المونسية": (24.832545, 46.769485),
    "النزهة": (24.756886, 46.708374), "النسيم الشرقي": (24.740439, 46.846390),
    "النسيم الغربي": (24.725160, 46.821327), "النهضة": (24.760549, 46.815748),
    "اليرموك": (24.808551, 46.781330), "غرناطة": (24.795695, 46.752491),
    "قرطبة": (24.815095, 46.730690), "الربيع": (24.795228, 46.660309),
    "السليمانية": (24.701301, 46.701164), "الصحافة": (24.799903, 46.637650),
    "العارض": (24.899049, 46.603661), "العقيق": (24.774188, 46.630268),
    "العليا": (24.697766, 46.687489), "الغدير": (24.773487, 46.653013),
    "المروج": (24.757432, 46.661940), "النرجس": (24.887475, 46.645718),
    "النفل": (24.781877, 46.673183), "الياسمين": (24.828287, 46.643143),
    "حطين": (24.762680, 46.600399), "الحزم": (24.538587, 46.646061),
    "الدار البيضاء": (24.564402, 46.791801), "الروابي": (24.695661, 46.790257),
    "الشفا": (24.564662, 46.700220), "المروة": (24.541163, 46.675844),
    "بدر": (24.524272, 46.727085), "طيبة": (24.543792, 46.829395),
    "عكاظ": (24.512714, 46.663914), "نمار": (24.568800, 46.677818),
    "السويدي": (24.591981, 46.673598), "سلطانة": (24.603792, 46.688676),
    "شبرا": (24.577308, 46.669235), "ظهرة لبن": (24.628917, 46.543636),
}

neighborhood_en_to_ar = {
    "al olaya": "العليا", "al-olaya": "العليا", "olaya": "العليا",
    "al malaz": "الملز", "al-malaz": "الملز", "malaz": "الملز",
    "al aqiq": "العقيق", "aqiq": "العقيق",
    "al sulaimaniyah": "السليمانية", "sulaimaniyah": "السليمانية",
    "al narjis": "النرجس", "narjis": "النرجس",
    "al yasmin": "الياسمين", "yasmin": "الياسمين",
    "al ghadir": "الغدير", "ghadir": "الغدير",
    "hittin": "حطين", "al muruj": "المروج", "muruj": "المروج",
    "al sahafa": "الصحافة", "sahafa": "الصحافة",
    "qurtubah": "قرطبة", "ghirnatah": "غرناطة",
    "al rabie": "الربيع", "al rawdah": "الروضة", "rawdah": "الروضة",
    "al yarmuk": "اليرموك", "al nahdah": "النهضة",
    "al nuzha": "النزهة", "al hamra": "الحمراء",
    "al khalij": "الخليج", "al suwaidi": "السويدي",
    "al shifa": "الشفا", "badr": "بدر",
    "sultana": "سلطانة", "shubra": "شبرا",
    "taybah": "طيبة", "ukaz": "عكاظ",
    "manfuhah": "منفوحة", "namar": "نمار",
}

categoryArabic = {
    "restaurant": "مطعم", "cafe": "كافيه", "supermarket": "سوبرماركت",
    "pharmacy": "صيدلية", "bakery": "مخبز", "gym": "نادي رياضي",
    "hotel": "فندق", "clothing": "محل ملابس", "electronics": "محل إلكترونيات",
    "furniture": "محل أثاث", "barber": "صالون حلاقة رجالي", "salon": "صالون نسائي",
    "gas_station": "محطة وقود", "laundry": "مغسلة ملابس", "jewelry": "محل مجوهرات",
    "grocery": "بقالة", "shoes": "محل أحذية", "sports_clothing": "محل ملابس رياضية",
    "curtains": "محل ستائر وسجاد", "lighting": "محل إضاءة", "sweets": "محل حلويات",
    "perfume": "محل عطور", "spa": "سبا", "auto_repair": "ورشة سيارات",
    "toys": "محل ألعاب أطفال", "pet_shop": "محل حيوانات أليفة",
    "gifts": "محل هدايا وزهور", "eyewear": "محل نظارات"
}

le = LabelEncoder()
df['category_encoded'] = le.fit_transform(df['category_en'])
region_map = {0: 'Central', 1: 'East', 2: 'North', 3: 'South', 4: 'West'}
df['region'] = df['region_encoded'].map(region_map)
region_dummies = pd.get_dummies(df['region'], prefix='region')
df = pd.concat([df, region_dummies], axis=1)
print('Model loaded successfully!')

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
    pair_rows = df[(df['category_en'] == category_name) & (df['neighborhood'] == neighborhood_name)]
    neighborhood_rows = df[df['neighborhood'] == neighborhood_name]
    category_rows = df[df['category_en'] == category_name]

    if len(pair_rows) > 0:
        base = pair_rows.mean(numeric_only=True)
    elif len(neighborhood_rows) > 0 and len(category_rows) > 0:
        base = (neighborhood_rows.mean(numeric_only=True) + category_rows.mean(numeric_only=True)) / 2
    elif len(neighborhood_rows) > 0:
        base = neighborhood_rows.mean(numeric_only=True)
    else:
        return None

    row = pd.DataFrame([base])
    row['category_encoded'] = df[df['category_en'] == category_name]['category_encoded'].iloc[0]
    row['neighborhood_success_rate'] = neighborhood_success_rate.get(neighborhood_name, df['success'].mean())
    row['category_success_rate'] = category_success_rate.get(category_name, df['success'].mean())
    row['transport_index'] = row['metro'] + row['bus'] + row['public_station']

    for col in feature_cols:
        if col not in row.columns:
            row[col] = 0
    return row[feature_cols]

def calculate_score(category_name, neighborhood_name):
    row = build_candidate_row(category_name, neighborhood_name)
    if row is None:
        return None

    ml_probability = xgboost_model.predict_proba(row)[0][1]
    values = row.iloc[0]

    demand_score = normalize_value(values['population_density'], df['population_density'].min(), df['population_density'].max())
    nearby_activity_score = normalize_value(values['nearby_all_businesses'], df['nearby_all_businesses'].min(), df['nearby_all_businesses'].max())
    transport_score = normalize_value(
        values['metro'] + values['bus'] + values['public_station'],
        (df['metro'] + df['bus'] + df['public_station']).min(),
        (df['metro'] + df['bus'] + df['public_station']).max()
    )
    market_strength_score = normalize_value(values['business_licenses'], df['business_licenses'].min(), df['business_licenses'].max())
    competition = values['competition_ratio']
    ideal_competition = df['competition_ratio'].median()
    if ideal_competition == 0:
        competition_score = 0.5
    else:
        competition_score = 1 - abs(competition - ideal_competition) / ideal_competition
        competition_score = max(0, min(1, competition_score))

    final_score = round((0.40 * ml_probability + 0.20 * demand_score + 0.15 * competition_score +
                         0.10 * nearby_activity_score + 0.10 * transport_score + 0.05 * market_strength_score) * 100, 2)
    label = 'مناسب جداً' if final_score >= 70 else 'مناسب' if final_score >= 50 else 'غير مناسب'

    return {
        'neighborhood': neighborhood_name, 'category': category_name,
        'final_score': final_score, 'label': label,
        'details': {
            'ml_probability': round(ml_probability * 100, 2),
            'demand_score': round(demand_score * 100, 2),
            'competition_score': round(competition_score * 100, 2),
            'nearby_activity_score': round(nearby_activity_score * 100, 2),
            'transport_score': round(transport_score * 100, 2),
            'market_strength_score': round(market_strength_score * 100, 2)
        }
    }

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
    data = request.json
    category = data.get('category', '').strip().lower()
    neighborhood = data.get('neighborhood', '').strip()
    if not category or not neighborhood:
        return jsonify({'error': 'category and neighborhood are required'}), 400
    if category not in df['category_en'].unique():
        return jsonify({'error': 'Category not found'}), 404
    if neighborhood not in df['neighborhood'].unique():
        return jsonify({'error': 'Neighborhood not found'}), 404
    result = calculate_score(category, neighborhood)
    if result is None:
        return jsonify({'error': 'Could not calculate score'}), 500
    return jsonify(convert_to_serializable(result))

@app.route('/api/rank', methods=['POST'])
def rank():
    data = request.json
    category = data.get('category', '').strip().lower()
    top_n = data.get('top_n', 10)
    if not category:
        return jsonify({'error': 'category is required'}), 400
    if category not in df['category_en'].unique():
        return jsonify({'error': 'Category not found'}), 404
    results = []
    for neighborhood in sorted(df['neighborhood'].unique()):
        score = calculate_score(category, neighborhood)
        if score:
            results.append(score)
    results = sorted(results, key=lambda x: x['final_score'], reverse=True)
    return jsonify(convert_to_serializable({'category': category, 'rankings': results[:top_n]}))

@app.route('/api/map/<category>', methods=['GET'])
def get_map(category):
    if category not in df['category_en'].unique():
        return jsonify({'error': 'Category not found'}), 404
    rankings = []
    for n in sorted(df['neighborhood'].unique()):
        s = calculate_score(category, n)
        if s:
            coords = centroid_dict.get(n)
            if coords:
                rankings.append({'neighborhood': n, 'final_score': s['final_score'], 'label': s['label'], 'lat': coords[0], 'lon': coords[1]})
    rankings = sorted(rankings, key=lambda x: x['final_score'], reverse=True)
    return jsonify(convert_to_serializable({'category': category, 'rankings': rankings}))

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    return jsonify({'reviews': load_reviews()})

@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json
    name = data.get('name', '').strip()
    rating = data.get('rating', 5)
    comment = data.get('comment', '').strip()
    role = data.get('role', '').strip()
    if not name or not comment:
        return jsonify({'error': 'name and comment required'}), 400
    save_review({'name': name, 'role': role, 'rating': rating, 'comment': comment})
    return jsonify({'success': True})

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    msg = data.get('msg', '').strip()
    if not name or not email or not msg:
        return jsonify({'error': 'all fields required'}), 400
    save_contact({'name': name, 'email': email, 'msg': msg})
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
        return jsonify({'contacts': []})

# ===== Chatbot Route مع Gemini =====
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question", "").strip()
    lang = data.get("lang", "ar")

    if not question:
        return jsonify({"answer": "الرجاء كتابة سؤال 😊"})

    if not client:
        return jsonify({"answer": "عذراً، خدمة المساعد غير متاحة حالياً 😅"})

    try:
        # كشف الحي
        detected_nb = None
        for n in df['neighborhood'].unique():
            if n in question:
                detected_nb = n
                break
        if not detected_nb:
            q_lower = question.lower()
            for en, ar in neighborhood_en_to_ar.items():
                if en in q_lower:
                    detected_nb = ar
                    break

        # كشف الفئة
        cat_keywords = {
            "restaurant": ["مطعم", "restaurant", "food", "اكل"],
            "cafe": ["كافيه", "cafe", "coffee", "قهوة"],
            "pharmacy": ["صيدلية", "pharmacy", "دواء"],
            "supermarket": ["سوبرماركت", "supermarket", "هايبر"],
            "gym": ["جيم", "gym", "نادي رياضي"],
            "grocery": ["بقالة", "grocery"],
            "clothing": ["ملابس", "clothing", "fashion"],
            "bakery": ["مخبز", "bakery", "خبز"],
            "sweets": ["حلويات", "sweets", "dessert"],
            "salon": ["صالون", "salon", "beauty"],
            "hotel": ["فندق", "hotel"],
            "pharmacy": ["صيدلية", "pharmacy"],
            "jewelry": ["مجوهرات", "jewelry", "ذهب"],
            "shoes": ["أحذية", "shoes"],
            "perfume": ["عطور", "perfume"],
            "spa": ["سبا", "spa"],
        }
        detected_cat = None
        for cat, kws in cat_keywords.items():
            for kw in kws:
                if kw in question.lower():
                    detected_cat = cat
                    break
            if detected_cat:
                break

        # بناء context من البيانات الحقيقية
        forsati_context = ""

        if detected_nb and detected_cat:
            result = calculate_score(detected_cat, detected_nb)
            if result:
                d = result['details']
                forsati_context = f"""
بيانات حقيقية من نموذج فرصتي (XGBoost):
- الحي: {detected_nb}
- النشاط: {categoryArabic.get(detected_cat, detected_cat)}
- الدرجة الكلية: {result['final_score']}/100
- التصنيف: {result['label']}
- تفاصيل:
  * توقع النموذج: {d['ml_probability']}%
  * الطلب والكثافة السكانية: {d['demand_score']}%
  * مستوى المنافسة: {d['competition_score']}%
  * النشاط التجاري القريب: {d['nearby_activity_score']}%
  * المواصلات: {d['transport_score']}%
  * قوة السوق: {d['market_strength_score']}%
"""

        elif detected_cat and not detected_nb:
            results = []
            for n in sorted(df['neighborhood'].unique()):
                s = calculate_score(detected_cat, n)
                if s:
                    results.append(s)
            results = sorted(results, key=lambda x: x['final_score'], reverse=True)[:3]
            if results:
                top_list = "\n".join([f"  {i+1}. {r['neighborhood']}: {r['final_score']}/100 ({r['label']})"
                                      for i, r in enumerate(results)])
                forsati_context = f"""
بيانات حقيقية من نموذج فرصتي:
أفضل 3 أحياء لـ {categoryArabic.get(detected_cat, detected_cat)}:
{top_list}
"""

        elif detected_nb and not detected_cat:
            result = calculate_score("restaurant", detected_nb)
            if result:
                d = result['details']
                forsati_context = f"""
بيانات حقيقية عن حي {detected_nb}:
- مستوى المنافسة: {d['competition_score']}%
- الكثافة السكانية: {d['demand_score']}%
- المواصلات: {d['transport_score']}%
- النشاط التجاري القريب: {d['nearby_activity_score']}%
- قوة السوق: {d['market_strength_score']}%
"""

        # كشف أسئلة منافسة ومواصلات
        competition_keywords = ["أقل منافسة", "منافسة قليلة", "least competition", "low competition", "منافسة منخفضة", "أعلى منافسة", "highest competition"]
        transport_keywords = ["مواصلات", "مترو", "باص", "transport", "metro", "bus"]

        if any(kw in question for kw in competition_keywords) and not forsati_context:
            cat = detected_cat or "restaurant"
            hood_scores = []
            for n in sorted(df['neighborhood'].unique()):
                hood_data = df[(df['neighborhood'] == n) & (df['category_en'] == cat)]
                if len(hood_data) > 0:
                    comp_ratio = hood_data['competition_ratio'].mean()
                    hood_scores.append({'neighborhood': n, 'competition_ratio': round(comp_ratio, 4)})

            if any(w in question for w in ["أعلى", "أكثر", "highest", "most", "عالية"]):
                hood_scores = sorted(hood_scores, key=lambda x: x['competition_ratio'], reverse=True)[:5]
                forsati_context = f"أعلى أحياء منافسة لـ{categoryArabic.get(cat, cat)}:\n"
            else:
                hood_scores = sorted(hood_scores, key=lambda x: x['competition_ratio'])[:5]
                forsati_context = f"أقل أحياء منافسة لـ{categoryArabic.get(cat, cat)}:\n"

            forsati_context += "\n".join([f"  {i+1}. {h['neighborhood']}: {h['competition_ratio']}" for i, h in enumerate(hood_scores)])

        elif any(kw in question for kw in transport_keywords) and not forsati_context:
            transport_data = df.groupby('neighborhood')[['metro', 'bus', 'public_station']].mean()
            transport_data['total'] = transport_data['metro'] + transport_data['bus'] + transport_data['public_station']
            top_transport = transport_data.nlargest(5, 'total').reset_index()
            forsati_context = "أفضل أحياء من ناحية المواصلات:\n"
            forsati_context += "\n".join([f"  {i+1}. {row['neighborhood']}: مترو={row['metro']:.0f}, باص={row['bus']:.0f}"
                                          for i, row in top_transport.iterrows()])

        system_prompt = f"""أنت مساعد فرصتي الذكي، منصة متخصصة في تحليل أفضل مواقع الأعمال التجارية في الرياض.
تعتمد على نموذج XGBoost مدرّب على بيانات حقيقية من 60 حياً و28 فئة تجارية.

{forsati_context}

تعليمات:
- أجب بنفس لغة المستخدم (عربي أو إنجليزي)
- استخدم البيانات الحقيقية أعلاه إذا كانت متوفرة
- اشرح التوصية بشكل واضح ومفيد
- إذا الدرجة أقل من 50، اقترح أحياء بديلة
- إذا السؤال خارج نطاق أحياء الرياض، اعتذر بلطف
- لا تخترع أرقاماً، استخدم البيانات الحقيقية فقط"""

        response = client.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=f"{system_prompt}\n\nسؤال المستخدم: {question}",
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2000,
            )
        )
        return jsonify({"answer": response.text, "sources": [detected_nb] if detected_nb else []})

    except Exception as e:
        print("Gemini error:", e)
        return jsonify({"answer": "صار خطأ في المساعد الذكي 😅"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)