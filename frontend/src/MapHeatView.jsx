import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const API = "http://127.0.0.1:5000";

// ========== إضافة قاموس الترجمة للأحياء ==========
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

function getNeighborhoodLabel(name, lang) {
  return lang === "en" ? (neighborhoodEnglish[name] || name) : name;
}
// ===============================================

function getColor(score) {
  if (score >= 70) return "#16a34a";
  if (score >= 50) return "#f59e0b";
  return "#dc2626";
}

function FlyTo({ position }) {
  const map = useMap();

  useEffect(() => {
    if (position) {
      map.flyTo(position, 13, { duration: 1.5 });
    }
  }, [position]);

  return null;
}

export default function MapHeatView({ category, lang }) {  // ✅ استقبال lang
  const [data, setData] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetch(`${API}/api/map/${category}`)
      .then(res => res.json())
      .then(json => {
        setData((json.rankings || []).slice(0, 10));
      });
  }, [category]);

  const createIcon = (score) =>
    L.divIcon({
      html: `
        <div style="
          background:${getColor(score)};
          width:22px;
          height:22px;
          border-radius:50%;
          border:3px solid white;
          box-shadow:0 0 10px rgba(0,0,0,.3);
        "></div>
      `,
      className: "",
      iconSize: [22, 22]
    });

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "2fr 1fr",
        gap: "18px",
        height: "620px",
        fontFamily: "Tajawal"
      }}
    >
      {/* ===== MAP ===== */}
      <div
        style={{
          borderRadius: "18px",
          overflow: "hidden",
          boxShadow: "0 10px 30px rgba(0,0,0,.12)"
        }}
      >
        <MapContainer
          center={[24.7136, 46.6753]}
          zoom={11}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {selected && (
            <FlyTo position={[selected.lat, selected.lon]} />
          )}

          {data.map((item, i) => (
            <Marker
              key={i}
              position={[item.lat, item.lon]}
              icon={createIcon(item.final_score)}
              eventHandlers={{
                click: () => setSelected(item)
              }}
            >
              <Popup>
                <div dir={lang === "ar" ? "rtl" : "ltr"} style={{ textAlign: lang === "ar" ? "right" : "left" }}>
                  {/* ✅ تعديل عرض اسم الحي */}
                  <strong>{getNeighborhoodLabel(item.neighborhood, lang)}</strong>
                  <br />
                  {lang === "ar" ? "التقييم: " : "Score: "}{item.final_score}/100
                  <br />
                  {item.final_score >= 70
                    ? (lang === "ar" ? "مناسب جداً" : "Highly Suitable")
                    : item.final_score >= 50
                    ? (lang === "ar" ? "مناسب" : "Suitable")
                    : (lang === "ar" ? "ضعيف" : "Poor")}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* ===== SIDE LIST ===== */}
      <div
        style={{
          background: "#ffffff",
          borderRadius: "18px",
          boxShadow: "0 10px 25px rgba(0,0,0,.08)",
          padding: "18px",
          overflowY: "auto"
        }}
      >
        <h2
          style={{
            marginBottom: "16px",
            fontSize: "22px",
            fontWeight: "800",
            color: "#111827"
          }}
        >
          {lang === "ar" ? "أفضل 10 أحياء" : "Top 10 Neighborhoods"}
        </h2>

        {data.map((item, i) => (
          <div
            key={i}
            onClick={() => setSelected(item)}
            style={{
              padding: "14px",
              marginBottom: "10px",
              borderRadius: "14px",
              cursor: "pointer",
              background:
                selected?.neighborhood === item.neighborhood
                  ? "#ecfdf5"
                  : "#f9fafb",
              border:
                selected?.neighborhood === item.neighborhood
                  ? "2px solid #16a34a"
                  : "1px solid #e5e7eb",
              transition: ".2s"
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "6px"
              }}
            >
              {/* ✅ تعديل عرض اسم الحي */}
              <strong>{i + 1}. {getNeighborhoodLabel(item.neighborhood, lang)}</strong>
              <span style={{ color: getColor(item.final_score) }}>
                {item.final_score}
              </span>
            </div>

            <div
              style={{
                height: "8px",
                borderRadius: "20px",
                background: "#e5e7eb"
              }}
            >
              <div
                style={{
                  width: `${item.final_score}%`,
                  height: "100%",
                  borderRadius: "20px",
                  background: getColor(item.final_score)
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}