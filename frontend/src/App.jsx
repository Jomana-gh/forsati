import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import MapHeatView from "./MapHeatView";

const API = "";

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

const reviews = [
  { name: "سارة العتيبي", role: "صاحبة مطعم", text: "فرصتي ساعدتني أختار الحي الصح لمطعمي، والحمد لله المشروع نجح!", stars: 5 },
  { name: "محمد الغامدي", role: "مستثمر عقاري", text: "أداة رائعة لأي شخص يفكر يبدأ مشروع، التحليل دقيق وسهل الفهم.", stars: 5 },
  { name: "نورة الشمري", role: "صاحبة كافيه", text: "قبل ما أفتح كافيهي جربت فرصتي وطلع الحي اللي اخترته مناسب جداً!", stars: 4 },
  { name: "فهد الزهراني", role: "رجل أعمال", text: "واجهة سهلة والنتائج واضحة. أنصح كل من يريد فتح مشروع يستخدمها.", stars: 5 },
];

const faqs = [
  { q: "كيف يعمل نظام التقييم؟", a: "نستخدم نموذج ذكاء اصطناعي مدرّب على بيانات حقيقية من أحياء الرياض، يأخذ بعين الاعتبار الكثافة السكانية، المنافسة، وسائل النقل، والنشاط التجاري القريب." },
  { q: "هل البيانات محدّثة؟", a: "نعم، البيانات مبنية على إحصائيات حديثة من مصادر رسمية وتُحدَّث بشكل دوري." },
  { q: "ما الفرق بين 'أفضل الأحياء' و'تقييم حي محدد'؟", a: "أفضل الأحياء يرتب لك أعلى 10 أحياء لنشاطك، بينما تقييم حي محدد يعطيك تحليلاً تفصيلياً لحي معين اخترته." },
  { q: "هل الخدمة مجانية؟", a: "نعم، فرصتي مجانية بالكامل لجميع المستخدمين." },
  { q: "ما مدى دقة النتائج؟", a: "النموذج دقيق بنسبة عالية بناءً على البيانات المتاحة، لكن ننصح بدمج النتائج مع دراسة ميدانية شخصية قبل اتخاذ قرار الاستثمار." },
];

// ===== HeatMap Component =====
function HeatMap({ results, category }) {
  const max = Math.max(...results.map(r => r.final_score));
  const min = Math.min(...results.map(r => r.final_score));

  const getColor = (score) => {
    const norm = max === min ? 0.5 : (score - min) / (max - min);
    if (norm >= 0.7) return { bg: "#16a34a", text: "#fff", opacity: 0.9 };
    if (norm >= 0.4) return { bg: "#f59e0b", text: "#fff", opacity: 0.8 };
    return { bg: "#dc2626", text: "#fff", opacity: 0.7 };
  };

  return (
    <div className="heatmap-container">
      <h3 className="heatmap-title">🗺️ خريطة حرارية — {categoryArabic[category] || category}</h3>
      <div className="heatmap-legend">
        <span className="legend-item"><span className="legend-dot" style={{ background: "#16a34a" }} />مناسب جداً (70+)</span>
        <span className="legend-item"><span className="legend-dot" style={{ background: "#f59e0b" }} />مناسب (50-69)</span>
        <span className="legend-item"><span className="legend-dot" style={{ background: "#dc2626" }} />غير مناسب (أقل من 50)</span>
      </div>
      <div className="heatmap-grid">
        {results.map((r, i) => {
          const c = getColor(r.final_score);
          return (
            <div
              key={i}
              className="heatmap-cell"
              style={{ background: c.bg, opacity: c.opacity }}
              title={`${r.neighborhood}: ${r.final_score}/100`}
            >
              <span className="cell-name">{r.neighborhood}</span>
              <span className="cell-score">{r.final_score}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ===== Logo Image =====
function Logo({ size = 32, dark = false }) {
  return (
    <img
      src="/forsati_logo.png"
      alt="فرصتي لوقو"
      style={{
        width: size,
        height: size,
        objectFit: "contain",
        mixBlendMode: dark ? "screen" : "multiply",
        background: "transparent",
        display: "block",
      }}
    />
  );
}

// ===== Footer =====
function Footer() {
  return (
    <footer className="footer" dir="rtl">
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">
            <img src="/forsati_logo.png" alt="فرصتي" className="footer-logo-img" />
            <span>فرصتي</span>
          </div>
          <p className="footer-tagline">اختر موقعك بثقة، وابدأ استثمارك بذكاء</p>
        </div>

        <div className="footer-links">
          <h4>روابط سريعة</h4>
          <ul>
            <li><a href="#home">الرئيسية</a></li>
            <li><a href="#about">عن المشروع</a></li>
            <li><a href="#faq">الأسئلة الشائعة</a></li>
            <li><a href="#contact">تواصل معنا</a></li>
          </ul>
        </div>

        <div className="footer-social">
          <h4>تابعونا</h4>
          <div className="social-icons">
            <a href="#" className="social-icon" aria-label="تويتر/X">
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a>
            <a href="#" className="social-icon" aria-label="انستقرام">
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" />
              </svg>
            </a>
            <a href="#" className="social-icon" aria-label="لينكد إن">
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
              </svg>
            </a>
            <a href="#" className="social-icon" aria-label="يوتيوب">
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
              </svg>
            </a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <p>© 2025 فرصتي — جميع الحقوق محفوظة</p>
      </div>
    </footer>
  );
}

// ===== Main App =====
export default function App() {
  const [page, setPage] = useState("home");
  const [categories, setCategories] = useState([]);
  const [neighborhoods, setNeighborhoods] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedNeighborhood, setSelectedNeighborhood] = useState("");
  const [searchMode, setSearchMode] = useState("rank");
  const [viewMode, setViewMode] = useState("list"); // list | heatmap
  const [results, setResults] = useState([]);
  const [detailResult, setDetailResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [openFaq, setOpenFaq] = useState(null);
  const [contactForm, setContactForm] = useState({ name: "", email: "", msg: "" });
  const [contactSent, setContactSent] = useState(false);
  const [activeNav, setActiveNav] = useState("home");

  useEffect(() => {
    axios.get(`${API}/api/categories`).then(r => setCategories(r.data.categories)).catch(() => {});
    axios.get(`${API}/api/neighborhoods`).then(r => setNeighborhoods(r.data.neighborhoods)).catch(() => {});
  }, []);

  const scrollTo = (id) => {
    setPage("home");
    setTimeout(() => {
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  const handleSearch = async () => {
    if (!selectedCategory) { setError("اختاري نوع المشروع"); return; }
    setError(""); setLoading(true);
    try {
      if (searchMode === "rank") {
        const r = await axios.post(`${API}/api/rank`, { category: selectedCategory.trim().toLowerCase(), top_n: 10 });
        setResults(r.data.rankings);
        setPage("results");
      } else {
        if (!selectedNeighborhood) { setError("اختاري الحي"); setLoading(false); return; }
        const r = await axios.post(`${API}/api/evaluate`, { category: selectedCategory.trim().toLowerCase(), neighborhood: selectedNeighborhood.trim() });
        setDetailResult(r.data);
        setPage("detail");
      }
    } catch (e) { setError("حدث خطأ، حاولي مرة ثانية"); }
    setLoading(false);
  };

  const scoreColor = (s) => s >= 70 ? "#16a34a" : s >= 50 ? "#ca8a04" : "#dc2626";
  const scoreLabel = (s) => s >= 70 ? "مناسب جداً ✅" : s >= 50 ? "مناسب 🟡" : "غير مناسب ❌";

  // ===== Header shared =====
  const Header = ({ showBack = false }) => (
    <header className="header">
      <div className="header-logo" onClick={() => setPage("home")}>
        <img src="/forsati_logo.png" alt="فرصتي" className="header-logo-img" />
      </div>
      {showBack ? (
        <button className="back-btn" onClick={() => setPage(results.length && page === "detail" ? "results" : "home")}>← رجوع</button>
      ) : (
        <nav className="nav">
          <a href="#home" onClick={(e) => { e.preventDefault(); scrollTo("home-top"); }}>الرئيسية</a>
          <a href="#about" onClick={(e) => { e.preventDefault(); scrollTo("about"); }}>عن المشروع</a>
          <a href="#faq" onClick={(e) => { e.preventDefault(); scrollTo("faq"); }}>الأسئلة الشائعة</a>
          <a href="#contact" onClick={(e) => { e.preventDefault(); scrollTo("contact"); }}>تواصل معنا</a>
        </nav>
      )}
    </header>
  );

  // ===== Results Page =====
  if (page === "results") return (
    <div className="page" dir="rtl">
      <Header showBack />
      <div className="results-container">
        <h2 className="results-title">
          أفضل الأحياء لـ <span className="highlight">{categoryArabic[selectedCategory]}</span>
        </h2>

        {/* View Toggle */}
        <div className="view-toggle">
          <button className={viewMode === "list" ? "view-btn active" : "view-btn"} onClick={() => setViewMode("list")}>📋 قائمة</button>
          <button className={viewMode === "heatmap" ? "view-btn active" : "view-btn"} onClick={() => setViewMode("heatmap")}>🌡️ خريطة حرارية</button>
        </div>

{viewMode === "heatmap" ? (
  <MapHeatView
    category={selectedCategory}
  />
) : (
          <div className="results-grid">
            {results.map((r, i) => (
              <div key={i} className="result-card" onClick={() => { setDetailResult(r); setPage("detail"); }}>
                <div className="rank-badge">#{i + 1}</div>
                <div className="card-body">
                  <h3 className="neighborhood-name">{r.neighborhood}</h3>
                  <div className="score-bar-container">
                    <div className="score-bar" style={{ width: `${r.final_score}%`, background: scoreColor(r.final_score) }} />
                  </div>
                  <div className="card-footer">
                    <span className="score-num" style={{ color: scoreColor(r.final_score) }}>{r.final_score}/100</span>
                    <span className="score-label">{scoreLabel(r.final_score)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      <Footer />
    </div>
  );

  // ===== Detail Page =====
  if (page === "detail" && detailResult) return (
    <div className="page" dir="rtl">
      <Header showBack />
      <div className="detail-container">
        <div className="detail-hero" style={{ borderColor: scoreColor(detailResult.final_score) }}>
          <h2>{detailResult.neighborhood}</h2>
          <p className="detail-category">{categoryArabic[detailResult.category] || detailResult.category}</p>
          <div className="big-score" style={{ color: scoreColor(detailResult.final_score) }}>
            {detailResult.final_score}<span>/100</span>
          </div>
          <div className="big-label">{scoreLabel(detailResult.final_score)}</div>
        </div>
        {detailResult.details && (
          <div className="detail-breakdown">
            <h3>تفاصيل التقييم</h3>
            {[
              { label: "توقع النموذج 🤖", key: "ml_probability" },
              { label: "الطلب والكثافة السكانية 👥", key: "demand_score" },
              { label: "مستوى المنافسة ⚖️", key: "competition_score" },
              { label: "النشاط التجاري القريب 🏪", key: "nearby_activity_score" },
              { label: "المواصلات العامة 🚇", key: "transport_score" },
              { label: "قوة السوق 📊", key: "market_strength_score" },
            ].map((item) => (
              <div key={item.key} className="breakdown-row">
                <span className="breakdown-label">{item.label}</span>
                <div className="breakdown-bar-container">
                  <div className="breakdown-bar" style={{ width: `${detailResult.details[item.key]}%`, background: scoreColor(detailResult.details[item.key]) }} />
                </div>
                <span className="breakdown-score">{detailResult.details[item.key]}%</span>
              </div>
            ))}
          </div>
        )}
      </div>
      <Footer />
    </div>
  );

  // ===== Home Page =====
  return (
    <div className="page" dir="rtl" id="home-top">
      <Header />

      {/* ===== Hero ===== */}
      <section className="hero" id="hero" style={{ backgroundImage: "url('/forsati_bg.jpg')" }}>
        <div className="hero-bg-overlay" />
        <div className="hero-content">
          <div className="hero-logo-wrap">
            <img src="/forsati_logo.png" alt="فرصتي" className="hero-logo-img" />
          </div>
          <h1 className="hero-title">فرصتي</h1>
          <p className="hero-subtitle">اختر موقعك بثقة ... وابدأ استثمارك بذكاء</p>
          <div className="hero-btns">
            <button className="hero-btn" onClick={() => document.getElementById("search").scrollIntoView({ behavior: "smooth" })}>
              ابدأ الآن
            </button>
            <button className="hero-btn-outline" onClick={() => document.getElementById("about").scrollIntoView({ behavior: "smooth" })}>
              تعرف على المشروع
            </button>
          </div>
        </div>
        <div className="hero-stats">
          <div className="stat-card"><span className="stat-num">28+</span><span className="stat-label">نوع نشاط</span></div>
          <div className="stat-card"><span className="stat-num">50+</span><span className="stat-label">حي في الرياض</span></div>
          <div className="stat-card"><span className="stat-num">6</span><span className="stat-label">معايير تقييم</span></div>
        </div>
      </section>

      {/* ===== Search Section ===== */}
      <section className="search-section" id="search">
        <h2 className="search-title">ابحث بكل سهوله مع مساعدك الذكي!</h2>
        <div className="mode-toggle">
          <button className={searchMode === "rank" ? "mode-btn active" : "mode-btn"} onClick={() => setSearchMode("rank")}>أفضل الأحياء لنشاطي</button>
          <button className={searchMode === "evaluate" ? "mode-btn active" : "mode-btn"} onClick={() => setSearchMode("evaluate")}>تقييم حي محدد</button>
        </div>
        <div className="search-bar">
          <div className="select-wrapper">
            <span className="select-icon">📋</span>
            <select value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)} className="select-input">
              <option value="">نوع المشروع</option>
              {categories.map(c => <option key={c} value={c}>{categoryArabic[c] || c}</option>)}
            </select>
          </div>
          {searchMode === "evaluate" && (
            <div className="select-wrapper">
              <span className="select-icon">📍</span>
              <select value={selectedNeighborhood} onChange={e => setSelectedNeighborhood(e.target.value)} className="select-input">
                <option value="">اختاري الحي</option>
                {neighborhoods.map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
          )}
          <button className="search-btn" onClick={handleSearch} disabled={loading}>
            {loading ? "⏳ جاري البحث..." : "🔍 ابحث"}
          </button>
        </div>
        {error && <p className="error-msg">{error}</p>}
      </section>

<section className="categories-section">
  <div className="categories-header">
    <h2>الفئات التجارية المتوفرة</h2>
  </div>

  <div className="categories-slider">
    {Object.entries(categoryArabic).map(([key, label], i) => {

      const icons = {
        restaurant: "🍽️",
        cafe: "☕",
        supermarket: "🛒",
        pharmacy: "💊",
        bakery: "🥐",
        gym: "🏋️",
        hotel: "🏨",
        clothing: "👕",
        electronics: "💻",
        furniture: "🛋️",
        barber: "✂️",
        salon: "💅",
        gas_station: "⛽",
        laundry: "🧺",
        jewelry: "💍",
        grocery: "🛍️",
        shoes: "👟",
        sports_clothing: "🎽",
        curtains: "🪟",
        lighting: "💡",
        sweets: "🍰",
        perfume: "🌸",
        spa: "🧖",
        auto_repair: "🚗",
        toys: "🧸",
        pet_shop: "🐾",
        gifts: "🎁",
        eyewear: "👓"
      };

      return (
        <div
          key={i}
          className="category-card slider-card"
          onClick={() => {
            setSelectedCategory(key);
            setSearchMode("rank");

            document.getElementById("search")
              .scrollIntoView({ behavior: "smooth" });
          }}
        >
          <span className="category-icon">
            {icons[key] || "🏪"}
          </span>

          <span>{label}</span>
        </div>
      );
    })}
  </div>
</section>

      {/* ===== About Section ===== */}
      <section className="about-section" id="about">
        <div className="about-inner">
          <div className="section-badge">عن المشروع</div>
          <h2 className="section-title">ما هي فرصتي؟</h2>
          <p className="about-text">
            فرصتي هي منصة ذكية تساعد رواد الأعمال والمستثمرين في اختيار الموقع المثالي لمشاريعهم التجارية
            داخل مدينة الرياض. تعتمد المنصة على نماذج تعلم آلي متقدمة تحلل بيانات حقيقية من أحياء المدينة
            لتقديم توصيات دقيقة وموثوقة.
          </p>
          <div className="about-features">
            {[
              { icon: "🤖", title: "ذكاء اصطناعي", desc: "نموذج XGBoost مدرّب على بيانات حقيقية من الرياض" },
              { icon: "📊", title: "تحليل شامل", desc: "6 معايير تقييم تشمل المنافسة والكثافة السكانية والنقل" },
              { icon: "⚡", title: "نتائج فورية", desc: "احصل على تقييمك في ثوانٍ معدودة" },
              { icon: "🎯", title: "دقة عالية", desc: "توصيات مبنية على إحصائيات رسمية وبيانات موثوقة" },
            ].map((f, i) => (
              <div key={i} className="feature-card">
                <span className="feature-icon">{f.icon}</span>
                <h4>{f.title}</h4>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== Reviews Section ===== */}
      <section className="reviews-section" id="reviews">
        <div className="section-badge">آراء المستخدمين</div>
        <h2 className="section-title">ماذا يقولون عنا؟</h2>
        <div className="reviews-grid">
          {reviews.map((r, i) => (
            <div key={i} className="review-card">
              <div className="review-stars">{"⭐".repeat(r.stars)}</div>
              <p className="review-text">"{r.text}"</p>
              <div className="reviewer">
                <div className="reviewer-avatar">{r.name[0]}</div>
                <div>
                  <div className="reviewer-name">{r.name}</div>
                  <div className="reviewer-role">{r.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ===== FAQ Section ===== */}
      <section className="faq-section" id="faq">
        <div className="faq-inner">
          <div className="section-badge">الأسئلة الشائعة</div>
          <h2 className="section-title">هل لديك سؤال؟</h2>
          <div className="faq-list">
            {faqs.map((f, i) => (
              <div key={i} className={`faq-item ${openFaq === i ? "open" : ""}`}>
                <button className="faq-q" onClick={() => setOpenFaq(openFaq === i ? null : i)}>
                  <span>{f.q}</span>
                  <span className="faq-arrow">{openFaq === i ? "▲" : "▼"}</span>
                </button>
                {openFaq === i && <div className="faq-a">{f.a}</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== Contact Section ===== */}
      <section className="contact-section" id="contact">
        <div className="contact-inner">
          <div className="section-badge">تواصل معنا</div>
          <h2 className="section-title">نحن هنا لمساعدتك</h2>
          {contactSent ? (
            <div className="contact-success">
              <span>✅</span>
              <p>شكراً! تم استلام رسالتك وسنتواصل معك قريباً.</p>
            </div>
          ) : (
            <div className="contact-form">
              <div className="form-row">
                <input className="form-input" placeholder="الاسم" value={contactForm.name}
                  onChange={e => setContactForm({ ...contactForm, name: e.target.value })} />
                <input className="form-input" placeholder="البريد الإلكتروني" value={contactForm.email}
                  onChange={e => setContactForm({ ...contactForm, email: e.target.value })} />
              </div>
              <textarea className="form-textarea" placeholder="رسالتك..." rows={4} value={contactForm.msg}
                onChange={e => setContactForm({ ...contactForm, msg: e.target.value })} />
              <button className="form-submit" onClick={() => {
                if (contactForm.name && contactForm.email && contactForm.msg) setContactSent(true);
              }}>إرسال الرسالة</button>
            </div>
          )}
          <div className="contact-info">
            <div className="contact-info-item">📧 <span>forsati@example.com</span></div>
            <div className="contact-info-item">📍 <span>الرياض، المملكة العربية السعودية</span></div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}