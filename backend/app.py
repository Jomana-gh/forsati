# ============================================================
# مشروع فرصتي - Flask API
# ============================================================

# pip install flask flask-cors pandas numpy xgboost scikit-learn
# cd backend
# python app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)


# ===== تحويل float32 لـ float عادي =====
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


# ===== تحميل النموذج والبيانات =====
print('Loading model...')
with open('forsati_model_v2.pkl', 'rb') as f:
    saved = pickle.load(f)

model        = saved['model']
feature_cols = saved['features']

df = pd.read_csv('forsati_final_dataset.csv')

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

# حساب category_encoded
le = LabelEncoder()
df['category_encoded'] = le.fit_transform(df['category_en'])

# إعادة بناء One-Hot للمنطقة
region_map = {0: 'Central', 1: 'East', 2: 'North', 3: 'South', 4: 'West'}
df['region'] = df['region_encoded'].map(region_map)
region_dummies = pd.get_dummies(df['region'], prefix='region')
df = pd.concat([df, region_dummies], axis=1)

print('Model loaded successfully!')


# ===== دوال مساعدة =====

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

    if len(pair_rows) > 0:
        base = pair_rows.mean(numeric_only=True)
    elif len(neighborhood_rows) > 0:
        base = neighborhood_rows.mean(numeric_only=True)
    else:
        return None

    row = pd.DataFrame([base])
    category_code = df[df['category_en'] == category_name]['category_encoded'].iloc[0]
    row['category_encoded'] = category_code

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

    if final_score >= 70:
        label = 'مناسب جداً'
    elif final_score >= 50:
        label = 'مناسب'
    else:
        label = 'غير مناسب'

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
    neighborhoods = sorted(df['neighborhood'].unique().tolist())
    return jsonify({'neighborhoods': neighborhoods})


@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = sorted(df['category_en'].unique().tolist())
    return jsonify({'categories': categories})


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

    return jsonify(convert_to_serializable({
        'category': category,
        'rankings': results[:top_n]
    }))


# ===== /api/map يرجع JSON بدل HTML =====
# React يرسمه مباشرة بدون Leaflet أو folium
@app.route('/api/map/<category>', methods=['GET'])
def get_map(category):
    if category not in df['category_en'].unique():
        return jsonify({'error': 'Category not found'}), 404

    neighborhoods = sorted(df['neighborhood'].unique())
    rankings = []

    for n in neighborhoods:
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


# ===== تشغيل السيرفر =====
if __name__ == '__main__':
    app.run(debug=True, port=5000)