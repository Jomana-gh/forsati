import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  ar: {
    translation: {
      home: "الرئيسية",
      about: "عن المشروع",
      faq: "الأسئلة الشائعة",
      contact: "تواصل معنا",

      heroTitle: "فرصتي",
      heroSubtitle: "اختر موقعك بثقة ... وابدأ استثمارك بذكاء",

      startNow: "ابدأ الآن",
      learnMore: "تعرف على المشروع",

      searchTitle: "ابحث بكل سهولة مع مساعدك الذكي!",
      bestNeighborhoods: "أفضل الأحياء لنشاطي",
      evaluateNeighborhood: "تقييم حي محدد",

      projectType: "نوع المشروع",
      chooseNeighborhood: "اختاري الحي",

      search: "ابحث",
      loading: "جاري البحث...",

      availableCategories: "الفئات التجارية المتوفرة",

      aboutBadge: "عن المشروع",
      whatIsForsati: "ما هي فرصتي؟",

      reviewsTitle: "ماذا يقولون عنا؟",
      reviewsBadge: "آراء المستخدمين",

      faqTitle: "هل لديك سؤال؟",

      contactTitle: "نحن هنا لمساعدتك",
      contactBadge: "تواصل معنا",

      send: "إرسال الرسالة",

      quickLinks: "روابط سريعة",
      followUs: "تابعونا",

      rights: "جميع الحقوق محفوظة",

      suitableVery: "مناسب جداً ✅",
      suitable: "مناسب 🟡",
      unsuitable: "غير مناسب ❌",

      list: "قائمة",
      heatmap: "خريطة حرارية",
    },
  },

  en: {
    translation: {
      home: "Home",
      about: "About",
      faq: "FAQ",
      contact: "Contact",

      heroTitle: "Forsati",
      heroSubtitle: "Choose your location wisely and invest smarter",

      startNow: "Start Now",
      learnMore: "Learn More",

      searchTitle: "Search Easily With Your Smart Assistant!",
      bestNeighborhoods: "Best Areas For My Business",
      evaluateNeighborhood: "Evaluate Specific Area",

      projectType: "Project Type",
      chooseNeighborhood: "Choose Neighborhood",

      search: "Search",
      loading: "Searching...",

      availableCategories: "Available Business Categories",

      aboutBadge: "About",
      whatIsForsati: "What is Forsati?",

      reviewsTitle: "What Users Say",
      reviewsBadge: "Reviews",

      faqTitle: "Do You Have Questions?",

      contactTitle: "We Are Here To Help",
      contactBadge: "Contact Us",

      send: "Send Message",

      quickLinks: "Quick Links",
      followUs: "Follow Us",

      rights: "All Rights Reserved",

      suitableVery: "Excellent ✅",
      suitable: "Good 🟡",
      unsuitable: "Not Suitable ❌",

      list: "List",
      heatmap: "Heatmap",
    },
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: "ar",
  fallbackLng: "ar",

  interpolation: {
    escapeValue: false,
  },
});

export default i18n;

