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

app = Flask(__name__)
CORS(app)


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


# ===== Chatbot =====

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

@app.route('/api/chat', methods=['POST'])
def chatbot():
    data = request.json
    question = data.get('question', '').strip()
    lang = data.get('lang', 'ar')
    q_lower = question.lower()

    if not question:
        return jsonify({"answer": "What would you like to know? 😊" if lang == 'en' else "وش تبي تعرف؟ 😊"})

    # ===== دالة تحويل اسم الحي للإنجليزي =====
    # معكوس neighborhood_en_to_ar — نأخذ أول إنجليزي لكل عربي
    ar_to_en = {}
    for en, ar in neighborhood_en_to_ar.items():
        if ar not in ar_to_en:
            ar_to_en[ar] = en.title()

    def display_name(ar_name):
        return ar_to_en.get(ar_name, ar_name) if lang == 'en' else ar_name

    category     = detect_category(question)
    neighborhood = detect_neighborhood(question)

    # ===== 1. كثافة سكانية — يجي أول قبل greeting =====
    density_ar = ["كثافة", "سكان", "عدد السكان"]
    density_en = ["density", "population", "crowded", "most populated", "highest density"]
    if any(w in question for w in density_ar) or any(w in q_lower for w in density_en):
        top_nb = df.groupby('neighborhood')['population_density'].mean().idxmax()
        if lang == 'en':
            return jsonify({"answer": f"The neighborhood with the highest population density in Riyadh is **{display_name(top_nb)}** 👥"})
        return jsonify({"answer": f"أعلى حي بالكثافة السكانية في الرياض هو **{top_nb}** 👥"})

    # ===== 2. حي محدد + فئة محددة =====
    if category and neighborhood:
        result = calculate_score(category, neighborhood)
        if result:
            score  = result['final_score']
            cat_ar = categoryArabic.get(category, category)
            d      = result['details']
            nb_display = display_name(neighborhood)

            if lang == 'en':
                if score >= 70:
                    verdict = "Very Suitable ✅"
                    intro   = f"{nb_display} is an excellent choice for a {category}! 🎯"
                elif score >= 50:
                    verdict = "Suitable 🟡"
                    intro   = f"{nb_display} has potential for a {category}, but needs more study."
                else:
                    verdict = "Not Suitable ❌"
                    intro   = f"{nb_display} is not ideal for a {category}. Consider other neighborhoods."

                answer  = f"{intro}\n\n"
                answer += f"📊 Overall Score: {score}/100 — {verdict}\n\n"
                answer += f"Score Breakdown:\n"
                answer += f"🤖 Model Prediction: {d['ml_probability']}%\n"
                answer += f"👥 Demand & Density: {d['demand_score']}%\n"
                answer += f"⚖️ Competition Level: {d['competition_score']}%\n"
                answer += f"🏪 Nearby Activity: {d['nearby_activity_score']}%\n"
                answer += f"🚇 Transportation: {d['transport_score']}%\n"
                answer += f"📈 Market Strength: {d['market_strength_score']}%"
            else:
                if score >= 70:
                    verdict = "مناسب جداً ✅"
                    intro   = f"حي {neighborhood} خيار ممتاز لـ{cat_ar}! 🎯"
                elif score >= 50:
                    verdict = "مناسب 🟡"
                    intro   = f"حي {neighborhood} فيه إمكانية لـ{cat_ar}، بس تحتاج دراسة أكثر."
                else:
                    verdict = "غير مناسب ❌"
                    intro   = f"حي {neighborhood} مو مثالي لـ{cat_ar}، أنصحك تشوف أحياء ثانية."

                answer  = f"{intro}\n\n"
                answer += f"📊 الدرجة الكلية: {score}/100 — {verdict}\n\n"
                answer += f"تفاصيل التقييم:\n"
                answer += f"🤖 توقع النموذج: {d['ml_probability']}%\n"
                answer += f"👥 الطلب والكثافة: {d['demand_score']}%\n"
                answer += f"⚖️ مستوى المنافسة: {d['competition_score']}%\n"
                answer += f"🏪 النشاط التجاري القريب: {d['nearby_activity_score']}%\n"
                answer += f"🚇 المواصلات: {d['transport_score']}%\n"
                answer += f"📈 قوة السوق: {d['market_strength_score']}%"

            return jsonify({"answer": answer, "sources": [nb_display]})

    # ===== 3. فئة فقط → أفضل 3 أحياء =====
    if category:
        cat_ar  = categoryArabic.get(category, category)
        results = []
        for n in sorted(df['neighborhood'].unique()):
            s = calculate_score(category, n)
            if s:
                results.append(s)
        results = sorted(results, key=lambda x: x['final_score'], reverse=True)[:3]

        if results:
            medals  = ["🥇", "🥈", "🥉"]
            sources = [display_name(r['neighborhood']) for r in results]

            if lang == 'en':
                answer = f"Best neighborhoods for a {category} in Riyadh 🏆\n\n"
                for i, r in enumerate(results):
                    d = r['details']
                    answer += f"{medals[i]} {display_name(r['neighborhood'])} — {r['final_score']}/100\n"
                    answer += f"   👥 Demand: {d['demand_score']}% | ⚖️ Competition: {d['competition_score']}% | 🚇 Transit: {d['transport_score']}%\n\n"
                answer += "You can view more details through the search on the website! 😊"
            else:
                answer = f"أفضل الأحياء لـ{cat_ar} في الرياض 🏆\n\n"
                for i, r in enumerate(results):
                    d = r['details']
                    answer += f"{medals[i]} {r['neighborhood']} — {r['final_score']}/100\n"
                    answer += f"   👥 الطلب: {d['demand_score']}% | ⚖️ المنافسة: {d['competition_score']}% | 🚇 النقل: {d['transport_score']}%\n\n"
                answer += "تقدر تشوفي تفاصيل أكثر من خلال البحث في الموقع! 😊"

            return jsonify({"answer": answer, "sources": sources})

    # ===== 4. تحيات — بعد كل الـ checks المفيدة =====
    greeting_ar = ["مرحبا", "هلا", "السلام", "اهلا", "أهلا"]
    # نبحث عن كلمة مستقلة لتجنب false positive مثل "highest"
    greeting_en = ["hello", "hey", "greetings", "good morning", "good evening"]
    q_words = set(q_lower.split())
    if any(w in question for w in greeting_ar) or any(w in q_words for w in greeting_en):
        if lang == 'en':
            return jsonify({"answer": "Hello! I'm the Forsati assistant 🤖\nAsk me about any business type and I'll help you find the best neighborhood in Riyadh!"})
        return jsonify({"answer": "مرحباً! أنا مساعد فرصتي 🤖\nاسأليني عن أي نشاط تجاري وأساعدك تختاري أفضل حي في الرياض!"})

    # ===== 5. شكر =====
    thanks_ar = ["شكرا", "شكراً", ]
    thanks_en = ["thanks", "thank you", "appreciate"]
    if any(w in question for w in thanks_ar) or any(w in q_lower for w in thanks_en):
        if lang == 'en':
            return jsonify({"answer": "You're welcome! Anything else I can help with? 😊"})
        return jsonify({"answer": "العفو! أي خدمة ثانية؟ 😊"})

    # ===== ما فهم السؤال =====
    if lang == 'en':
        return jsonify({"answer": "I didn't quite understand your question 😅\nTry asking:\n• What's the best neighborhood for a restaurant?\n• Is Al-Malaz suitable for a cafe?\n• Which neighborhood has the highest population density?"})
    return jsonify({"answer": "ما فهمت سؤالك كويس 😅\nجربي تسأليني مثلاً:\n• وين أفضل حي لمطعم؟\n• هل حي الملز مناسب لكافيه؟\n• أي حي فيه أعلى كثافة سكانية؟"})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)