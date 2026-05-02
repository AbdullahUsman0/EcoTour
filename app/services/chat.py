from app.data.knowledge import DESTINATION_TIPS


def bilingual(text_en: str, text_ur: str, language: str) -> str:
    if language.lower().startswith("ur"):
        return text_ur
    return text_en


def detect_question_type(message: str) -> str:
    """Detect the type of question to provide targeted responses."""
    lowered = message.lower()
    
    if any(word in lowered for word in ["budget", "cost", "price", "افراد", "رقم", "پیسے"]):
        return "budget"
    if any(word in lowered for word in ["emergency", "crisis", "help", "danger", "ہنگامی", "مدد"]):
        return "emergency"
    if any(word in lowered for word in ["weather", "climate", "season", "موسم", "موسم_کا"]):
        return "weather"
    if any(word in lowered for word in ["hotel", "stay", "accommodation", "lodge", "ہوٹل", "ٹھہرنا"]):
        return "accommodation"
    if any(word in lowered for word in ["food", "eat", "restaurant", "cuisine", "کھانا", "کھانے"]):
        return "food"
    if any(word in lowered for word in ["transport", "travel", "car", "bus", "flight", "گاڑی", "سفر"]):
        return "transport"
    if any(word in lowered for word in ["activity", "trek", "hike", "climb", "adventure", "سرگرمی", "پہاڑ"]):
        return "activity"
    if any(word in lowered for word in ["safe", "security", "security", "danger", "محفوظ", "خطرہ"]):
        return "safety"
    
    return "general"


def generate_chat_reply(message: str, language: str) -> str:
    """Generate contextual chat responses based on question type."""
    lowered = message.lower()
    question_type = detect_question_type(message)
    
    # Destination-specific tips
    for destination, tips in DESTINATION_TIPS.items():
        if destination.lower() in lowered:
            joined = " ".join(tips)
            return bilingual(
                f"🎯 **{destination.title()}** - Essential Guide:\n\n{joined}\n\n💡 Pro Tip: Share your exact dates and budget for a personalized itinerary!",
                f"🎯 **{destination.title()}** - ضروری رہنمائی:\n\n{joined}\n\n💡 Pro Tip: اپنی تاریخیں اور بجٹ شیئر کریں برائے منصوبہ!",
                language,
            )
    
    # Type-specific responses
    if question_type == "budget":
        return bilingual(
            "💰 **Budget Planning for Pakistan Tours**\n\n"
            "Budget varies by destination:\n"
            "• **Northern Areas** (Skardu, Nanga Parbat): PKR 15,000-25,000/day\n"
            "• **Coastal** (Karachi, Gwadar): PKR 8,000-15,000/day\n"
            "• **Historical** (Lahore, Peshawar): PKR 5,000-12,000/day\n\n"
            "Share origin → destination → budget for accurate cost breakdown!",
            "💰 **پاکستان کے ٹور کے لیے بجٹ**\n\n"
            "بجٹ منزل کے لحاظ سے مختلف ہے:\n"
            "• **شمالی علاقے** (سکردو، نانگا پربت): روزانہ PKR 15,000-25,000\n"
            "• **ساحلی** (کراچی، گوادر): روزانہ PKR 8,000-15,000\n"
            "• **تاریخی** (لاہور، پشاور): روزانہ PKR 5,000-12,000\n\n"
            "درست تفصیل کے لیے اپنی أصل → منزل → بجٹ بتائیں!",
            language,
        )
    
    if question_type == "weather":
        return bilingual(
            "🌤️ **Pakistan Weather & Best Seasons**\n\n"
            "• **Spring (Mar-May)**: Perfect weather! Temperature 20-28°C\n"
            "• **Summer (Jun-Aug)**: Hot, rain expected in mountains\n"
            "• **Fall (Sep-Nov)**: Clear skies, ideal for trekking\n"
            "• **Winter (Dec-Feb)**: Snow in north, cold in plains\n\n"
            "Tell me your destination to get specific weather advice!",
            "🌤️ **پاکستان میں موسم اور بہترین سیزن**\n\n"
            "• **بہار (مارچ-مئی)**: بہترین موسم! درجۂ حرارت 20-28°C\n"
            "• **گرمی (جون-اگست)**: گرم، پہاڑوں میں بارش\n"
            "• **خریف (ستمبر-نومبر)**: صاف آسمان، پیدل چلنے کے لیے بہترین\n"
            "• **سردی (دسمبر-فروری)**: شمال میں برف، میدانوں میں سردی\n\n"
            "مجھے اپنی منزل بتائیں تاکہ میں مخصوص موسم کی رہنمائی دے سکوں!",
            language,
        )
    
    if question_type == "accommodation":
        return bilingual(
            "🏨 **Accommodation Options in Pakistan**\n\n"
            "**Budget**: Hostels & Basic Hotels (PKR 2,000-4,000/night)\n"
            "**Mid-Range**: Comfortable Hotels & Lodges (PKR 4,000-8,000/night)\n"
            "**Premium**: 4-5 Star Hotels & Resorts (PKR 8,000+/night)\n\n"
            "📌 **Popular chains**: Serena Hotels, Pearl Continental, Memories\n\n"
            "What's your preferred destination? I can suggest specific properties!",
            "🏨 **پاکستان میں رہائش کے اختیارات**\n\n"
            "**سستا**: Hostels اور بنیادی ہوٹل (رات میں PKR 2,000-4,000)\n"
            "**درمیانی**: آرام دہ ہوٹل اور Lodge (رات میں PKR 4,000-8,000)\n"
            "**پریمیم**: 4-5 ستاروں کے ہوٹل (رات میں PKR 8,000+)\n\n"
            "📌 **مشہور چین**: سرینا ہوٹلز، پرل کانٹینینٹل، میموریز\n\n"
            "آپ کی پسند کی منزل کیا ہے؟ میں مخصوص ہوٹل تجویز کر سکتا ہوں!",
            language,
        )
    
    if question_type == "food":
        return bilingual(
            "🍜 **Pakistani Cuisine & Food Scene**\n\n"
            "**Must-try dishes**:\n"
            "• Biryani (Karachi & Lahore specialty)\n"
            "• Nihari & Haleem (breakfast delights)\n"
            "• Chapli Kebab (Peshawar famous)\n"
            "• Dahi Bhalle & Lassi (refreshing)\n\n"
            "**Budget**: Street food PKR 200-500, Restaurants PKR 500-1500\n\n"
            "Share your destination to get local food recommendations!",
            "🍜 **پاکستانی کھانے اور کھانے کا منظر**\n\n"
            "**لازمی آزمائیں**:\n"
            "• بریانی (کراچی و لاہور کی خصوصیت)\n"
            "• نہاری اور حلیم (صبح کے کھانوں میں شاندار)\n"
            "• چپلی کباب (پشاور میں مشہور)\n"
            "• دہی بھلے اور لسی (تازگی بخش)\n\n"
            "**بجٹ**: سڑک کا کھانا PKR 200-500، ریستوران PKR 500-1500\n\n"
            "مقامی کھانے کی سفارشات کے لیے اپنی منزل بتائیں!",
            language,
        )
    
    if question_type == "transport":
        return bilingual(
            "🚗 **Getting Around Pakistan**\n\n"
            "**Options**:\n"
            "• **Bus**: PKR 500-2000 (budget, scenic routes)\n"
            "• **Car Rental**: PKR 3000-8000/day (flexible, comfortable)\n"
            "• **Domestic Flights**: PKR 5000-15000 (save time, north routes)\n"
            "• **Local Taxis**: Metered in cities, negotiate for long trips\n\n"
            "💡 **Safety**: Use registered services, travel during daylight!",
            "🚗 **پاکستان میں سفر کرنا**\n\n"
            "**اختیارات**:\n"
            "• **بس**: PKR 500-2000 (سستا، خوبصورت راستہ)\n"
            "• **کار کرائے پر**: PKR 3000-8000/دن (لچکدار، آرام دہ)\n"
            "• **ہوائی جہاز**: PKR 5000-15000 (وقت بچائیں، شمالی راستے)\n"
            "• **مقامی ٹیکسی**: شہروں میں میٹر، لمبے سفر میں سودا کریں\n\n"
            "💡 **حفاظت**: رجسٹرڈ سروسز استعمال کریں، دن میں سفر کریں!",
            language,
        )
    
    if question_type == "activity":
        return bilingual(
            "🏔️ **Adventure Activities in Pakistan**\n\n"
            "**Trekking**: K2, Fairy Meadows, Swat Valley trails\n"
            "**Mountaineering**: Kilimanjaro-style peaks, proper guides needed\n"
            "**Water Sports**: Kayaking in northern rivers, beach sports\n"
            "**Cultural**: Bazaars, ancient sites, local markets\n\n"
            "⚠️ **Safety first**: Hire certified guides, carry maps & supplies!",
            "🏔️ **پاکستان میں مہم جوئی کی سرگرمیاں**\n\n"
            "**پیدل سفر**: K2، فیری میڈوز، سوات وادی کی پگڈنڈیاں\n"
            "**پہاڑ پر چڑھنا**: کلمنجارو جیسی چوٹیاں، مجاز رہنماؤں کی ضرورت\n"
            "**پانی کی سپورٹس**: شمالی دریاؤں میں کیکنگ، ساحل کی سپورٹس\n"
            "**ثقافتی**: بازار، قدیم مقام، مقامی منڈیاں\n\n"
            "⚠️ **حفاظت پہلے**: مجاز رہنما کرائے پر لیں، نقشے اور سامان رکھیں!",
            language,
        )
    
    if question_type == "safety":
        return bilingual(
            "🛡️ **Travel Safety in Pakistan**\n\n"
            "**Safe for tourists**: Most major destinations are tourist-friendly\n"
            "**Best practices**:\n"
            "• Travel with guides in remote areas\n"
            "• Keep copies of important documents\n"
            "• Stay updated on local news\n"
            "• Use official transportation\n\n"
            "🆘 For emergencies, use the Crisis Help tab. Stay safe!",
            "🛡️ **پاکستان میں سفر کی حفاظت**\n\n"
            "**سیاحوں کے لیے محفوظ**: زیادہ تر بڑی منزلین سیاحتوں کے لیے دوستانہ ہیں\n"
            "**بہترین طریقے**:\n"
            "• دور دراز علاقوں میں رہنما کے ساتھ سفر کریں\n"
            "• اہم دستاویزات کی کاپی رکھیں\n"
            "• مقامی خبروں سے اپ ڈیٹ رہیں\n"
            "• سرکاری ٹرانسپورٹ استعمال کریں\n\n"
            "🆘 ہنگامی حالات میں، Crisis Help ٹیب استعمال کریں۔ محفوظ رہیں!",
            language,
        )
    
    if question_type == "emergency":
        return bilingual(
            "🆘 **Emergency Support Available**\n\n"
            "Please use the **Crisis Help** tab in the app for immediate assistance.\n\n"
            "**Quick emergency numbers**:\n"
            "• Police: 15\n"
            "• Ambulance: 1122\n"
            "• Tourist Police: +92-51-2817-7734\n\n"
            "Stay safe! Help is always available.",
            "🆘 **ہنگامی مدد دستیاب ہے**\n\n"
            "براہ کرم فوری معاونت کے لیے ایپ میں **Crisis Help** ٹیب استعمال کریں۔\n\n"
            "**فوری ہنگامی نمبر**:\n"
            "• پولیس: 15\n"
            "• ایمبولینس: 1122\n"
            "• سیاحتی پولیس: +92-51-2817-7734\n\n"
            "محفوظ رہیں! مدد ہمیشہ دستیاب ہے۔",
            language,
        )
    
    # General response
    return bilingual(
        "🌍 **How can I help you explore Pakistan?**\n\n"
        "I can help with:\n"
        "• 📍 **Trip Planning** - Suggest routes & itineraries\n"
        "• 💰 **Budget Calculator** - Estimate costs\n"
        "• 🏨 **Accommodation** - Hotel suggestions\n"
        "• 🛡️ **Safety Info** - Travel safety tips\n"
        "• 🍜 **Food & Culture** - Local cuisine guide\n"
        "• 🧗 **Activities** - Adventure suggestions\n\n"
        "What would you like to know?",
        "🌍 **میں آپ کو پاکستان کی تلاش میں کیسے مدد کر سکتا ہوں؟**\n\n"
        "میں مدد کر سکتا ہوں:\n"
        "• 📍 **سفر کی منصوبہ بندی** - راستے اور منصوبہ\n"
        "• 💰 **بجٹ کیلکولیٹر** - اخراجات کا تخمینہ\n"
        "• 🏨 **رہائش** - ہوٹل کی تجاویز\n"
        "• 🛡️ **حفاظت کی معلومات** - سفر کی حفاظت کے تجاویز\n"
        "• 🍜 **کھانا اور ثقافت** - مقامی کھانوں کی رہنمائی\n"
        "• 🧗 **سرگرمیاں** - مہم جوئی کی تجاویز\n\n"
        "آپ کیا جاننا چاہتے ہیں؟",
        language,
    )


def fallback_rag_style_reply(message: str, context: str, language: str) -> str:
    """Improved fallback response with better formatting."""
    question_type = detect_question_type(message)
    
    if language.lower().startswith("ur"):
        return (
            f"📚 **متعلقہ معلومات ملی ہے:**\n\n"
            f"{context[:700]}\n\n"
            f"💡 **مزید معلومات کے لیے:**\n"
            f"• اپنی منزل بتائیں\n"
            f"• بجٹ اور تاریخیں شیئر کریں\n"
            f"• مخصوص سرگرمیوں کے بارے میں پوچھیں"
        )
    
    return (
        f"📚 **Found relevant information:**\n\n"
        f"{context[:700]}\n\n"
        f"💡 **For more specific advice:**\n"
        f"• Share your exact destination\n"
        f"• Mention your budget and dates\n"
        f"• Ask about specific activities or interests"
    )
