# ============================================================
# مشروع فرصتي - Flask API
# ============================================================
from flask_sqlalchemy import SQLAlchemy
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')

import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///forsati.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

# ===== Database Models =====

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100))
    rating = db.Column(db.Integer, default=5)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    msg = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50))

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


print('Loading model...')
with open('forsati_model_v2.pkl', 'rb') as f:
    saved = pickle.load(f)

model        = saved['model']
feature_cols = saved['features']

df = pd.read_csv('forsati_final_dataset.csv')

# Feature Engineering — نفس اللي في النموذج الجديد
df['category_share'] = df['category_count'] / (df['total_businesses'] + 1)
df['pop_per_business'] = df['Population'] / (df['total_businesses'] + 1)
df['transport_index'] = df['metro'] + df['bus'] + df['public_station']
df['nearby_competition_density'] = df['nearby_same_category'] / (df['nearby_all_businesses'] + 1)
df['economic_index'] = df['annual_transactions'] / (df['Population'] + 1)
df['pop_density_per_km2'] = df['Population'] / (df['Area_km2'] + 0.01)
 
# Target Encoding — نفس اللي في النموذج الجديد
neighborhood_success_rate = df.groupby('neighborhood')['success'].mean()
df['neighborhood_success_rate'] = df['neighborhood'].map(neighborhood_success_rate)
df['neighborhood_success_rate'] = df['neighborhood_success_rate'].fillna(df['success'].mean())
 
category_success_rate = df.groupby('category_en')['success'].mean()
df['category_success_rate'] = df['category_en'].map(category_success_rate)
df['category_success_rate'] = df['category_success_rate'].fillna(df['success'].mean())

centroid_dict = {
    "الجرادية": (24.615341, 46.698203),
    "الدريهمية": (24.589588, 46.696444),
    "الشميسي": (24.624860, 46.699920),
    "الصالحية": (24.638578, 46.732876),
    "الصفا": (24.666518, 46.765194),
    "الضباط": (24.700599, 46.717772),
    "العزيزية": (24.588807, 46.769314),
    "العمل": (24.645886, 46.722836),
    "الفوطة": (24.641439, 46.710134),
    "المربع": (24.659888, 46.708374),
    "المرقب": (24.635705, 46.723309),
    "المعذر": (24.667454, 46.672583),
    "الملز": (24.662696, 46.734810),
    "المنصورة": (24.608786, 46.742449),
    "الوزارات": (24.678218, 46.713781),
    "الوشام": (24.642024, 46.697774),
    "اليمامة": (24.595363, 46.716657),
    "عليشة": (24.631765, 46.685586),
    "منفوحة": (24.599812, 46.728630),
    "الحمراء": (24.775513, 46.752748),
    "الخليج": (24.776760, 46.803989),
    "الروضة": (24.734541, 46.767540),
    "السعادة": (24.695791, 46.840067),
    "السلام": (24.707175, 46.811314),
    "السلي": (24.650190, 46.844559),
    "الفيحاء": (24.682143, 46.811571),
    "القدس": (24.755042, 46.754837),
    "المونسية": (24.832545, 46.769485),
    "النزهة": (24.756886, 46.708374),
    "النسيم الشرقي": (24.740439, 46.846390),
    "النسيم الغربي": (24.725160, 46.821327),
    "النهضة": (24.760549, 46.815748),
    "اليرموك": (24.808551, 46.781330),
    "غرناطة": (24.795695, 46.752491),
    "قرطبة": (24.815095, 46.730690),
    "الربيع": (24.795228, 46.660309),
    "السليمانية": (24.701301, 46.701164),
    "الصحافة": (24.799903, 46.637650),
    "العارض": (24.899049, 46.603661),
    "العقيق": (24.774188, 46.630268),
    "العليا": (24.697766, 46.687489),
    "الغدير": (24.773487, 46.653013),
    "المروج": (24.757432, 46.661940),
    "النرجس": (24.887475, 46.645718),
    "النفل": (24.781877, 46.673183),
    "الياسمين": (24.828287, 46.643143),
    "حطين": (24.762680, 46.600399),
    "الحزم": (24.538587, 46.646061),
    "الدار البيضاء": (24.564402, 46.791801),
    "الروابي": (24.695661, 46.790257),
    "الشفا": (24.564662, 46.700220),
    "المروة": (24.541163, 46.675844),
    "بدر": (24.524272, 46.727085),
    "طيبة": (24.543792, 46.829395),
    "عكاظ": (24.512714, 46.663914),
    "نمار": (24.568800, 46.677818),
    "السويدي": (24.591981, 46.673598),
    "سلطانة": (24.603792, 46.688676),
    "شبرا": (24.577308, 46.669235),
    "ظهرة لبن": (24.628917, 46.543636),
}

# ===== خريطة الأسماء الإنجليزية للأحياء =====
neighborhood_en_to_ar = {
    "al olaya": "العليا", "al-olaya": "العليا", "olaya": "العليا",
    "al malaz": "الملز", "al-malaz": "الملز", "malaz": "الملز",
    "al aqiq": "العقيق", "al-aqiq": "العقيق", "aqiq": "العقيق",
    "al sulaimaniyah": "السليمانية", "sulaimaniyah": "السليمانية", "sulamaniyah": "السليمانية",
    "al narjis": "النرجس", "narjis": "النرجس",
    "al yasmin": "الياسمين", "yasmin": "الياسمين",
    "al ghadir": "الغدير", "ghadir": "الغدير",
    "hittin": "حطين", "al hittin": "حطين",
    "al muruj": "المروج", "muruj": "المروج",
    "al sahafa": "الصحافة", "sahafa": "الصحافة",
    "qurtubah": "قرطبة", "al qurtubah": "قرطبة",
    "ghirnatah": "غرناطة", "al ghirnatah": "غرناطة",
    "al rabie": "الربيع", "rabie": "الربيع",
    "al rawabi": "الروابي", "rawabi": "الروابي",
    "dhahrat laban": "ظهرة لبن", "laban": "ظهرة لبن",
    "al nafil": "النفل", "nafil": "النفل",
    "al dar al baida": "الدار البيضاء", "dar al baida": "الدار البيضاء",
    "al rawdah": "الروضة", "rawdah": "الروضة",
    "al munsiyah": "المونسية", "munsiyah": "المونسية",
    "al nasim al sharqi": "النسيم الشرقي",
    "al nasim al gharbi": "النسيم الغربي", "nasim": "النسيم الشرقي",
    "al yarmuk": "اليرموك", "yarmuk": "اليرموك",
    "al yamamah": "اليمامة", "yamamah": "اليمامة",
    "al wazarat": "الوزارات", "wazarat": "الوزارات",
    "al wisham": "الوشام", "wisham": "الوشام",
    "al aziziyah": "العزيزية", "aziziyah": "العزيزية",
    "al mansurah": "المنصورة", "mansurah": "المنصورة",
    "al malqa": "الملقا", "malqa": "الملقا",
    "al muadhar": "المعذر", "muadhar": "المعذر",
    "al nahdah": "النهضة", "nahdah": "النهضة",
    "al nuzha": "النزهة", "nuzha": "النزهة",
    "al jaradiyah": "الجرادية", "jaradiyah": "الجرادية",
    "al duraihimiyah": "الدريهمية", "duraihimiyah": "الدريهمية",
    "al shumaisi": "الشميسي", "shumaisi": "الشميسي",
    "al hamra": "الحمراء", "hamra": "الحمراء",
    "al khalij": "الخليج", "khalij": "الخليج",
    "al saadah": "السعادة", "saadah": "السعادة",
    "al salam": "السلام", "salam": "السلام",
    "al sali": "السلي", "sali": "السلي",
    "al suwaidi": "السويدي", "suwaidi": "السويدي",
    "al shifa": "الشفا", "shifa": "الشفا",
    "al salhiyah": "الصالحية", "salhiyah": "الصالحية",
    "al safa": "الصفا", "safa": "الصفا",
    "al dubbat": "الضباط", "dubbat": "الضباط",
    "al arid": "العارض", "arid": "العارض",
    "al futah": "الفوطة", "futah": "الفوطة",
    "al fayha": "الفيحاء", "fayha": "الفيحاء",
    "al quds": "القدس", "quds": "القدس",
    "al murabbaa": "المربع", "murabbaa": "المربع",
    "al marqab": "المرقب", "marqab": "المرقب",
    "al marwah": "المروة", "marwah": "المروة",
    "al hazm": "الحزم", "hazm": "الحزم",
    "badr": "بدر",
    "sultana": "سلطانة",
    "shubra": "شبرا",
    "taybah": "طيبة", "taiba": "طيبة",
    "ukaz": "عكاظ",
    "ulaisha": "عليشة",
    "manfuhah": "منفوحة",
    "namar": "نمار",
    "salihiyah": "الصالحية",
}

le = LabelEncoder()
df['category_encoded'] = le.fit_transform(df['category_en'])

region_map = {0: 'Central', 1: 'East', 2: 'North', 3: 'South', 4: 'West'}
df['region'] = df['region_encoded'].map(region_map)
region_dummies = pd.get_dummies(df['region'], prefix='region')
df = pd.concat([df, region_dummies], axis=1)

print('Model loaded successfully!')


def normalize_value(value, min_value, max_value):
    if max_value == min_value:
        return 0.5
    return (value - min_value) / (max_value - min_value)


def build_candidate_row(category_name, neighborhood_name):
    pair_rows = df[
        (df['category_en'] == category_name) &
        (df['neighborhood'] == neighborhood_name)
    ]
    neighborhood_rows = df[df['neighborhood'] == neighborhood_name]
    category_rows     = df[df['category_en'] == category_name]
 
    if len(pair_rows) > 0:
        base = pair_rows.mean(numeric_only=True)
    elif len(neighborhood_rows) > 0 and len(category_rows) > 0:
        base = (neighborhood_rows.mean(numeric_only=True) + category_rows.mean(numeric_only=True)) / 2
    elif len(neighborhood_rows) > 0:
        base = neighborhood_rows.mean(numeric_only=True)
    else:
        return None
 
    row = pd.DataFrame([base])
 
    # Restore encodings
    row['category_encoded'] = df[df['category_en'] == category_name]['category_encoded'].iloc[0]
    row['neighborhood_success_rate'] = neighborhood_success_rate.get(neighborhood_name, df['success'].mean())
    row['category_success_rate']     = category_success_rate.get(category_name, df['success'].mean())
 
    # Recompute engineered features
    row['transport_index'] = row['metro'] + row['bus'] + row['public_station']
 
    for col in feature_cols:
        if col not in row.columns:
            row[col] = 0
 
    return row[feature_cols]


def calculate_score(category_name, neighborhood_name):
    row = build_candidate_row(category_name, neighborhood_name)
    if row is None:
        return None

    ml_probability = model.predict_proba(row)[0][1]
    values = row.iloc[0]

    demand_score = normalize_value(
        values['population_density'],
        df['population_density'].min(),
        df['population_density'].max()
    )
    nearby_activity_score = normalize_value(
        values['nearby_all_businesses'],
        df['nearby_all_businesses'].min(),
        df['nearby_all_businesses'].max()
    )
    transport_score = normalize_value(
        values['metro'] + values['bus'] + values['public_station'],
        (df['metro'] + df['bus'] + df['public_station']).min(),
        (df['metro'] + df['bus'] + df['public_station']).max()
    )
    market_strength_score = normalize_value(
        values['business_licenses'],
        df['business_licenses'].min(),
        df['business_licenses'].max()
    )
    competition = values['competition_ratio']
    ideal_competition = df['competition_ratio'].median()
    if ideal_competition == 0:
        competition_score = 0.5
    else:
        competition_score = 1 - abs(competition - ideal_competition) / ideal_competition
        competition_score = max(0, min(1, competition_score))

    final_score = (
        0.40 * ml_probability +
        0.20 * demand_score +
        0.15 * competition_score +
        0.10 * nearby_activity_score +
        0.10 * transport_score +
        0.05 * market_strength_score
    )
    final_score = round(final_score * 100, 2)

    label = 'مناسب جداً' if final_score >= 70 else 'مناسب' if final_score >= 50 else 'غير مناسب'

    return {
        'neighborhood': neighborhood_name,
        'category': category_name,
        'final_score': final_score,
        'label': label,
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

    neighborhoods = sorted(df['neighborhood'].unique())
    results = []
    for neighborhood in neighborhoods:
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
                rankings.append({
                    'neighborhood': n,
                    'final_score': s['final_score'],
                    'label': s['label'],
                    'lat': coords[0],
                    'lon': coords[1],
                })

    rankings = sorted(rankings, key=lambda x: x['final_score'], reverse=True)
    return jsonify(convert_to_serializable({'category': category, 'rankings': rankings}))

# جلب التعليقات
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    reviews = Review.query.order_by(Review.id.desc()).all()

    result = []

    for r in reviews:
        result.append({
            'id': r.id,
            'name': r.name,
            'role': r.role,
            'rating': r.rating,
            'comment': r.comment,
            'date': r.date
        })

    return jsonify({'reviews': result})

# إضافة تعليق
@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json

    name = data.get('name', '').strip()
    rating = data.get('rating', 5)
    comment = data.get('comment', '').strip()
    role = data.get('role', '').strip()

    if not name or not comment:
        return jsonify({'error': 'name and comment required'}), 400

    review = Review(
        name=name,
        role=role,
        rating=rating,
        comment=comment,
        date=datetime.now().strftime('%Y-%m-%d')
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({'success': True})

# ===== Contact Route =====
@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    msg = data.get('msg', '').strip()

    if not name or not email or not msg:
        return jsonify({'error': 'all fields required'}), 400

    contact_entry = Contact(
        name=name,
        email=email,
        msg=msg,
        date=datetime.now().strftime('%Y-%m-%d %H:%M')
    )

    db.session.add(contact_entry)
    db.session.commit()

    return jsonify({'success': True})

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    contacts = Contact.query.order_by(Contact.id.desc()).all()

    result = []

    for c in contacts:
        result.append({
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'msg': c.msg,
            'date': c.date
        })

    return jsonify({'contacts': result})

# ===== Chatbot =====

neighborhoodEnglish = {
    "الجرادية": "Al-Jaradia", "الدريهمية": "Al-Duraihimiyah",
    "الشميسي": "Al-Shamisiyah", "الصالحية": "Al-Salihiyah",
    "الصفا": "Al-Safa", "الضباط": "Al-Dabbat",
    "العزيزية": "Al-Aziziyah", "العمل": "Al-Amal",
    "الفوطة": "Al-Fawwaz", "المربع": "Al-Murabba",
    "المرقب": "Al-Marqab", "المعذر": "Al-Muathar",
    "الملز": "Al-Malaz", "المنصورة": "Al-Mansurah",
    "الوزارات": "Al-Wizarat", "الوشام": "Al-Wisham",
    "اليمامة": "Al-Yamamah", "عليشة": "Ulayshah",
    "منفوحة": "Manfuhah", "الحمراء": "Al-Hamra",
    "الخليج": "Al-Khalij", "الروضة": "Al-Rawdah",
    "السعادة": "Al-Saadah", "السلام": "Al-Salam",
    "السلي": "Al-Sali", "الفيحاء": "Al-Fayha",
    "القدس": "Al-Quds", "المونسية": "Al-Munsiyah",
    "النزهة": "Al-Nuzhah", "النسيم الشرقي": "Al-Naseem East",
    "النسيم الغربي": "Al-Naseem West", "النهضة": "Al-Nahdah",
    "اليرموك": "Al-Yarmuk", "غرناطة": "Gharnata",
    "قرطبة": "Qurtubah", "الربيع": "Al-Rabi",
    "السليمانية": "Al-Sulaymaniyah", "الصحافة": "Al-Sahafah",
    "العارض": "Al-Arid", "العقيق": "Al-Aqiq",
    "العليا": "Al-Olaya", "الغدير": "Al-Ghadir",
    "المروج": "Al-Muruj", "النرجس": "Al-Narjis",
    "النفل": "Al-Nafal", "الياسمين": "Al-Yasmin",
    "حطين": "Hittin", "الحزم": "Al-Hazm",
    "الدار البيضاء": "Al-Dar Al-Baida", "الروابي": "Al-Rawabi",
    "الشفا": "Al-Shafa", "المروة": "Al-Marwah",
    "بدر": "Badr", "طيبة": "Taybah",
    "عكاظ": "Ukaz", "نمار": "Namar",
    "السويدي": "Al-Suwaidi", "سلطانة": "Sultanah",
    "شبرا": "Shubra", "ظهرة لبن": "Dhahrat Laban",
}

def translate_neighborhood(name, lang):
    if lang == "en":
        return neighborhoodEnglish.get(name, name)
    return name

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

categoryKeywords = {
    "restaurant": ["مطعم", "اكل", "طعام", "أكل", "وجبة", "مأكولات", "restaurant", "food", "meal", "dining", "eat"],
    "cafe": ["كافيه", "كافيهات", "قهوة", "كوفي", "cafe", "coffee", "coffee shop", "coffeehouse"],
    "pharmacy": ["صيدلية", "دواء", "أدوية", "pharmacy", "drugstore", "medicine", "chemist"],
    "supermarket": ["سوبرماركت", "هايبر", "supermarket", "grocery store", "market", "hypermarket"],
    "gym": ["جيم", "نادي رياضي", "رياضة", "gym", "fitness", "sports club", "workout"],
    "grocery": ["بقالة", "دكان", "grocery", "corner shop", "groceries"],
    "clothing": ["ملابس", "موضة", "عباية", "clothing", "fashion", "clothes", "apparel", "wear"],
    "salon": ["صالون نسائي", "تجميل", "كوافير", "salon", "beauty", "hair salon", "beauty salon"],
    "barber": ["حلاقة", "حلاق", "صالون رجالي", "barber", "barbershop", "haircut"],
    "gas_station": ["وقود", "محطة وقود", "بنزين", "gas station", "fuel", "petrol", "filling station"],
    "sweets": ["حلويات", "حلا", "كيك", "sweets", "dessert", "pastry", "candy"],
    "electronics": ["الكترونيات", "جوالات", "أجهزة", "electronics", "phones", "gadgets", "appliances"],
    "perfume": ["عطور", "عطر", "perfume", "fragrance", "scent"],
    "spa": ["سبا", "مساج", "spa", "massage", "wellness"],
    "bakery": ["مخبز", "خبز", "bakery", "bread", "baker"],
    "jewelry": ["مجوهرات", "ذهب", "jewelry", "jewellery", "gold", "diamonds"],
    "shoes": ["أحذية", "حذاء", "shoes", "footwear", "sneakers"],
    "furniture": ["أثاث", "اثاث", "furniture", "home decor", "furnishings"],
    "hotel": ["فندق", "فنادق", "hotel", "lodging", "accommodation", "inn"],
    "toys": ["ألعاب", "العاب اطفال", "toys", "children toys", "play"],
    "pet_shop": ["حيوانات", "بيت الحيوان", "pet shop", "pet store", "animals", "pets"],
    "gifts": ["هدايا", "زهور", "gifts", "flowers", "presents", "gift shop"],
    "eyewear": ["نظارات", "عيون", "eyewear", "glasses", "optician", "spectacles"],
    "laundry": ["مغسلة", "غسيل", "laundry", "dry cleaning", "wash"],
    "curtains": ["ستائر", "سجاد", "curtains", "carpets", "blinds", "rugs"],
    "lighting": ["إضاءة", "اضاءة", "lighting", "lights", "lamps"],
    "sports_clothing": ["ملابس رياضية", "رياضي", "sports clothing", "activewear", "sportswear", "athletic"],
    "auto_repair": ["ورشة", "سيارات", "صيانة سيارات", "auto repair", "car repair", "mechanic", "garage"],
}

def detect_category(text):
    text_lower = text.lower()
    for cat, keywords in categoryKeywords.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return cat
    return None

def detect_neighborhood(text):
    # 1. بحث مباشر بالعربي
    for n in df['neighborhood'].unique():
        if n in text:
            return n
    # 2. بحث بالإنجليزي من الـ mapping
    text_lower = text.lower()
    for en_name, ar_name in neighborhood_en_to_ar.items():
        if en_name in text_lower:
            return ar_name
    return None


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question", "").strip()
    lang = data.get("lang", "ar")
    q = question.lower()
    answer = ""
    sources = []

    category = detect_category(question)

    # استخراج كل الأحياء المذكورة في السؤال (للمقارنة)
    all_neighborhoods = []
    for n in df['neighborhood'].unique():
        if n in question:
            all_neighborhoods.append(n)
    # بحث بالإنجليزي كمان
    for en_name, ar_name in neighborhood_en_to_ar.items():
        if en_name in q and ar_name not in all_neighborhoods:
            all_neighborhoods.append(ar_name)

    neighborhood = all_neighborhoods[0] if all_neighborhoods else None

    # ============================================
    # مقارنة بين حيين
    # ============================================
    if len(all_neighborhoods) >= 2 and any(w in q for w in ["مقارنة", "قارن", "أفضل من", "احسن من", "versus", "vs", "compare", "or", "او", "أو"]):
        n1 = all_neighborhoods[0]
        n2 = all_neighborhoods[1]
        cat = category or "restaurant"
        cat_ar = categoryArabic.get(cat, cat)

        r1 = calculate_score(cat, n1)
        r2 = calculate_score(cat, n2)

        if r1 and r2:
            winner = n1 if r1['final_score'] > r2['final_score'] else n2
            d1 = r1['details']
            d2 = r2['details']

            if lang == "ar":
                answer = f"مقارنة بين {n1} و {n2} لـ{cat_ar} ⚖️\n\n"
                answer += f"🏘️ {n1} — {r1['final_score']}/100\n"
                answer += f"   🤖 النموذج: {d1['ml_probability']}%\n"
                answer += f"   👥 الطلب: {d1['demand_score']}%\n"
                answer += f"   ⚖️ المنافسة: {d1['competition_score']}%\n"
                answer += f"   🚇 النقل: {d1['transport_score']}%\n\n"
                answer += f"🏘️ {n2} — {r2['final_score']}/100\n"
                answer += f"   🤖 النموذج: {d2['ml_probability']}%\n"
                answer += f"   👥 الطلب: {d2['demand_score']}%\n"
                answer += f"   ⚖️ المنافسة: {d2['competition_score']}%\n"
                answer += f"   🚇 النقل: {d2['transport_score']}%\n\n"
                answer += f"🏆 الفائز: حي {winner}!"
            else:
                answer = f"Comparing {n1} vs {n2} for {cat} ⚖️\n\n"
                answer += f"🏘️ {n1} — {r1['final_score']}/100\n"
                answer += f"   🤖 Model: {d1['ml_probability']}%\n"
                answer += f"   👥 Demand: {d1['demand_score']}%\n"
                answer += f"   ⚖️ Competition: {d1['competition_score']}%\n"
                answer += f"   🚇 Transit: {d1['transport_score']}%\n\n"
                answer += f"🏘️ {n2} — {r2['final_score']}/100\n"
                answer += f"   🤖 Model: {d2['ml_probability']}%\n"
                answer += f"   👥 Demand: {d2['demand_score']}%\n"
                answer += f"   ⚖️ Competition: {d2['competition_score']}%\n"
                answer += f"   🚇 Transit: {d2['transport_score']}%\n\n"
                answer += f"🏆 Winner: {winner}!"
            sources = [n1, n2]
            return jsonify({"answer": answer, "sources": sources})

    # ============================================
    # تحية
    # ============================================
    if any(w in q for w in ["مرحبا", "هلا", "السلام", "اهلا", "هاي", "hi", "hello", "hey", "good morning", "good evening"]):
        answer = "مرحباً! أنا مساعد فرصتي 🤖\nاسألني عن أي نشاط تجاري وأساعدك تختار أفضل حي في الرياض!\n\nمثلاً:\n• وين أفضل حي لمطعم؟\n• هل حي العليا مناسب لصيدلية؟\n• أي حي فيه أقل منافسة؟" if lang == "ar" else "Hello! I'm Forsati's assistant 🤖\nAsk me about any business and I'll help you find the best neighborhood in Riyadh!"

    # ============================================
    # شكراً
    # ============================================
    elif any(w in q for w in ["شكرا", "شكراً", "مشكور", "يسلمو", "thanks", "thank you", "thx"]):
        answer = "العفو! أي خدمة ثانية؟ 😊" if lang == "ar" else "You're welcome! Anything else? 😊"

    # ============================================
    # ما هو فرصتي / عن المشروع
    # ============================================
    elif any(w in q for w in ["ما هو", "وش هو", "عن", "فرصتي", "المشروع", "what is forsati", "about"]):
        answer = "فرصتي 🎯 هي منصة ذكية تساعد رواد الأعمال على اختيار أفضل موقع لمشروعهم في الرياض.\n\nنستخدم:\n🤖 نموذج XGBoost مدرّب على بيانات حقيقية\n📊 تحليل الكثافة السكانية والمنافسة\n🚇 تقييم وسائل النقل والنشاط التجاري\n\nالنتيجة: درجة من 100 تخبرك إذا الحي مناسب لمشروعك!" if lang == "ar" else "Forsati 🎯 is a smart platform that helps entrepreneurs choose the best location for their business in Riyadh using XGBoost ML model trained on real data."

    # ============================================
    # حي محدد + فئة محددة
    # ============================================
    elif category and neighborhood:
        result = calculate_score(category, neighborhood)
        if result:
            score = result['final_score']
            d = result['details']
            cat_ar = categoryArabic.get(category, category)
            if score >= 70:
                verdict = "مناسب جداً ✅" if lang == "ar" else "Highly Suitable ✅"
                intro = f"حي {neighborhood} خيار ممتاز لـ{cat_ar}! 🎯" if lang == "ar" else f"{neighborhood} is an excellent choice! 🎯"
            elif score >= 50:
                verdict = "مناسب 🟡" if lang == "ar" else "Suitable 🟡"
                intro = f"حي {neighborhood} فيه إمكانية لـ{cat_ar}." if lang == "ar" else f"{neighborhood} has potential."
            else:
                verdict = "غير مناسب ❌" if lang == "ar" else "Not Suitable ❌"
                intro = f"حي {neighborhood} مو مثالي لـ{cat_ar}." if lang == "ar" else f"{neighborhood} is not ideal."

            if lang == "ar":
                answer = f"{intro}\n\n📊 الدرجة الكلية: {score}/100 — {verdict}\n\nتفاصيل التقييم:\n🤖 توقع النموذج: {d['ml_probability']}%\n👥 الطلب والكثافة: {d['demand_score']}%\n⚖️ مستوى المنافسة: {d['competition_score']}%\n🏪 النشاط التجاري القريب: {d['nearby_activity_score']}%\n🚇 المواصلات: {d['transport_score']}%\n📈 قوة السوق: {d['market_strength_score']}%"
            else:
                answer = f"{intro}\n\n📊 Overall Score: {score}/100 — {verdict}\n\nBreakdown:\n🤖 Model: {d['ml_probability']}%\n👥 Demand: {d['demand_score']}%\n⚖️ Competition: {d['competition_score']}%\n🏪 Nearby Activity: {d['nearby_activity_score']}%\n🚇 Transport: {d['transport_score']}%\n📈 Market: {d['market_strength_score']}%"
            sources = [neighborhood]

    # ============================================
    # حي محدد بدون فئة
    # ============================================
    elif neighborhood and not category:
        result = calculate_score("restaurant", neighborhood)
        if result:
            d = result['details']
            if lang == "ar":
                answer = f"معلومات عن حي {neighborhood} 📍\n\n⚖️ مستوى المنافسة: {d['competition_score']}%\n👥 الكثافة السكانية: {d['demand_score']}%\n🚇 المواصلات: {d['transport_score']}%\n🏪 النشاط التجاري: {d['nearby_activity_score']}%\n📈 قوة السوق: {d['market_strength_score']}%\n\nأخبرني نوع مشروعك وأعطيك تقييم أدق! 😊"
            else:
                answer = f"Info about {neighborhood} 📍\n\n⚖️ Competition: {d['competition_score']}%\n👥 Density: {d['demand_score']}%\n🚇 Transport: {d['transport_score']}%\n🏪 Activity: {d['nearby_activity_score']}%\n📈 Market: {d['market_strength_score']}%"
            sources = [neighborhood]

    # ============================================
    # فئة محددة بدون حي — أفضل الأحياء
    # ============================================
    elif category and not neighborhood:
        cat_ar = categoryArabic.get(category, category)
        results = []
        for n in sorted(df['neighborhood'].unique()):
            s = calculate_score(category, n)
            if s:
                results.append(s)
        results = sorted(results, key=lambda x: x['final_score'], reverse=True)[:3]
        medals = ["🥇", "🥈", "🥉"]
        if lang == "ar":
            answer = f"أفضل الأحياء لـ{cat_ar} في الرياض 🏆\n\n"
            for i, r in enumerate(results):
                d = r['details']
                answer += f"{medals[i]} {r['neighborhood']} — {r['final_score']}/100\n"
                answer += f"   👥 الطلب: {d['demand_score']}% | ⚖️ المنافسة: {d['competition_score']}% | 🚇 النقل: {d['transport_score']}%\n\n"
            answer += "تقدر تشوف تفاصيل أكثر من البحث في الموقع! 😊"
        else:
            answer = f"Best neighborhoods for a {category} in Riyadh 🏆\n\n"
            for i, r in enumerate(results):
                d = r['details']
                answer += f"{medals[i]} {r['neighborhood']} — {r['final_score']}/100\n"
                answer += f"   👥 Demand: {d['demand_score']}% | ⚖️ Competition: {d['competition_score']}% | 🚇 Transit: {d['transport_score']}%\n\n"
        sources = [r['neighborhood'] for r in results]

    # ============================================
    # المنافسة (بدون فئة أو حي)
    # ============================================
    elif any(w in q for w in ["منافسة", "تنافس", "منافس", "زحمة", "competition", "compete"]):
        results = []
        for n in df["neighborhood"].unique():
            s = calculate_score("restaurant", n)
            if s:
                results.append({"neighborhood": n, "competition": s["details"]["competition_score"]})

        if any(w in q for w in ["عالية", "مرتفعة", "قوية", "أكثر", "أعلى", "اعلى", "highest", "most", "high"]):
            results = sorted(results, key=lambda x: x["competition"], reverse=True)[:3]
            answer = "الأحياء الأعلى بالمنافسة:\n" if lang == "ar" else "Most competitive neighborhoods:\n"
        else:
            results = sorted(results, key=lambda x: x["competition"])[:3]
            answer = "الأحياء الأقل بالمنافسة:\n" if lang == "ar" else "Least competitive neighborhoods:\n"

        for r in results:
            answer += f"- {r['neighborhood']} ({r['competition']}%)\n"
        sources = [r["neighborhood"] for r in results]

    # ============================================
    # الكثافة السكانية
    # ============================================
    elif any(w in q for w in ["كثافة", "سكان", "سكانية", "population", "density", "crowded"]):
        if any(w in q for w in ["أقل", "اقل", "منخفض", "lowest", "low", "least"]):
            top = df.groupby("neighborhood")["population_density"].mean().sort_values(ascending=True).head(3)
            answer = "الأحياء الأقل كثافة سكانية:\n" if lang == "ar" else "Least populated neighborhoods:\n"
        else:
            top = df.groupby("neighborhood")["population_density"].mean().sort_values(ascending=False).head(3)
            answer = "الأحياء الأعلى كثافة سكانية:\n" if lang == "ar" else "Most populated neighborhoods:\n"
        for n, val in top.items():
            answer += f"- {n} ({int(val):,} نسمة/كم²)\n"
        sources = top.index.tolist()

    # ============================================
    # المواصلات والنقل
    # ============================================
    elif any(w in q for w in ["مواصلات", "مترو", "نقل", "باص", "حافلة", "transport", "metro", "bus", "transit"]):
        results = []
        for n in df["neighborhood"].unique():
            s = calculate_score("restaurant", n)
            if s:
                results.append({"neighborhood": n, "transport": s["details"]["transport_score"]})
        results = sorted(results, key=lambda x: x["transport"], reverse=True)[:3]
        answer = "أفضل الأحياء بالمواصلات:\n" if lang == "ar" else "Best neighborhoods for transportation:\n"
        for r in results:
            answer += f"- {r['neighborhood']} ({r['transport']}%)\n"
        sources = [r["neighborhood"] for r in results]

    # ============================================
    # قوة السوق / النشاط التجاري
    # ============================================
    elif any(w in q for w in ["سوق", "تجاري", "نشاط", "رخص", "market", "business", "commercial"]):
        results = []
        for n in df["neighborhood"].unique():
            s = calculate_score("restaurant", n)
            if s:
                results.append({"neighborhood": n, "market": s["details"]["market_strength_score"]})
        results = sorted(results, key=lambda x: x["market"], reverse=True)[:3]
        answer = "أقوى الأحياء تجارياً:\n" if lang == "ar" else "Strongest commercial neighborhoods:\n"
        for r in results:
            answer += f"- {r['neighborhood']} ({r['market']}%)\n"
        sources = [r["neighborhood"] for r in results]

    # ============================================
    # الطلب / الفرصة
    # ============================================
    elif any(w in q for w in ["طلب", "فرصة", "demand", "opportunity"]):
        results = []
        for n in df["neighborhood"].unique():
            s = calculate_score("restaurant", n)
            if s:
                results.append({"neighborhood": n, "demand": s["details"]["demand_score"]})
        results = sorted(results, key=lambda x: x["demand"], reverse=True)[:3]
        answer = "الأحياء الأعلى طلباً:\n" if lang == "ar" else "Highest demand neighborhoods:\n"
        for r in results:
            answer += f"- {r['neighborhood']} ({r['demand']}%)\n"
        sources = [r["neighborhood"] for r in results]

    # ============================================
    # كيف يعمل النظام / الدرجة
    # ============================================
    elif any(w in q for w in ["كيف", "طريقة", "نظام", "درجة", "تقييم", "how", "score", "rating", "system", "work"]):
        answer = "طريقة عمل فرصتي 🔍\n\nنحسب درجة لكل حي من 100 بناءً على:\n\n🤖 40% — توقع نموذج XGBoost\n👥 20% — الكثافة السكانية والطلب\n⚖️ 15% — مستوى المنافسة\n🏪 10% — النشاط التجاري القريب\n🚇 10% — وسائل النقل\n📈 5% — رخص الأعمال وقوة السوق\n\n✅ 70+ = مناسب جداً\n🟡 50-69 = مناسب\n🔴 أقل من 50 = غير مناسب" if lang == "ar" else "How Forsati works 🔍\n\nWe calculate a score from 100 based on:\n🤖 40% ML model (XGBoost)\n👥 20% Population density\n⚖️ 15% Competition level\n🏪 10% Nearby businesses\n🚇 10% Transportation\n📈 5% Market strength"

    # ============================================
    # عدد الأحياء / الفئات
    # ============================================
    elif any(w in q for w in ["كم حي", "عدد الاحياء", "كم فئة", "كم نشاط", "how many", "neighborhoods count"]):
        n_count = len(df['neighborhood'].unique())
        c_count = len(df['category_en'].unique())
        answer = f"فرصتي تغطي:\n📍 {n_count} حي في الرياض\n🏪 {c_count} نوع نشاط تجاري\n\nاختر أي نشاط وأي حي وأعطيك تقييم فوري! 😊" if lang == "ar" else f"Forsati covers:\n📍 {n_count} neighborhoods in Riyadh\n🏪 {c_count} business categories"

    # ============================================
    # أفضل حي بشكل عام
    # ============================================
    elif any(w in q for w in ["أفضل حي", "افضل حي", "best neighborhood", "top neighborhood"]):
        results = []
        for n in sorted(df['neighborhood'].unique()):
            s = calculate_score("restaurant", n)
            if s:
                results.append(s)
        results = sorted(results, key=lambda x: x['final_score'], reverse=True)[:3]
        answer = "أفضل الأحياء عموماً في الرياض 🏆\n\n" if lang == "ar" else "Best neighborhoods in Riyadh 🏆\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, r in enumerate(results):
            answer += f"{medals[i]} {r['neighborhood']} — {r['final_score']}/100\n"
        sources = [r['neighborhood'] for r in results]

    # ============================================
    # رد افتراضي ذكي
    # ============================================
    else:
        answer = "ما فهمت سؤالك كويس 😅\n\nجرب تسألني:\n• وين أفضل حي لمطعم؟\n• هل حي العليا مناسب لصيدلية؟\n• أي حي فيه أقل منافسة؟\n• أي حي فيه أعلى كثافة سكانية؟\n• كيف المواصلات في الملز؟\n• كيف يعمل النظام؟\n• كم حي تغطي فرصتي؟" if lang == "ar" else "I didn't understand your question 😅\n\nTry asking:\n• Best neighborhood for a restaurant?\n• Is Al-Olaya good for a pharmacy?\n• Which neighborhood has least competition?\n• How does the system work?"

    return jsonify({"answer": answer, "sources": sources})

if __name__ == "__main__":
    app.run(debug=True, port=5000)