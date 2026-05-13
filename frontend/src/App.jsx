import { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";
import Chatbot from "./Chatbot";
import MapHeatView from "./MapHeatView";

import {
  Coffee, Store, ShoppingCart, Pill, Cake, Dumbbell, Hotel,
  Shirt, Laptop, Sofa, Scissors, Sparkles, Fuel, Gem,
  Gift, Glasses, Car, PawPrint,
  Search, Loader2, List, Map, ArrowLeft,
  Bot, Users, Scale, Train, BarChart3,
  Mail, MapPin, Star, Zap, Target,
  Download, GitCompare, MessageSquarePlus, Menu, X
} from "lucide-react";

const API = "https://forsati-api.onrender.com";

const T = {
  ar: {
    dir: "rtl",
    appName: "فرصتي",
    tagline: "اختر موقعك بثقة ... وابدأ استثمارك بذكاء",
    startNow: "ابدأ الآن",
    learnMore: "تعرف على المشروع",
    searchTitle: "ابحث بكل سهولة مع مساعدك الذكي!",
    bestNeighborhoods: "أفضل الأحياء لنشاطي",
    evaluateNeighborhood: "تقييم حي محدد",
    compareNeighborhoods: "مقارنة بين حيين",
    projectType: "نوع المشروع",
    chooseNeighborhood: "اختار الحي",
    chooseNeighborhood2: "اختار الحي الثاني",
    search: "ابحث",
    compare: "قارن",
    searching: "جاري البحث...",
    comparing: "جاري المقارنة...",
    chooseProject: "اختار نوع المشروع",
    chooseNeighborhoodErr: "اختار الحي",
    errorMsg: "حدث خطأ، حاول مرة ثانية",
    bestFor: "أفضل الأحياء لـ",
    list: "قائمة",
    heatmap: "خريطة",
    back: "رجوع",
    ratingDetails: "تفاصيل التقييم",
    categories: "الفئات التجارية المتوفرة",
    aboutBadge: "عن المشروع",
    aboutTitle: "ما هو فرصتي؟",
    aboutText: "فرصتي هي منصة ذكية تساعد رواد الأعمال والمستثمرين في اختيار الموقع المثالي لمشاريعهم التجارية داخل مدينة الرياض.",
    reviewsBadge: "آراء المستخدمين",
    reviewsTitle: "ماذا يقولون عنا؟",
    writeReview: "اكتب تقييمك",
    reviewName: "اسمك",
    reviewRole: "دورك (صاحب مطعم، مستثمر...)",
    reviewComment: "تجربتك مع فرصتي",
    reviewSubmit: "إرسال التقييم",
    reviewSuccess: "شكراً! تم إرسال تقييمك ",
    faqBadge: "الأسئلة الشائعة",
    faqTitle: "هل لديك سؤال؟",
    contactBadge: "تواصل معنا",
    contactTitle: "نحن هنا لمساعدتك",
    namePlaceholder: "الاسم",
    emailPlaceholder: "البريد الإلكتروني",
    msgPlaceholder: "رسالتك...",
    send: "إرسال الرسالة",
    successMsg: "شكراً! تم استلام رسالتك وسنتواصل معك قريباً.",
    quickLinks: "روابط سريعة",
    home: "الرئيسية",
    about: "عن المشروع",
    faq: "الأسئلة الشائعة",
    contact: "تواصل معنا",
    copyright: "© 2026 فرصتي — جميع الحقوق محفوظة",
    statsActivities: "نوع نشاط",
    statsNeighborhoods: "حي في الرياض",
    statsCriteria: "معايير تقييم",
    veryGood: "مناسب جداً ",
    good: "مناسب ",
    bad: "غير مناسب ",
    mlScore: "توقع النموذج",
    demandScore: "الطلب والكثافة السكانية",
    competitionScore: "مستوى المنافسة",
    nearbyScore: "النشاط التجاري القريب",
    transportScore: "المواصلات العامة",
    marketScore: "قوة السوق",
    savePdf: "حفظ كـ PDF",
    compareTitle: "مقارنة بين حيين",
    winner: "الفائز",
    features: [
      { icon: <Bot size={35} />, title: "ذكاء اصطناعي", desc: "نموذج XGBoost مدرّب على بيانات حقيقية من الرياض" },
      { icon: <BarChart3 size={35} />, title: "تحليل شامل", desc: "6 معايير تقييم تشمل المنافسة والكثافة السكانية والنقل" },
      { icon: <Zap size={35} />, title: "نتائج فورية", desc: "احصل على تقييمك في ثوانٍ معدودة" },
      { icon: <Target size={35} />, title: "دقة عالية", desc: "توصيات مبنية على إحصائيات رسمية وبيانات موثوقة" },
    ],
    faqs: [
      { q: "كيف يعمل نظام التقييم؟", a: "نستخدم نموذج ذكاء اصطناعي مدرّب على بيانات حقيقية من أحياء الرياض، يأخذ بعين الاعتبار الكثافة السكانية، المنافسة، وسائل النقل، والنشاط التجاري القريب." },
      { q: "هل البيانات محدّثة؟", a: "نعم، البيانات مبنية على إحصائيات حديثة من مصادر رسمية." },
      { q: "ما الفرق بين 'أفضل الأحياء' و'تقييم حي محدد'؟", a: "أفضل الأحياء يرتب لك أعلى 10 أحياء لنشاطك، بينما تقييم حي محدد يعطيك تحليلاً تفصيلياً لحي معين اخترته." },
      { q: "هل الخدمة مجانية؟", a: "نعم، فرصتي مجانية بالكامل لجميع المستخدمين." },
      { q: "ما مدى دقة النتائج؟", a: "النموذج دقيق بنسبة عالية، لكن ننصح بدمج النتائج مع دراسة ميدانية شخصية." },
    ],
  },
  en: {
    dir: "ltr",
    appName: "Forsati",
    tagline: "Choose your location with confidence... Start your investment smartly",
    startNow: "Get Started",
    learnMore: "Learn More",
    searchTitle: "Search easily with your smart assistant!",
    bestNeighborhoods: "Best neighborhoods for my business",
    evaluateNeighborhood: "Evaluate a specific neighborhood",
    compareNeighborhoods: "Compare two neighborhoods",
    projectType: "Business Type",
    chooseNeighborhood: "Choose Neighborhood",
    chooseNeighborhood2: "Choose 2nd Neighborhood",
    search: "Search",
    compare: "Compare",
    searching: "Searching...",
    comparing: "Comparing...",
    chooseProject: "Please select a business type",
    chooseNeighborhoodErr: "Please select a neighborhood",
    errorMsg: "An error occurred. Please try again.",
    bestFor: "Best neighborhoods for",
    list: "List",
    heatmap: "Map",
    back: "Back",
    ratingDetails: "Rating Details",
    categories: "Available Business Categories",
    aboutBadge: "About",
    aboutTitle: "What is Forsati?",
    aboutText: "Forsati is a smart platform that helps entrepreneurs and investors choose the ideal location for their businesses in Riyadh.",
    reviewsBadge: "User Reviews",
    reviewsTitle: "What do they say about us?",
    writeReview: "Write a Review",
    reviewName: "Your Name",
    reviewRole: "Your Role (e.g. Restaurant Owner)",
    reviewComment: "Your experience with Forsati",
    reviewSubmit: "Submit Review",
    reviewSuccess: "Thank you! Your review has been submitted ",
    faqBadge: "FAQ",
    faqTitle: "Have a question?",
    contactBadge: "Contact Us",
    contactTitle: "We are here to help",
    namePlaceholder: "Name",
    emailPlaceholder: "Email",
    msgPlaceholder: "Your message...",
    send: "Send Message",
    successMsg: "Thank you! Your message has been received.",
    quickLinks: "Quick Links",
    home: "Home",
    about: "About",
    faq: "FAQ",
    contact: "Contact",
    copyright: "© 2026 Forsati — All rights reserved",
    statsActivities: "Business Types",
    statsNeighborhoods: "Neighborhoods",
    statsCriteria: "Rating Criteria",
    veryGood: "Highly Suitable ",
    good: "Suitable ",
    bad: "Not Suitable ",
    mlScore: "Model Prediction",
    demandScore: "Population Density",
    competitionScore: "Competition Level",
    nearbyScore: "Nearby Activity",
    transportScore: "Public Transport",
    marketScore: "Market Strength",
    savePdf: "Save as PDF",
    compareTitle: "Neighborhood Comparison",
    winner: "Winner",
    features: [
      { icon: <Bot size={35} />, title: "Artificial Intelligence", desc: "XGBoost model trained on real Riyadh data" },
      { icon: <BarChart3 size={35} />, title: "Comprehensive Analysis", desc: "6 rating criteria including competition, density, and transport" },
      { icon: <Zap size={35} />, title: "Instant Results", desc: "Get your assessment in seconds" },
      { icon: <Target size={35} />, title: "High Accuracy", desc: "Recommendations based on official statistics and reliable data" },
    ],
    faqs: [
      { q: "How does the rating system work?", a: "We use an AI model trained on real data from Riyadh neighborhoods, considering population density, competition, transportation, and nearby commercial activity." },
      { q: "Is the data up to date?", a: "Yes, the data is built on recent statistics from official sources." },
      { q: "What is the difference between Best Neighborhoods and Evaluate a Neighborhood?", a: "Best Neighborhoods ranks the top 10 neighborhoods for your business, while Evaluate a Neighborhood gives a detailed analysis." },
      { q: "Is the service free?", a: "Yes, Forsati is completely free for all users." },
      { q: "How accurate are the results?", a: "The model is highly accurate, but we recommend combining results with personal field research." },
    ],
  }
};

const categoryArabic = {
  restaurant: "مطعم", cafe: "كافيه", supermarket: "سوبرماركت",
  pharmacy: "صيدلية", bakery: "مخبز", gym: "نادي رياضي",
  hotel: "فندق", clothing: "محل ملابس", electronics: "محل إلكترونيات",
  furniture: "محل أثاث", barber: "صالون حلاقة رجالي", salon: "صالون نسائي",
  gas_station: "محطة وقود", laundry: "مغسلة ملابس", jewelry: "محل مجوهرات",
  grocery: "بقالة", shoes: "محل أحذية", sports_clothing: "محل ملابس رياضية",
  curtains: "محل ستائر وسجاد", lighting: "محل إضاءة", sweets: "محل حلويات",
  perfume: "محل عطور", spa: "سبا", auto_repair: "ورشة سيارات",
  toys: "محل ألعاب أطفال", pet_shop: "محل حيوانات أليفة",
  gifts: "محل هدايا وزهور", eyewear: "محل نظارات"
};
const categoryEnglish = {
  restaurant: "Restaurant", cafe: "Cafe", supermarket: "Supermarket",
  pharmacy: "Pharmacy", bakery: "Bakery", gym: "Gym",
  hotel: "Hotel", clothing: "Clothing Store", electronics: "Electronics Store",
  furniture: "Furniture Store", barber: "Barbershop", salon: "Hair Salon",
  gas_station: "Gas Station", laundry: "Laundry", jewelry: "Jewelry Store",
  grocery: "Grocery", shoes: "Shoe Store", sports_clothing: "Sports Clothing",
  curtains: "Curtains & Carpets", lighting: "Lighting Store", sweets: "Sweets Shop",
  perfume: "Perfume Store", spa: "Spa", auto_repair: "Auto Repair",
  toys: "Toy Store", pet_shop: "Pet Shop", gifts: "Gift & Flower Shop", eyewear: "Eyewear Store"
};
const neighborhoodEnglish = {
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
};
const categoryIcons = {
  restaurant:<Store size={20}/>, cafe:<Coffee size={20}/>, supermarket:<ShoppingCart size={20}/>,
  pharmacy:<Pill size={20}/>, bakery:<Cake size={20}/>, gym:<Dumbbell size={20}/>,
  hotel:<Hotel size={20}/>, clothing:<Shirt size={20}/>, electronics:<Laptop size={20}/>,
  furniture:<Sofa size={20}/>, barber:<Scissors size={20}/>, salon:<Sparkles size={20}/>,
  gas_station:<Fuel size={20}/>, laundry:<Shirt size={20}/>, jewelry:<Gem size={20}/>,
  grocery:<ShoppingCart size={20}/>, shoes:<Shirt size={20}/>, sports_clothing:<Dumbbell size={20}/>,
  curtains:<Store size={20}/>, lighting:<Sparkles size={20}/>, sweets:<Cake size={20}/>,
  perfume:<Sparkles size={20}/>, spa:<Sparkles size={20}/>, auto_repair:<Car size={20}/>,
  toys:<Gift size={20}/>, pet_shop:<PawPrint size={20}/>, gifts:<Gift size={20}/>, eyewear:<Glasses size={20}/>
};

function getNeighborhoodLabel(name, lang) { return lang==="en"?(neighborhoodEnglish[name]||name):name; }
function getCategoryLabel(key, lang) { return lang==="ar"?(categoryArabic[key]||key):(categoryEnglish[key]||key); }

// ===== Star Rating =====
function StarRating({ value, onChange, readonly=false }) {
  const [hover, setHover] = useState(0);
  return (
    <div style={{ display:"flex", gap:4, direction:"ltr" }}>
      {[1,2,3,4,5].map(s => (
        <span key={s}
          onClick={() => !readonly && onChange && onChange(s)}
          onMouseEnter={() => !readonly && setHover(s)}
          onMouseLeave={() => !readonly && setHover(0)}
          style={{ fontSize: readonly?16:28, cursor: readonly?"default":"pointer", color: s<=(hover||value)?"#f59e0b":"#d1d5db", transition:"color .15s" }}
        >★</span>
      ))}
    </div>
  );
}

// ===== Review Form =====
function ReviewForm({ lang, t, onSubmitted }) {
  const [name, setName]       = useState("");
  const [role, setRole]       = useState("");
  const [stars, setStars]     = useState(0);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone]       = useState(false);
  const [err, setErr]         = useState("");

  const submit = async () => {
    if (!name.trim()) { setErr(lang==="ar"?"اكتب اسمك":"Enter your name"); return; }
    if (!stars)       { setErr(lang==="ar"?"اختر النجوم":"Choose stars"); return; }
    if (!comment.trim()) { setErr(lang==="ar"?"اكتب تعليقك":"Write a comment"); return; }
    setLoading(true); setErr("");
    try {
      await axios.post(`${API}/api/reviews`, { name: name.trim(), role: role.trim(), rating: stars, comment: comment.trim() });
      setDone(true);
      onSubmitted && onSubmitted();
    } catch { setErr(lang==="ar"?"حدث خطأ":"Error occurred"); }
    setLoading(false);
  };

  if (done) return (
    <div className="review-form-card" style={{ textAlign:"center", padding:"28px" }}>
      <div style={{ fontSize:40 }}>🎉</div>
      <div style={{ fontSize:16, fontWeight:700, color:"#16a34a", marginTop:8 }}>{t.reviewSuccess}</div>
    </div>
  );

  return (
    <div className="review-form-card">
      <h3 style={{ fontSize:17, fontWeight:700, marginBottom:6, display:"flex", alignItems:"center", gap:8 }}>
        <MessageSquarePlus size={20} color="#16a34a" /> {t.writeReview}
      </h3>
      <div style={{ marginBottom:14 }}>
        <label className="review-label">{lang==="ar"?"تقييمك":"Your Rating"}</label>
        <StarRating value={stars} onChange={setStars} />
      </div>
      <div style={{ marginBottom:10 }}>
        <input className="review-input" placeholder={t.reviewName} value={name} onChange={e=>setName(e.target.value)} maxLength={40} />
      </div>
      <div style={{ marginBottom:10 }}>
        <input className="review-input" placeholder={t.reviewRole} value={role} onChange={e=>setRole(e.target.value)} maxLength={50} />
      </div>
      <div style={{ marginBottom:10 }}>
        <textarea className="review-input" placeholder={t.reviewComment} value={comment} onChange={e=>setComment(e.target.value)} rows={3} maxLength={300} style={{ resize:"vertical" }} />
      </div>
      {err && <p style={{ color:"#dc2626", fontSize:13, marginBottom:8 }}>{err}</p>}
      <button className="review-submit-btn" onClick={submit} disabled={loading}>
        {loading ? <Loader2 className="spin" size={16} /> : t.reviewSubmit}
      </button>
    </div>
  );
}

// ===== Footer =====
function Footer({ t }) {
  return (
    <footer className="footer" dir={t.dir}>
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">
            <img src="/forsati_logo.png" alt="Forsati" className="footer-logo-img" />
            <span>{t.appName}</span>
          </div>
          <p className="footer-tagline">{t.tagline}</p>
        </div>
        <div className="footer-links">
          <h4>{t.quickLinks}</h4>
          <ul>
            <li><a href="#home-top">{t.home}</a></li>
            <li><a href="#about">{t.about}</a></li>
            <li><a href="#faq">{t.faq}</a></li>
            <li><a href="#contact">{t.contact}</a></li>
          </ul>
        </div>
      </div>
      <div className="footer-bottom"><p>{t.copyright}</p></div>
    </footer>
  );
}

// ===== Main App =====
export default function App() {
  const [lang, setLang]   = useState("ar");
  const t = T[lang];

  const [page, setPage]                         = useState("home");
  const [categories, setCategories]             = useState([]);
  const [neighborhoods, setNeighborhoods]       = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedNeighborhood, setSelectedNeighborhood]   = useState("");
  const [selectedNeighborhood2, setSelectedNeighborhood2] = useState("");
  const [searchMode, setSearchMode]             = useState("rank");
  const [viewMode, setViewMode]                 = useState("list");
  const [results, setResults]                   = useState([]);
  const [detailResult, setDetailResult]         = useState(null);
  const [compareResults, setCompareResults]     = useState(null);
  const [loading, setLoading]                   = useState(false);
  const [error, setError]                       = useState("");
  const [openFaq, setOpenFaq]                   = useState(null);
  const [contactForm, setContactForm]           = useState({ name:"", email:"", msg:"" });
  const [contactSent, setContactSent]           = useState(false);
  const [menuOpen, setMenuOpen]                 = useState(false);
  const [reviews, setReviews]                   = useState([]);
  const [reviewsLoading, setReviewsLoading]     = useState(true);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  const detailRef = useRef(null);

  useEffect(() => {
    axios.get(`${API}/api/categories`).then(r => setCategories(r.data.categories)).catch(()=>{});
    axios.get(`${API}/api/neighborhoods`).then(r => setNeighborhoods(r.data.neighborhoods)).catch(()=>{});
    fetchReviews();
  }, []);

const fetchReviews = async () => {
  setReviewsLoading(true);
  try {
    const r = await axios.get(`${API}/api/reviews`);
    const apiReviews = r.data.reviews || [];
    
    // ريفيوز ثابتة تظهر دايماً
    const staticReviews = lang === "ar" ? [
      { name: "سارة العتيبي", role: "صاحبة مطعم", comment: "فرصتي ساعدتني أختار الحي الصح لمطعمي، والحمد لله المشروع نجح!", rating: 5 },
      { name: "محمد الغامدي", role: "مستثمر عقاري", comment: "أداة رائعة لأي شخص يفكر يبدأ مشروع، التحليل دقيق وسهل الفهم.", rating: 5 },
      { name: "نورة الشمري", role: "صاحبة كافيه", comment: "قبل ما أفتح كافيهي جربت فرصتي وطلع الحي اللي اخترته مناسب جداً!", rating: 4 },
      { name: "فهد الزهراني", role: "رجل أعمال", comment: "واجهة سهلة والنتائج واضحة. أنصح كل من يريد فتح مشروع يستخدمها.", rating: 5 },
    ] : [
      { name: "Sara Al-Otaibi", role: "Restaurant Owner", comment: "Forsati helped me choose the right neighborhood. The business has been a success!", rating: 5 },
      { name: "Mohammed Al-Ghamdi", role: "Real Estate Investor", comment: "A great tool for anyone thinking of starting a business.", rating: 5 },
      { name: "Noura Al-Shammari", role: "Cafe Owner", comment: "Before opening my cafe, I tried Forsati and it was highly suitable!", rating: 4 },
      { name: "Fahad Al-Zahrani", role: "Businessman", comment: "Easy interface and clear results. Highly recommend!", rating: 5 },
    ];

    // الريفيوز من API تجي أول، بعدين الثابتة
    setReviews([...apiReviews, ...staticReviews]);
  } catch {
    setReviews([
      { name: "سارة العتيبي", role: "صاحبة مطعم", comment: "فرصتي ساعدتني أختار الحي الصح!", rating: 5 },
      { name: "محمد الغامدي", role: "مستثمر عقاري", comment: "التحليل دقيق وسهل الفهم.", rating: 5 },
    ]);
  }
  setReviewsLoading(false);
};

  const scrollTo = (id) => {
    setPage("home"); setMenuOpen(false);
    setTimeout(() => { const el = document.getElementById(id); if (el) el.scrollIntoView({ behavior:"smooth" }); }, 100);
  };

  const scoreColor = (s) => s>=70?"#16a34a":s>=50?"#ca8a04":"#dc2626";
  const scoreLabel = (s) => s>=70?t.veryGood:s>=50?t.good:t.bad;

  // ===== Search Handler =====
  const handleSearch = async () => {
    if (!selectedCategory) { setError(t.chooseProject); return; }
    setError(""); setLoading(true);
    try {
      if (searchMode === "rank") {
        const r = await axios.post(`${API}/api/rank`, { category: selectedCategory.trim().toLowerCase(), top_n:10 });
        setResults(r.data.rankings);
        setPage("results");
        window.scrollTo({ top:0, behavior:"smooth" });
      } else if (searchMode === "evaluate") {
        if (!selectedNeighborhood) { setError(t.chooseNeighborhoodErr); setLoading(false); return; }
        const r = await axios.post(`${API}/api/evaluate`, { category: selectedCategory.trim().toLowerCase(), neighborhood: selectedNeighborhood.trim() });
        setDetailResult(r.data);
        setPage("detail");
        window.scrollTo({ top:0, behavior:"smooth" });
      } else if (searchMode === "compare") {
        if (!selectedNeighborhood || !selectedNeighborhood2) { setError(t.chooseNeighborhoodErr); setLoading(false); return; }
        if (selectedNeighborhood === selectedNeighborhood2) { setError(lang==="ar"?"اختاري حيين مختلفين":"Choose two different neighborhoods"); setLoading(false); return; }
        const [r1, r2] = await Promise.all([
          axios.post(`${API}/api/evaluate`, { category: selectedCategory.trim().toLowerCase(), neighborhood: selectedNeighborhood.trim() }),
          axios.post(`${API}/api/evaluate`, { category: selectedCategory.trim().toLowerCase(), neighborhood: selectedNeighborhood2.trim() }),
        ]);
        setCompareResults({ a: r1.data, b: r2.data });
        setPage("compare");
        window.scrollTo({ top:0, behavior:"smooth" });
      }
    } catch { setError(t.errorMsg); }
    setLoading(false);
  };

  // ===== PDF Download =====
  const handleDownloadPdf = () => {
    if (!detailResult) return;
    const nbLabel  = getNeighborhoodLabel(detailResult.neighborhood, lang);
    const catLabel = getCategoryLabel(detailResult.category, lang);
    const d        = detailResult.details || {};
    const html = `
      <html dir="${t.dir}"><head><meta charset="utf-8">
      <style>
        body { font-family: Arial, sans-serif; padding: 40px; color: #111; }
        h1 { color: #16a34a; font-size: 28px; }
        h2 { color: #374151; font-size: 20px; margin-top: 28px; }
        .score { font-size: 56px; font-weight: 900; color: ${scoreColor(detailResult.final_score)}; }
        .row { display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #e5e7eb; }
        .bar-wrap { background:#e5e7eb; border-radius:99px; height:10px; width:200px; margin-top:6px; }
        .bar { height:100%; border-radius:99px; background:${scoreColor(detailResult.final_score)}; }
        .footer { margin-top:40px; font-size:12px; color:#9ca3af; text-align:center; }
      </style></head><body>
      <h1>فرصتي — Forsati</h1>
      <p>${catLabel} — ${nbLabel}</p>
      <div class="score">${detailResult.final_score}<span style="font-size:22px;color:#9ca3af">/100</span></div>
      <p>${scoreLabel(detailResult.final_score)}</p>
      <h2>${t.ratingDetails}</h2>
      ${[
        [t.mlScore, d.ml_probability],
        [t.demandScore, d.demand_score],
        [t.competitionScore, d.competition_score],
        [t.nearbyScore, d.nearby_activity_score],
        [t.transportScore, d.transport_score],
        [t.marketScore, d.market_strength_score],
      ].map(([label, val]) => `
        <div class="row">
          <span>${label}</span>
          <span><strong>${Number(val||0).toFixed(1)}%</strong></span>
        </div>
        <div class="bar-wrap"><div class="bar" style="width:${val||0}%"></div></div>
      `).join("")}
      <div class="footer">forsati-api.onrender.com — ${new Date().toLocaleDateString()}</div>
      </body></html>
    `;
    const win = window.open("", "_blank");
    win.document.write(html);
    win.document.close();
    win.focus();
    setTimeout(() => { win.print(); win.close(); }, 500);
  };

  // ===== Contact Save =====
  const handleContact = async () => {
    if (!contactForm.name || !contactForm.email || !contactForm.msg) return;
    try {
      await axios.post(`${API}/api/contact`, contactForm);
    } catch {}
    setContactSent(true);
  };

  // ===== Header =====
  const Header = ({ showBack=false }) => (
    <>
      <header className="header" dir={t.dir}>
        <div className="header-logo" onClick={() => { setPage("home"); setMobileMenu(false); }}>
          <img src="/forsati_logo.png" alt="Forsati" className="header-logo-img" />
        </div>
        {showBack ? (
          <div style={{ display:"flex", alignItems:"center", gap:12 }}>
            <button className="lang-toggle" onClick={() => setLang(lang==="ar"?"en":"ar")}>{lang==="ar"?"EN":"عر"}</button>
            <button className="back-btn" onClick={() => setPage(results.length&&page==="detail"?"results":"home")}>
              <ArrowLeft size={16} /> {t.back}
            </button>
          </div>
        ) : (
          <div style={{ display:"flex", alignItems:"center", gap:16 }}>
            <nav className="nav">
              <a href="#home-top" onClick={(e) => { e.preventDefault(); scrollTo("home-top"); }}>{t.home}</a>
              <a href="#about" onClick={(e) => { e.preventDefault(); scrollTo("about"); }}>{t.about}</a>
              <a href="#faq" onClick={(e) => { e.preventDefault(); scrollTo("faq"); }}>{t.faq}</a>
              <a href="#contact" onClick={(e) => { e.preventDefault(); scrollTo("contact"); }}>{t.contact}</a>
            </nav>
            <button className="lang-toggle" onClick={() => setLang(lang==="ar"?"en":"ar")}>{lang==="ar"?"EN":"عر"}</button>
            <button className="mobile-menu-btn" onClick={() => setMobileMenu(m => !m)}>
              <Menu size={22} />
            </button>
          </div>
        )}
      </header>
      {mobileMenu && !showBack && (
        <div className="mobile-nav" dir={t.dir}>
          <a onClick={() => { scrollTo("home-top"); setMobileMenu(false); }}>{t.home}</a>
          <a onClick={() => { scrollTo("about"); setMobileMenu(false); }}>{t.about}</a>
          <a onClick={() => { scrollTo("faq"); setMobileMenu(false); }}>{t.faq}</a>
          <a onClick={() => { scrollTo("contact"); setMobileMenu(false); }}>{t.contact}</a>
        </div>
      )}
    </>
  );


  if (page === "results") return (
    <div className="page" dir={t.dir}>
      <Header showBack />
      <div className="results-container">
        <h2 className="results-title">{t.bestFor} <span className="highlight">{getCategoryLabel(selectedCategory, lang)}</span></h2>
        <div className="view-toggle">
          <button className={viewMode==="list"?"view-btn active":"view-btn"} onClick={()=>setViewMode("list")}><List size={16}/> {t.list}</button>
          <button className={viewMode==="heatmap"?"view-btn active":"view-btn"} onClick={()=>setViewMode("heatmap")}><Map size={16}/> {t.heatmap}</button>
        </div>
        {viewMode==="heatmap" ? (
          <MapHeatView category={selectedCategory} lang={lang} t={t} />
        ) : (
          <div className="results-grid">
            {results.map((r,i) => (
              <div key={i} className="result-card" onClick={() => { setDetailResult(r); setPage("detail"); }}>
                <div className="card-body">
                  <h3 className="neighborhood-name">{getNeighborhoodLabel(r.neighborhood, lang)}</h3>
                  <div className="rank-badge-inline">#{i+1}</div>
                  <div className="score-bar-container">
                    <div className="score-bar" style={{ width:`${r.final_score}%`, background:scoreColor(r.final_score) }} />
                  </div>
                  <div className="card-footer">
                    <span className="score-num" style={{ color:scoreColor(r.final_score) }}>{r.final_score}/100</span>
                    <span className="score-label">{scoreLabel(r.final_score)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      <Footer t={t} />
    </div>
  );

  // ===== Detail Page =====
  if (page==="detail" && detailResult) return (
    <div className="page" dir={t.dir}>
      <Header showBack />
      <div className="detail-container" ref={detailRef}>
        <div className="detail-hero" style={{ borderColor:scoreColor(detailResult.final_score) }}>
          <h2>{getNeighborhoodLabel(detailResult.neighborhood, lang)}</h2>
          <p className="detail-category">{getCategoryLabel(detailResult.category, lang)}</p>
          <div className="big-score" style={{ color:scoreColor(detailResult.final_score) }}>
            {detailResult.final_score}<span>/100</span>
          </div>
          <div className="big-label">{scoreLabel(detailResult.final_score)}</div>
          {/* زر PDF */}
          <button onClick={handleDownloadPdf} style={{
            marginTop:16, display:"flex", alignItems:"center", gap:8,
            background:"#16a34a", color:"#fff", border:"none",
            padding:"10px 22px", borderRadius:10, fontSize:14,
            fontWeight:700, cursor:"pointer", fontFamily:"Tajawal, sans-serif",
          }}>
            <Download size={16} /> {t.savePdf}
          </button>
        </div>

        {detailResult.details && (
          <div className="detail-breakdown">
            <h3>{t.ratingDetails}</h3>
            {[
              { label:t.mlScore,          key:"ml_probability",       icon:<Bot size={16}/> },
              { label:t.demandScore,      key:"demand_score",          icon:<Users size={16}/> },
              { label:t.competitionScore, key:"competition_score",     icon:<Scale size={16}/> },
              { label:t.nearbyScore,      key:"nearby_activity_score", icon:<Store size={16}/> },
              { label:t.transportScore,   key:"transport_score",       icon:<Train size={16}/> },
              { label:t.marketScore,      key:"market_strength_score", icon:<BarChart3 size={16}/> },
            ].map(item => (
              <div key={item.key} className="breakdown-row">
                <span className="breakdown-label">{item.icon} {item.label}</span>
                <div className="breakdown-bar-container">
                  <div className="breakdown-bar" style={{ width:`${detailResult.details[item.key]}%`, background:scoreColor(detailResult.details[item.key]) }} />
                </div>
                <span className="breakdown-score">{Number(detailResult.details[item.key]).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        )}

        {/* Review Form */}
        <ReviewForm lang={lang} t={t} onSubmitted={fetchReviews} />
      </div>
      <Footer t={t} />
    </div>
  );

  // ===== Compare Page =====
  if (page==="compare" && compareResults) {
    const { a, b } = compareResults;
    const winner = a.final_score >= b.final_score ? a : b;
    const metrics = [
      { label:t.mlScore,          key:"ml_probability" },
      { label:t.demandScore,      key:"demand_score" },
      { label:t.competitionScore, key:"competition_score" },
      { label:t.nearbyScore,      key:"nearby_activity_score" },
      { label:t.transportScore,   key:"transport_score" },
      { label:t.marketScore,      key:"market_strength_score" },
    ];
    return (
      <div className="page" dir={t.dir}>
        <Header showBack />
        <div className="detail-container">
          <h2 style={{ textAlign:"center", marginBottom:8 }}>{t.compareTitle}</h2>
          <p style={{ textAlign:"center", color:"#16a34a", fontWeight:700, marginBottom:24 }}>
             {t.winner}: {getNeighborhoodLabel(winner.neighborhood, lang)} ({winner.final_score}/100)
          </p>

          {/* Header row */}
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:12, marginBottom:16 }}>
            <div style={{ background:"#f9fafb", borderRadius:12, padding:"16px", textAlign:"center", border:`2px solid ${scoreColor(a.final_score)}` }}>
              <div style={{ fontWeight:700, fontSize:15 }}>{getNeighborhoodLabel(a.neighborhood, lang)}</div>
              <div style={{ fontSize:32, fontWeight:900, color:scoreColor(a.final_score) }}>{a.final_score}</div>
            </div>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"center", fontSize:24 }}>VS</div>
            <div style={{ background:"#f9fafb", borderRadius:12, padding:"16px", textAlign:"center", border:`2px solid ${scoreColor(b.final_score)}` }}>
              <div style={{ fontWeight:700, fontSize:15 }}>{getNeighborhoodLabel(b.neighborhood, lang)}</div>
              <div style={{ fontSize:32, fontWeight:900, color:scoreColor(b.final_score) }}>{b.final_score}</div>
            </div>
          </div>

          {/* Metrics */}
          <div className="detail-breakdown">
            {metrics.map(m => {
              const va = Number(a.details?.[m.key]||0);
              const vb = Number(b.details?.[m.key]||0);
              return (
                <div key={m.key} style={{ marginBottom:16 }}>
                  <div style={{ fontWeight:600, fontSize:13, marginBottom:6 }}>{m.label}</div>
                  <div style={{ display:"grid", gridTemplateColumns:"1fr auto 1fr", gap:8, alignItems:"center" }}>
                    <div>
                      <div style={{ height:10, background:"#e5e7eb", borderRadius:99, overflow:"hidden" }}>
                        <div style={{ height:"100%", width:`${va}%`, background:va>=vb?"#16a34a":"#dc2626", borderRadius:99 }} />
                      </div>
                      <div style={{ fontSize:12, marginTop:2, color:va>=vb?"#16a34a":"#6b7280" }}>{va.toFixed(1)}% {va>=vb?"✓":""}</div>
                    </div>
                    <div style={{ fontSize:11, color:"#9ca3af", textAlign:"center" }}>VS</div>
                    <div>
                      <div style={{ height:10, background:"#e5e7eb", borderRadius:99, overflow:"hidden" }}>
                        <div style={{ height:"100%", width:`${vb}%`, background:vb>va?"#16a34a":"#dc2626", borderRadius:99 }} />
                      </div>
                      <div style={{ fontSize:12, marginTop:2, color:vb>va?"#16a34a":"#6b7280" }}>{vb.toFixed(1)}% {vb>va?"✓":""}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        <Footer t={t} />
      </div>
    );
  }

  // ===== Home Page =====
  return (
    <div className="page" dir={t.dir} id="home-top">
      <Header />

      <section className="hero" id="hero" style={{ backgroundImage:"url('/forsati_bg.jpg')" }}>
        <div className="hero-bg-overlay" />
        <div className="hero-content">
          <div className="hero-logo-wrap">
            <img src="/forsati_logo.png" alt="Forsati" className="hero-logo-img" />
          </div>
          <h1 className="hero-title">{t.appName}</h1>
          <p className="hero-subtitle">{t.tagline}</p>
          <div className="hero-btns">
            <button className="hero-btn" onClick={() => document.getElementById("search").scrollIntoView({ behavior:"smooth" })}>{t.startNow}</button>
            <button className="hero-btn-outline" onClick={() => document.getElementById("about").scrollIntoView({ behavior:"smooth" })}>{t.learnMore}</button>
          </div>
        </div>
        <div className="hero-stats">
          <div className="stat-card"><span className="stat-num">28</span><span className="stat-label">{t.statsActivities}</span></div>
          <div className="stat-card"><span className="stat-num">60</span><span className="stat-label">{t.statsNeighborhoods}</span></div>
          <div className="stat-card"><span className="stat-num">6</span><span className="stat-label">{t.statsCriteria}</span></div>
        </div>
      </section>

      {/* Search */}
      <section className="search-section" id="search">
        <h2 className="search-title">{t.searchTitle}</h2>
        <div className="mode-toggle">
          <button className={searchMode==="rank"?"mode-btn active":"mode-btn"} onClick={()=>setSearchMode("rank")}>{t.bestNeighborhoods}</button>
          <button className={searchMode==="evaluate"?"mode-btn active":"mode-btn"} onClick={()=>setSearchMode("evaluate")}>{t.evaluateNeighborhood}</button>
          <button className={searchMode==="compare"?"mode-btn active":"mode-btn"} onClick={()=>setSearchMode("compare")}>
            <GitCompare size={14} style={{ marginLeft:4 }} /> {t.compareNeighborhoods}
          </button>
        </div>
        <div className="search-bar">
          <div className="select-wrapper">
            <span className="select-icon"><List size={16}/></span>
            <select value={selectedCategory} onChange={e=>setSelectedCategory(e.target.value)} className="select-input">
              <option value="">{t.projectType}</option>
              {categories.map(c => <option key={c} value={c}>{getCategoryLabel(c,lang)}</option>)}
            </select>
          </div>
          {(searchMode==="evaluate"||searchMode==="compare") && (
            <div className="select-wrapper">
              <span className="select-icon"><MapPin size={16}/></span>
              <select value={selectedNeighborhood} onChange={e=>setSelectedNeighborhood(e.target.value)} className="select-input">
                <option value="">{t.chooseNeighborhood}</option>
                {neighborhoods.map(n => <option key={n} value={n}>{getNeighborhoodLabel(n,lang)}</option>)}
              </select>
            </div>
          )}
          {searchMode==="compare" && (
            <div className="select-wrapper">
              <span className="select-icon"><MapPin size={16}/></span>
              <select value={selectedNeighborhood2} onChange={e=>setSelectedNeighborhood2(e.target.value)} className="select-input">
                <option value="">{t.chooseNeighborhood2}</option>
                {neighborhoods.map(n => <option key={n} value={n}>{getNeighborhoodLabel(n,lang)}</option>)}
              </select>
            </div>
          )}
          <button className="search-btn" onClick={handleSearch} disabled={loading}>
            {loading ? <><Loader2 className="spin" size={18}/> {searchMode==="compare"?t.comparing:t.searching}</>
                     : <><Search size={18}/> {searchMode==="compare"?t.compare:t.search}</>}
          </button>
        </div>
        {error && <p className="error-msg">{error}</p>}
      </section>

      {/* Categories */}
      <section className="categories-section">
        <div className="categories-header"><h2>{t.categories}</h2></div>
        <div className="categories-slider">
          {Object.entries(categoryArabic).map(([key],i) => (
            <div key={i} className="category-card slider-card" onClick={() => {
              setSelectedCategory(key); setSearchMode("rank");
              document.getElementById("search").scrollIntoView({ behavior:"smooth" });
            }}>
              <span className="category-icon">{categoryIcons[key]||<Store size={20}/>}</span>
              <span>{getCategoryLabel(key,lang)}</span>
            </div>
          ))}
        </div>
      </section>

      {/* About */}
      <section className="about-section" id="about">
        <div className="about-inner">
          <div className="section-badge">{t.aboutBadge}</div>
          <h2 className="section-title">{t.aboutTitle}</h2>
          <p className="about-text">{t.aboutText}</p>
          <div className="about-features">
            {t.features.map((f,i) => (
              <div key={i} className="feature-card">
                <span className="feature-icon">{f.icon}</span>
                <h4>{f.title}</h4>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

{/* Reviews Section */}
<section className="reviews-section" id="reviews">
  <div className="section-badge">{t.reviewsBadge}</div>
  <h2 className="section-title">{t.reviewsTitle}</h2>

  {/* زر إضافة تقييم جديد */}
  <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 32 }}>
    <button 
      className="write-review-trigger"
      onClick={() => setShowReviewForm(!showReviewForm)}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        background: 'transparent',
        border: '2px dashed #16a34a',
        borderRadius: 99,
        padding: '10px 24px',
        fontSize: 14,
        fontWeight: 600,
        color: '#16a34a',
        cursor: 'pointer',
        transition: 'all 0.2s'
      }}
    >
      <MessageSquarePlus size={18} />
      {t.writeReview}
      <span style={{ fontSize: 12 }}>{showReviewForm ? '▲' : '▼'}</span>
    </button>
  </div>

  {/* الفورم يظهر فقط عند الضغط */}
  {showReviewForm && (
    <div style={{ maxWidth: 550, margin: '0 auto 40px auto' }}>
      <ReviewForm lang={lang} t={t} onSubmitted={() => {
        setShowReviewForm(false);
        fetchReviews();
      }} />
    </div>
  )}

  {/* باقي التعليقات الموجودة */}
  {reviewsLoading ? (
    <div style={{ textAlign:"center", padding:"40px 0", color:"#6b7280" }}>
      <Loader2 className="spin" size={24} />
    </div>
  ) : (
    <>
      <div className="reviews-grid">
        {reviews.slice(0,8).map((r,i) => (
          <div key={i} className="review-card">
            <StarRating value={r.rating||r.stars||5} readonly />
            {(r.comment||r.text) && <p className="review-text">"{r.comment||r.text}"</p>}
            <div className="reviewer">
              <div className="reviewer-avatar">{r.name?r.name[0]:"؟"}</div>
              <div>
                <div className="reviewer-name">{r.name}</div>
                <div className="reviewer-role">{r.role}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="reviews-slider">
        {reviews.slice(0,8).map((r,i) => (
          <div key={i} className="review-card" style={{ minWidth:280, flexShrink:0 }}>
            <StarRating value={r.rating||r.stars||5} readonly />
            {(r.comment||r.text) && <p className="review-text">"{r.comment||r.text}"</p>}
            <div className="reviewer">
              <div className="reviewer-avatar">{r.name?r.name[0]:"؟"}</div>
              <div>
                <div className="reviewer-name">{r.name}</div>
                <div className="reviewer-role">{r.role}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  )}
</section>

      {/* FAQ */}
      <section className="faq-section" id="faq">
        <div className="faq-inner">
          <div className="section-badge">{t.faqBadge}</div>
          <h2 className="section-title">{t.faqTitle}</h2>
          <div className="faq-list">
            {t.faqs.map((f,i) => (
              <div key={i} className={`faq-item ${openFaq===i?"open":""}`}>
                <button className="faq-q" onClick={() => setOpenFaq(openFaq===i?null:i)}>
                  <span>{f.q}</span><span className="faq-arrow">{openFaq===i?"▲":"▼"}</span>
                </button>
                {openFaq===i && <div className="faq-a">{f.a}</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact */}
      <section className="contact-section" id="contact">
        <div className="contact-inner">
          <div className="section-badge">{t.contactBadge}</div>
          <h2 className="section-title">{t.contactTitle}</h2>
          {contactSent ? (
            <div className="contact-success"><span></span><p>{t.successMsg}</p></div>
          ) : (
            <div className="contact-form">
              <div className="form-row">
                <input className="form-input" placeholder={t.namePlaceholder} value={contactForm.name} onChange={e=>setContactForm({...contactForm,name:e.target.value})} />
                <input className="form-input" placeholder={t.emailPlaceholder} value={contactForm.email} onChange={e=>setContactForm({...contactForm,email:e.target.value})} />
              </div>
              <textarea className="form-textarea" placeholder={t.msgPlaceholder} rows={4} value={contactForm.msg} onChange={e=>setContactForm({...contactForm,msg:e.target.value})} />
              <button className="form-submit" onClick={handleContact}>{t.send}</button>
            </div>
          )}
          <div className="contact-info">
            <div className="contact-info-item"><Mail size={16}/> <span>forsati@example.com</span></div>
            <div className="contact-info-item"><MapPin size={16}/> <span>{lang==="ar"?"الرياض، المملكة العربية السعودية":"Riyadh, Saudi Arabia"}</span></div>
          </div>
        </div>
      </section>

      <Chatbot lang={lang} t={t} />
      <Footer t={t} />
    </div>
  );
}