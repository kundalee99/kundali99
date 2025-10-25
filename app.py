from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
import os
import random
import base64
from io import BytesIO
import tempfile
import requests
import time

# CORRECT CASHFREE IMPORTS FOR v4.3.10
try:
    from cashfree_pg.models.create_order_request import CreateOrderRequest
    from cashfree_pg.api_client import Cashfree
    from cashfree_pg.models.customer_details import CustomerDetails
    from cashfree_pg.models.order_meta import OrderMeta
    CASHFREE_AVAILABLE = True
    print("✅ Cashfree SDK v4.3.10 imported successfully")
except ImportError as e:
    print(f"❌ Cashfree import error: {e}")
    CASHFREE_AVAILABLE = False
    Cashfree = None

import hmac
import hashlib

# Try different PDF libraries
try:
    from weasyprint import HTML
    PDF_ENGINE = 'weasyprint'
    print("✅ Using WeasyPrint for PDF generation")
except ImportError:
    try:
        import pdfkit
        PDF_ENGINE = 'pdfkit'
        print("✅ Using pdfkit for PDF generation")
    except ImportError:
        try:
            from xhtml2pdf import pisa
            PDF_ENGINE = 'xhtml2pdf'
            print("✅ Using xhtml2pdf for PDF generation")
        except ImportError:
            PDF_ENGINE = None
            print("❌ No PDF library available - using HTML fallback")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
CORS(app, origins=[
    "https://kundali99.com",
    "https://www.kundali99.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
])


# Real Lord Ganesha image URL
GANESHA_IMAGE_URL = "https://i.ibb.co/tgvs8sc/ganesha.jpg"

# Cashfree Configuration
CASHFREE_APP_ID = os.environ.get('CASHFREE_APP_ID')
CASHFREE_SECRET_KEY = os.environ.get('CASHFREE_SECRET_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
CASHFREE_ENVIRONMENT = os.environ.get('CASHFREE_ENVIRONMENT', 'PRODUCTION')  # or 'SANDBOX'
X_API_VERSION = '2023-08-01'

# Initialize Cashfree
if CASHFREE_AVAILABLE:
    try:
        Cashfree.XClientId = CASHFREE_APP_ID
        Cashfree.XClientSecret = CASHFREE_SECRET_KEY

        if CASHFREE_ENVIRONMENT == 'PRODUCTION':
            Cashfree.XEnvironment = Cashfree.XProduction
        else:
            Cashfree.XEnvironment = Cashfree.XSandbox

        print(f"✅ Cashfree configured - Environment: {CASHFREE_ENVIRONMENT}")
    except Exception as e:
        print(f"❌ Cashfree configuration error: {e}")
        CASHFREE_AVAILABLE = False
else:
    print("⚠️ Cashfree features disabled")

class AdvancedPredictionEngine:
    def __init__(self):
        self.setup_prediction_templates()

    def setup_prediction_templates(self):
        """Setup Vedic astrology based prediction templates"""
        # These will be used as bases for personalized predictions
        self.zodiac_characteristics = {
            'Aries': {'element': 'Fire', 'ruler': 'Mars', 'traits': ['courageous', 'energetic', 'competitive']},
            'Taurus': {'element': 'Earth', 'ruler': 'Venus', 'traits': ['patient', 'reliable', 'devoted']},
            'Gemini': {'element': 'Air', 'ruler': 'Mercury', 'traits': ['adaptable', 'curious', 'communicative']},
            'Cancer': {'element': 'Water', 'ruler': 'Moon', 'traits': ['intuitive', 'emotional', 'protective']},
            'Leo': {'element': 'Fire', 'ruler': 'Sun', 'traits': ['confident', 'generous', 'creative']},
            'Virgo': {'element': 'Earth', 'ruler': 'Mercury', 'traits': ['analytical', 'practical', 'helpful']},
            'Libra': {'element': 'Air', 'ruler': 'Venus', 'traits': ['diplomatic', 'social', 'fair-minded']},
            'Scorpio': {'element': 'Water', 'ruler': 'Mars/Pluto', 'traits': ['passionate', 'determined', 'intense']},
            'Sagittarius': {'element': 'Fire', 'ruler': 'Jupiter', 'traits': ['optimistic', 'adventurous', 'philosophical']},
            'Capricorn': {'element': 'Earth', 'ruler': 'Saturn', 'traits': ['disciplined', 'responsible', 'ambitious']},
            'Aquarius': {'element': 'Air', 'ruler': 'Saturn/Uranus', 'traits': ['innovative', 'independent', 'humanitarian']},
            'Pisces': {'element': 'Water', 'ruler': 'Jupiter/Neptune', 'traits': ['compassionate', 'artistic', 'intuitive']}
        }

        self.nakshatra_influences = {
            'Ashwini': {'deity': 'Ashwini Kumaras', 'quality': 'quick and sharp'},
            'Bharani': {'deity': 'Yama', 'quality': 'transformative'},
            'Krittika': {'deity': 'Agni', 'quality': 'fiery and determined'},
            'Rohini': {'deity': 'Brahma', 'quality': 'creative and fertile'},
            'Mrigashira': {'deity': 'Soma', 'quality': 'explorative and curious'},
            'Ardra': {'deity': 'Rudra', 'quality': 'intense and transformative'},
            'Punarvasu': {'deity': 'Aditi', 'quality': 'renewing and abundant'},
            'Pushya': {'deity': 'Brihaspati', 'quality': 'nurturing and wise'},
            'Ashlesha': {'deity': 'Nagas', 'quality': 'mysterious and intuitive'},
            'Magha': {'deity': 'Pitris', 'quality': 'authoritative and traditional'},
            'Purva Phalguni': {'deity': 'Bhaga', 'quality': 'creative and luxurious'},
            'Uttara Phalguni': {'deity': 'Aryaman', 'quality': 'helpful and supportive'},
            'Hasta': {'deity': 'Savitar', 'quality': 'skillful and precise'},
            'Chitra': {'deity': 'Vishwakarma', 'quality': 'artistic and architectural'},
            'Swati': {'deity': 'Vayu', 'quality': 'independent and changeable'},
            'Vishakha': {'deity': 'Indra-Agni', 'quality': 'determined and goal-oriented'},
            'Anuradha': {'deity': 'Mitra', 'quality': 'friendly and collaborative'},
            'Jyeshtha': {'deity': 'Indra', 'quality': 'protective and authoritative'},
            'Mula': {'deity': 'Nirriti', 'quality': 'transformative and investigative'},
            'Purva Ashadha': {'deity': 'Apah', 'quality': 'influential and invincible'},
            'Uttara Ashadha': {'deity': 'Vishvedevas', 'quality': 'victorious and universal'},
            'Shravana': {'deity': 'Vishnu', 'quality': 'listening and learning'},
            'Dhanishta': {'deity': 'Vasus', 'quality': 'wealthy and musical'},
            'Shatabhisha': {'deity': 'Varuna', 'quality': 'healing and mysterious'},
            'Purva Bhadrapada': {'deity': 'Aja Ekapada', 'quality': 'fiery and transformative'},
            'Uttara Bhadrapada': {'deity': 'Ahirbudhnya', 'quality': 'calm and profound'},
            'Revati': {'deity': 'Pushan', 'quality': 'nurturing and abundant'}
        }

        self.sanskrit_slokas = [
            "वक्रतुण्ड महाकाय सूर्यकोटि समप्रभ। निर्विघ्नं कुरु मे देव सर्वकार्येषु सर्वदा॥",
            "गजाननं भूतगणादिसेवितं कपित्थजम्बूफलसारभक्षितम्। उमासुतं शोकविनाशकारकं नमामि विघ्नेश्वरपादपङ्कजम्॥",
            "एकदन्तं महाकायं लम्बोदरं गजाननम्। विघ्ननाशकरं देवं हेरम्बं प्रणमाम्यहम्॥",
            "सुमुखश्चैकदन्तश्च कपिलो गजकर्णकः। लम्बोदरश्च विकटो विघ्ननाशो विनायकः॥"
        ]

    def generate_personalized_overview(self, zodiac_sign, ascendant, nakshatra, birth_data):
        """Generate personalized yearly overview based on Vedic astrology"""
        zodiac_info = self.zodiac_characteristics.get(zodiac_sign, {})
        nakshatra_info = self.nakshatra_influences.get(nakshatra, {})

        # Parse birth date for numerology
        birth_date = birth_data['birth_date']
        day = int(birth_date[:2])
        month = int(birth_date[2:4])
        birth_number = (day % 9) or 9

        # Generate personalized overview
        overview_templates = [
            f"Based on your {zodiac_sign} Sun sign and {ascendant} Ascendant, 2025-2026 brings significant planetary shifts. ",
            f"Your {nakshatra} Nakshatra combined with {zodiac_sign} zodiac indicates a transformative period in 2025-2026. ",
            f"The alignment of planets for your {zodiac_sign} chart suggests 2025-2026 will be a year of growth and opportunities. "
        ]

        # Add specific influences based on zodiac element
        element_influences = {
            'Fire': "Mars and Jupiter's transit will energize your natural leadership qualities and bring new beginnings.",
            'Earth': "Saturn's steady influence will help you build solid foundations and achieve long-term goals.",
            'Air': "Mercury and Venus will enhance your communication skills and bring intellectual growth.",
            'Water': "The Moon's cycles will deepen your intuition and emotional connections throughout the year."
        }

        overview = overview_templates[birth_number % len(overview_templates)]
        overview += element_influences.get(zodiac_info.get('element', ''), "Planetary movements favor personal and professional development.")

        return overview

    def generate_monthly_predictions(self, birth_data):
        """Generate personalized monthly predictions based on birth data"""
        # Parse birth data
        birth_date = birth_data['birth_date']
        day = int(birth_date[:2])
        month = int(birth_date[2:4])
        zodiac_sign, _ = self.calculate_zodiac_sign(day, month)
        nakshatra = self.calculate_nakshatra(day)

        # Use birth data for consistent but personalized predictions
        name = birth_data['name']
        seed = sum(ord(char) for char in name) + day + month
        random.seed(seed)

        zodiac_info = self.zodiac_characteristics.get(zodiac_sign, {})
        nakshatra_info = self.nakshatra_influences.get(nakshatra, {})

        monthly_predictions = []
        current_date = datetime.now()

        for i in range(12):
            month_date = current_date + timedelta(days=30*i)
            month_name = month_date.strftime('%B %Y')

            # Generate personalized predictions based on zodiac and nakshatra
            career = self.generate_career_prediction(zodiac_sign, nakshatra, i, birth_data)
            finance = self.generate_finance_prediction(zodiac_sign, nakshatra, i, birth_data)
            relationships = self.generate_relationship_prediction(zodiac_sign, nakshatra, i, birth_data)
            health = self.generate_health_prediction(zodiac_sign, nakshatra, i, birth_data)

            monthly_predictions.append({
                'month': month_name,
                'career': career,
                'finance': finance,
                'relationships': relationships,
                'health': health,
                'auspicious_days': self.generate_auspicious_days(day, month, i),
                'special_notes': self.generate_special_notes(zodiac_sign, nakshatra, i)
            })

        random.seed()
        return monthly_predictions

    def generate_career_prediction(self, zodiac_sign, nakshatra, month_index, birth_data):
        """Generate personalized career predictions"""
        zodiac_info = self.zodiac_characteristics.get(zodiac_sign, {})
        ruler = zodiac_info.get('ruler', '')
        traits = zodiac_info.get('traits', [])

        career_templates = {
            'Fire': [
                f"Your natural {traits[0] if traits else 'leadership'} qualities will shine in professional settings. Excellent time for taking initiative and starting new projects.",
                f"{ruler}'s influence brings opportunities for advancement. Your competitive spirit will help you overcome challenges.",
                f"Creative projects and leadership roles favor you. Your energy and confidence will impress superiors."
            ],
            'Earth': [
                f"Systematic planning and patience will yield long-term career benefits. Your reliable nature will be recognized.",
                f"Practical skills and attention to detail will lead to success. {ruler}'s steady influence supports gradual growth.",
                f"Building solid foundations in your career. Your disciplined approach will bring stability and recognition."
            ],
            'Air': [
                f"Communication and networking will open new doors. Your {traits[1] if len(traits) > 1 else 'adaptable'} nature helps in changing environments.",
                f"Intellectual pursuits and learning new skills will benefit your career. {ruler} enhances your mental agility.",
                f"Collaboration and teamwork bring success. Your social skills will help build important professional relationships."
            ],
            'Water': [
                f"Your intuition will guide you in important career decisions. Emotional intelligence becomes your strength.",
                f"Creative and nurturing professions favor you. {ruler}'s influence deepens your understanding of people.",
                f"Trust your instincts in professional matters. Your protective nature will serve you well in leadership."
            ]
        }

        element = zodiac_info.get('element', 'Fire')
        templates = career_templates.get(element, career_templates['Fire'])
        return templates[month_index % len(templates)]

    def generate_finance_prediction(self, zodiac_sign, nakshatra, month_index, birth_data):
        """Generate personalized finance predictions"""
        zodiac_info = self.zodiac_characteristics.get(zodiac_sign, {})

        finance_templates = {
            'Fire': [
                "Investments in technology and innovation sectors show promise. Your bold approach to finances may bring unexpected gains.",
                "Income through leadership roles and entrepreneurial ventures. Avoid impulsive spending and focus on long-term wealth.",
                "Financial growth through taking calculated risks. Your natural confidence in money matters serves you well."
            ],
            'Earth': [
                "Stable financial growth through traditional investments. Real estate and long-term savings plans favor you.",
                "Systematic financial planning yields excellent results. Your practical approach to money management brings security.",
                "Patience in financial matters rewards you. Conservative investments and savings strategies work best."
            ],
            'Air': [
                "Multiple income sources through communication and networking. Intellectual property and digital ventures show promise.",
                "Financial gains through partnerships and collaborations. Your adaptability helps you seize new opportunities.",
                "Investment in education and skills development brings future financial benefits. Stay open to unconventional ideas."
            ],
            'Water': [
                "Intuitive financial decisions prove beneficial. Investments in healing arts and creative fields show potential.",
                "Emotional stability leads to better financial choices. Trust your instincts regarding money matters.",
                "Financial security through nurturing existing resources. Avoid emotional spending and focus on practical needs."
            ]
        }

        element = zodiac_info.get('element', 'Fire')
        templates = finance_templates.get(element, finance_templates['Fire'])
        return templates[month_index % len(templates)]

    def generate_relationship_prediction(self, zodiac_sign, nakshatra, month_index, birth_data):
        """Generate personalized relationship predictions"""
        zodiac_info = self.zodiac_characteristics.get(zodiac_sign, {})
        traits = zodiac_info.get('traits', [])

        relationship_templates = {
            'Fire': [
                f"Your {traits[0] if traits else 'passionate'} nature enhances romantic relationships. Social gatherings bring meaningful connections.",
                "Leadership in relationships works well. Your confidence attracts partners who appreciate strong personalities.",
                "Adventurous activities with loved ones strengthen bonds. Your energetic approach to relationships brings joy."
            ],
            'Earth': [
                "Stable and reliable relationships flourish. Your consistent nature builds trust and deep connections.",
                "Practical support and loyalty strengthen partnerships. Your devoted approach to relationships is appreciated.",
                "Building long-term foundations in relationships. Your patience helps resolve any conflicts peacefully."
            ],
            'Air': [
                "Intellectual connections and good communication enhance relationships. Your curious nature makes you interesting.",
                "Social networks and group activities bring new friendships. Your adaptability helps in various social situations.",
                "Meaningful conversations deepen existing relationships. Your diplomatic nature helps maintain harmony."
            ],
            'Water': [
                "Emotional depth and intuition strengthen bonds. Your compassionate nature nurtures relationships.",
                "Intimate connections and shared feelings bring closeness. Your protective instincts create safe spaces.",
                "Healing and supportive relationships flourish. Your intuitive understanding of others' needs is valuable."
            ]
        }

        element = zodiac_info.get('element', 'Fire')
        templates = relationship_templates.get(element, relationship_templates['Fire'])
        return templates[month_index % len(templates)]

    def generate_health_prediction(self, zodiac_sign, nakshatra, month_index, birth_data):
        """Generate personalized health predictions"""
        zodiac_info = self.zodiac_characteristics.get(zodiac_sign, {})

        health_templates = {
            'Fire': [
                "Focus on managing stress and anger. Regular exercise channels your abundant energy positively.",
                "Pay attention to headaches and inflammation. Cooling foods and relaxation techniques benefit you.",
                "High-energy activities maintain your vitality. Balance intense workouts with proper rest."
            ],
            'Earth': [
                "Digestive health needs attention. Regular meals and grounding exercises maintain your stability.",
                "Focus on joint and bone health. Weight-bearing exercises and calcium-rich foods are beneficial.",
                "Routine health checkups prevent issues. Your consistent nature helps maintain good health habits."
            ],
            'Air': [
                "Nervous system and respiratory health need care. Breathing exercises and mental relaxation help.",
                "Manage anxiety through mindfulness. Light exercises and social activities maintain your well-being.",
                "Balance mental stimulation with physical activity. Your adaptable nature helps you try various health routines."
            ],
            'Water': [
                "Emotional health impacts physical well-being. Water-based exercises and meditation are beneficial.",
                "Focus on lymphatic system and fluid balance. Hydration and emotional expression maintain health.",
                "Intuitive eating and listening to body signals work best. Your compassionate nature extends to self-care."
            ]
        }

        element = zodiac_info.get('element', 'Fire')
        templates = health_templates.get(element, health_templates['Fire'])
        return templates[month_index % len(templates)]

    def generate_personalized_remedies(self, zodiac_sign, nakshatra, birth_data):
        """Generate personalized Vedic remedies based on birth chart"""
        zodiac_info = self.zodiac_characteristics.get(zodiac_sign, {})
        nakshatra_info = self.nakshatra_influences.get(nakshatra, {})
        ruler = zodiac_info.get('ruler', '')

        # Base remedies based on zodiac ruler
        ruler_remedies = {
            'Sun': [
                "Offer water to Sun god every Sunday morning",
                "Chant Gayatri Mantra daily during sunrise",
                "Donate wheat or jaggery on Sundays"
            ],
            'Moon': [
                "Observe fast on Mondays or consume only milk",
                "Chant Chandra Mantra on Monday evenings",
                "Donate white clothes or rice on Mondays"
            ],
            'Mars': [
                "Chant Hanuman Chalisa on Tuesdays",
                "Donate red clothes or lentils on Tuesdays",
                "Fast on Tuesdays or avoid non-veg food"
            ],
            'Mercury': [
                "Chant Vishnu Sahasranama on Wednesdays",
                "Donate green clothes or moong dal",
                "Feed birds, especially on Wednesdays"
            ],
            'Jupiter': [
                "Chant Guru Mantra on Thursdays",
                "Donate yellow clothes, turmeric, or gram dal",
                "Help teachers and students"
            ],
            'Venus': [
                "Chant Shri Suktam or Lakshmi Mantra on Fridays",
                "Donate white clothes, rice, or silver",
                "Maintain harmony in relationships"
            ],
            'Saturn': [
                "Light sesame oil lamp under Peepal tree on Saturdays",
                "Donate black til, iron items, or oil",
                "Help elderly people and those in need"
            ]
        }

        # Get base remedies
        remedies = ruler_remedies.get(ruler.split('/')[0], ruler_remedies['Jupiter'])

        # Add nakshatra-specific remedies
        nakshatra_deity = nakshatra_info.get('deity', '')
        if nakshatra_deity:
            remedies.append(f"Offer prayers to {nakshatra_deity} during important decisions")

        # Add element-based remedies
        element = zodiac_info.get('element', '')
        if element == 'Fire':
            remedies.append("Practice Surya Namaskar daily")
        elif element == 'Water':
            remedies.append("Perform abhishekam to Shiva lingam with water")

        return remedies

    def generate_auspicious_days(self, birth_day, birth_month, month_index):
        """Generate personalized auspicious days"""
        base_days = [(birth_day + i) % 28 + 1 for i in range(3)]
        return f"{base_days[0]}, {base_days[1]}, {base_days[2]}"

    def generate_special_notes(self, zodiac_sign, nakshatra, month_index):
        """Generate personalized special notes"""
        zodiac_info = self.zodiac_characteristics.get(zodiac_sign, {})
        nakshatra_info = self.nakshatra_influences.get(nakshatra, {})

        notes = [
            f"Your {zodiac_sign} energy combined with {nakshatra} nakshatra brings unique opportunities this month.",
            f"The {nakshatra_info.get('quality', 'special')} quality of your nakshatra influences this period positively.",
            f"Planetary transits favor your {zodiac_info.get('element', '')} element characteristics this month."
        ]

        return notes[month_index % len(notes)]

    def calculate_zodiac_sign(self, day, month):
        """Calculate zodiac sign based on birth date"""
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return 'Aries', 'Mesha'
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return 'Taurus', 'Vrishabha'
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return 'Gemini', 'Mithuna'
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return 'Cancer', 'Karka'
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return 'Leo', 'Simha'
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return 'Virgo', 'Kanya'
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return 'Libra', 'Tula'
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return 'Scorpio', 'Vrishchika'
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return 'Sagittarius', 'Dhanu'
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return 'Capricorn', 'Makara'
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return 'Aquarius', 'Kumbha'
        else:
            return 'Pisces', 'Meena'

    def calculate_ascendant(self, hour):
        """Calculate ascendant based on birth time"""
        ascendant_map = {
            0: ('Aries', 'Mesha'), 2: ('Taurus', 'Vrishabha'), 4: ('Gemini', 'Mithuna'),
            6: ('Cancer', 'Karka'), 8: ('Leo', 'Simha'), 10: ('Virgo', 'Kanya'),
            12: ('Libra', 'Tula'), 14: ('Scorpio', 'Vrishchika'), 16: ('Sagittarius', 'Dhanu'),
            18: ('Capricorn', 'Makara'), 20: ('Aquarius', 'Kumbha'), 22: ('Pisces', 'Meena')
        }

        for time_key in sorted(ascendant_map.keys(), reverse=True):
            if hour >= time_key:
                return ascendant_map[time_key]
        return ('Aries', 'Mesha')

    def calculate_nakshatra(self, day):
        """Calculate nakshatra based on birth day"""
        nakshatras = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
                     'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
                     'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
                     'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
                     'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati']
        return nakshatras[(day - 1) % len(nakshatras)]

    def get_lucky_elements(self, day, month):
        """Calculate lucky elements based on birth date"""
        lucky_num = (day + month) % 9
        lucky_num = 9 if lucky_num == 0 else lucky_num

        lucky_numbers = {
            1: [1, 4, 7], 2: [2, 5, 8], 3: [3, 6, 9], 4: [1, 4, 7],
            5: [2, 5, 8], 6: [3, 6, 9], 7: [1, 4, 7], 8: [2, 5, 8],
            9: [3, 6, 9]
        }

        color_map = {
            1: 'Red', 2: 'Orange', 3: 'Yellow', 4: 'Green',
            5: 'Blue', 6: 'Indigo', 7: 'Violet', 8: 'Pink', 9: 'Gold'
        }

        day_map = {
            0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
            4: 'Friday', 5: 'Saturday', 6: 'Sunday'
        }

        return {
            'lucky_number': lucky_numbers.get(lucky_num, [lucky_num]),
            'lucky_color': color_map.get(lucky_num, 'Blue'),
            'lucky_day': day_map.get((day + month) % 7, 'Thursday')
        }

    def generate_predictions(self, birth_data):
        """Generate comprehensive predictions based on birth data"""
        # Parse birth date
        birth_date = birth_data['birth_date']
        day = int(birth_date[:2])
        month = int(birth_date[2:4])
        year = int(birth_date[4:8])

        # Parse birth time
        birth_time = birth_data['birth_time']
        hour = int(birth_time[:2]) if len(birth_time) >= 2 else 12

        # Calculate astrological elements
        zodiac_sign, zodiac_sanskrit = self.calculate_zodiac_sign(day, month)
        ascendant, ascendant_sanskrit = self.calculate_ascendant(hour)
        nakshatra = self.calculate_nakshatra(day)
        lucky_elements = self.get_lucky_elements(day, month)

        # Generate personalized predictions
        monthly_predictions = self.generate_monthly_predictions(birth_data)
        yearly_overview = self.generate_personalized_overview(zodiac_sign, ascendant, nakshatra, birth_data)
        personalized_remedies = self.generate_personalized_remedies(zodiac_sign, nakshatra, birth_data)

        # Select random Sanskrit sloka
        random_sloka = random.choice(self.sanskrit_slokas)

        return {
            'predictions': {
                'overview': yearly_overview,
                'monthly': monthly_predictions,
                'remedies': personalized_remedies
            },
            'chart_info': {
                'ascendant': ascendant,
                'ascendant_sanskrit': ascendant_sanskrit,
                'moon_sign': zodiac_sign,
                'moon_sign_sanskrit': zodiac_sanskrit,
                'sun_sign': zodiac_sign,
                'nakshatra': nakshatra,
                'zodiac_sign': zodiac_sign,
                'zodiac_sanskrit': zodiac_sanskrit
            },
            'lucky_elements': lucky_elements,
            'sanskrit_sloka': random_sloka
        }

# Initialize prediction engine
prediction_engine = AdvancedPredictionEngine()

def get_language_name(code):
    languages = {
        'en': 'English',
        'hi': 'Hindi',
        'bn': 'Bengali',
        'ta': 'Tamil',
        'te': 'Telugu',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'kn': 'Kannada'
    }
    return languages.get(code, 'English')

def get_gemstone_recommendation(zodiac_sign):
    gemstone_map = {
        'Aries': 'Red Coral (Moonga)',
        'Taurus': 'Diamond (Heera)',
        'Gemini': 'Emerald (Panna)',
        'Cancer': 'Pearl (Moti)',
        'Leo': 'Ruby (Manik)',
        'Virgo': 'Emerald (Panna)',
        'Libra': 'Diamond (Heera)',
        'Scorpio': 'Red Coral (Moonga)',
        'Sagittarius': 'Yellow Sapphire (Pukhraj)',
        'Capricorn': 'Blue Sapphire (Neelam)',
        'Aquarius': 'Blue Sapphire (Neelam)',
        'Pisces': 'Yellow Sapphire (Pukhraj)'
    }
    return gemstone_map.get(zodiac_sign, 'consult an astrologer')

def translate_text_simple(text, target_language):
    """
    Simple translation using a free API that works reliably
    """
    try:
        if target_language == 'en':
            return text

        # Map language codes
        lang_map = {
            'hi': 'hi',  # Hindi
            'bn': 'bn',  # Bengali
            'ta': 'ta',  # Tamil
            'te': 'te',  # Telugu
            'mr': 'mr',  # Marathi
            'gu': 'gu',  # Gujarati
            'kn': 'kn'   # Kannada
        }

        target_lang = lang_map.get(target_language, 'en')
        if target_lang == 'en':
            return text

        # Use a simple and reliable translation API
        # Option 1: MyMemory Translation API (free)
        try:
            url = f"https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': f'en|{target_lang}'
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                result = response.json()
                translated_text = result['responseData']['translatedText']
                print(f"✅ Translated: {text[:30]}... -> {translated_text[:30]}...")
                return translated_text
        except Exception as e:
            print(f"MyMemory API failed: {e}")

        # Option 2: LibreTranslate fallback
        try:
            url = "https://libretranslate.de/translate"
            payload = {
                'q': text,
                'source': 'en',
                'target': target_lang,
                'format': 'text'
            }
            headers = {'Content-Type': 'application/json'}

            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ LibreTranslate: {text[:30]}... -> {result['translatedText'][:30]}...")
                return result['translatedText']
        except Exception as e:
            print(f"LibreTranslate failed: {e}")

        # If all translation fails, return original text
        print(f"❌ Translation failed for {target_language}, using English")
        return text

    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_predictions_content(predictions_data, language):
    """
    Translate the actual prediction content
    """
    if language == 'en':
        return predictions_data

    try:
        print(f"🔄 Starting translation to {language}...")
        translated = predictions_data.copy()

        # Translate overview
        if 'overview' in translated:
            print("Translating overview...")
            translated['overview'] = translate_text_simple(translated['overview'], language)
            time.sleep(0.5)  # Rate limiting

        # Translate monthly predictions
        if 'monthly' in translated:
            print(f"Translating {len(translated['monthly'])} monthly predictions...")
            for i, month_pred in enumerate(translated['monthly']):
                print(f"  Month {i+1}...")
                for key in ['career', 'finance', 'relationships', 'health', 'special_notes']:
                    if key in month_pred and month_pred[key]:
                        month_pred[key] = translate_text_simple(month_pred[key], language)
                        time.sleep(0.3)  # Rate limiting

        # Translate remedies
        if 'remedies' in translated:
            print(f"Translating {len(translated['remedies'])} remedies...")
            translated_remedies = []
            for remedy in translated['remedies']:
                translated_remedies.append(translate_text_simple(remedy, language))
                time.sleep(0.2)
            translated['remedies'] = translated_remedies

        print("✅ Translation completed successfully!")
        return translated

    except Exception as e:
        print(f"❌ Translation failed: {e}")
        return predictions_data

def generate_pdf(html_content, output_path):
    """Generate PDF from HTML content using available PDF engine"""
    try:
        if PDF_ENGINE == 'weasyprint':
            HTML(string=html_content, base_url=__file__).write_pdf(output_path)
            return True
        elif PDF_ENGINE == 'pdfkit':
            pdfkit.from_string(html_content, output_path)
            return True
        elif PDF_ENGINE == 'xhtml2pdf':
            with open(output_path, 'wb') as f:
                pisa.CreatePDF(html_content, dest=f)
            return True
        else:
            print("❌ No PDF engine available")
            return False
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cashfree_available': CASHFREE_AVAILABLE,
        'pdf_engine': PDF_ENGINE
    })

@app.route('/api/generate-predictions', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_predictions():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        print(f"📥 Received prediction request: {data}")

        # Validate required fields
        required_fields = ['name', 'birth_date', 'birth_time', 'birth_place']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400

        # Validate birth date format (DDMMYYYY)
        birth_date = data['birth_date']
        if len(birth_date) != 8 or not birth_date.isdigit():
            return jsonify({
                'status': 'error',
                'message': 'Birth date must be in DDMMYYYY format'
            }), 400

        # Validate birth time format (HHMM)
        birth_time = data['birth_time']
        if len(birth_time) != 4 or not birth_time.isdigit():
            return jsonify({
                'status': 'error',
                'message': 'Birth time must be in HHMM format (24-hour)'
            }), 400

        # Get language preference
        language = data.get('language', 'en')
        print(f"🌐 Language preference: {language}")

        # Generate predictions
        predictions_data = prediction_engine.generate_predictions(data)

        # Translate content if needed
        if language != 'en':
            print(f"🔄 Translating predictions to {language}...")
            predictions_data['predictions'] = translate_predictions_content(
                predictions_data['predictions'], language
            )

        # Add gemstone recommendation
        zodiac_sign = predictions_data['chart_info']['zodiac_sign']
        gemstone = get_gemstone_recommendation(zodiac_sign)
        predictions_data['gemstone_recommendation'] = gemstone

        # Add language info
        predictions_data['language'] = language
        predictions_data['language_name'] = get_language_name(language)

        print(f"✅ Predictions generated successfully for {data['name']}")
        return jsonify({
            'status': 'success',
            'data': predictions_data
        })

    except Exception as e:
        print(f"❌ Prediction generation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate predictions: {str(e)}'
        }), 500

@app.route('/api/generate-pdf-report', methods=['POST'])
def generate_pdf_report():
    try:
        data = request.get_json()
        print(f"📥 Received PDF generation request for: {data.get('name', 'Unknown')}")

        # Validate required fields
        required_fields = ['name', 'birth_date', 'predictions']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            pdf_path = temp_file.name

        # Generate PDF
        html_content = create_pdf_html(data)
        success = generate_pdf(html_content, pdf_path)

        if not success:
            return jsonify({
                'status': 'error',
                'message': 'PDF generation failed - no PDF engine available'
            }), 500

        # Return PDF as base64
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')

        # Clean up
        os.unlink(pdf_path)

        print(f"✅ PDF report generated successfully for {data['name']}")
        return jsonify({
            'status': 'success',
            'pdf_data': pdf_data,
            'filename': f"ganesha_predictions_{data['name'].replace(' ', '_')}.pdf"
        })

    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate PDF: {str(e)}'
        }), 500

def create_pdf_html(data):
    """Create HTML content for PDF report"""
    name = data['name']
    predictions = data['predictions']
    chart_info = predictions.get('chart_info', {})
    lucky_elements = predictions.get('lucky_elements', {})

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Lord Ganesha Predictions for {name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }}
            .ganesha-img {{ width: 100px; height: auto; }}
            .section {{ margin: 30px 0; }}
            .section-title {{ background: #f0f0f0; padding: 10px; border-left: 4px solid #333; }}
            .month-prediction {{ margin: 15px 0; padding: 10px; border: 1px solid #ddd; }}
            .lucky-elements {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .lucky-item {{ text-align: center; padding: 10px; }}
            .footer {{ text-align: center; margin-top: 40px; font-style: italic; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🙏 Lord Ganesha Predictions 🙏</h1>
            <h2>for {name}</h2>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>

        <div class="section">
            <h3 class="section-title">Astrological Chart</h3>
            <p><strong>Zodiac Sign:</strong> {chart_info.get('zodiac_sign', 'N/A')} ({chart_info.get('zodiac_sanskrit', 'N/A')})</p>
            <p><strong>Ascendant:</strong> {chart_info.get('ascendant', 'N/A')} ({chart_info.get('ascendant_sanskrit', 'N/A')})</p>
            <p><strong>Nakshatra:</strong> {chart_info.get('nakshatra', 'N/A')}</p>
        </div>

        <div class="section">
            <h3 class="section-title">Yearly Overview</h3>
            <p>{predictions.get('overview', 'No overview available.')}</p>
        </div>

        <div class="section">
            <h3 class="section-title">Lucky Elements</h3>
            <div class="lucky-elements">
                <div class="lucky-item">
                    <strong>Lucky Numbers:</strong><br>
                    {', '.join(map(str, lucky_elements.get('lucky_number', [])))}
                </div>
                <div class="lucky-item">
                    <strong>Lucky Color:</strong><br>
                    {lucky_elements.get('lucky_color', 'N/A')}
                </div>
                <div class="lucky-item">
                    <strong>Lucky Day:</strong><br>
                    {lucky_elements.get('lucky_day', 'N/A')}
                </div>
            </div>
        </div>

        <div class="section">
            <h3 class="section-title">Monthly Predictions</h3>
    """

    # Add monthly predictions
    for month_pred in predictions.get('monthly', []):
        html += f"""
            <div class="month-prediction">
                <h4>{month_pred.get('month', 'Unknown Month')}</h4>
                <p><strong>Career:</strong> {month_pred.get('career', 'N/A')}</p>
                <p><strong>Finance:</strong> {month_pred.get('finance', 'N/A')}</p>
                <p><strong>Relationships:</strong> {month_pred.get('relationships', 'N/A')}</p>
                <p><strong>Health:</strong> {month_pred.get('health', 'N/A')}</p>
                <p><strong>Auspicious Days:</strong> {month_pred.get('auspicious_days', 'N/A')}</p>
                <p><em>{month_pred.get('special_notes', '')}</em></p>
            </div>
        """

    html += f"""
        </div>

        <div class="section">
            <h3 class="section-title">Personalized Remedies</h3>
            <ul>
    """

    # Add remedies
    for remedy in predictions.get('remedies', []):
        html += f"<li>{remedy}</li>"

    html += f"""
            </ul>
        </div>

        <div class="section">
            <h3 class="section-title">Sanskrit Blessing</h3>
            <p style="text-align: center; font-size: 16px; font-style: italic;">
                {predictions.get('sanskrit_sloka', '')}
            </p>
        </div>

        <div class="footer">
            <p>May Lord Ganesha remove all obstacles from your path and bless you with success and happiness.</p>
            <p>This prediction is generated based on Vedic astrology principles.</p>
        </div>
    </body>
    </html>
    """

    return html

@app.route('/api/create-payment-order', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_payment_order():
    if request.method == 'OPTIONS':
        return '', 200
    """Create Cashfree payment order"""
    try:
        if not CASHFREE_AVAILABLE:
            return jsonify({
                'status': 'error',
                'message': 'Payment service temporarily unavailable'
            }), 503

        data = request.get_json()
        print(f"💳 Creating payment order for: {data}")

        # Validate required fields
        required_fields = ['order_id', 'order_amount', 'customer_name', 'customer_email', 'customer_phone']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400

        # Create order request
        customer_details = CustomerDetails(
            customer_id=data.get('customer_id', 'customer_' + str(int(time.time()))),
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone']
        )

        order_meta = OrderMeta(
            return_url=data.get('return_url', 'https://your-app.railway.app/payment-success'),
            notify_url=data.get('notify_url', 'https://your-app.railway.app/api/payment-webhook')
        )

        order_request = CreateOrderRequest(
            order_id=data['order_id'],
            order_amount=data['order_amount'],
            order_currency='INR',
            customer_details=customer_details,
            order_meta=order_meta
        )

        # Create order
        api_instance = Cashfree.PGCreateOrderApi()
        api_response = api_instance.p_g_create_order(
            x_client_id=CASHFREE_APP_ID,
            x_client_secret=CASHFREE_SECRET_KEY,
            x_api_version=X_API_VERSION,
            create_order_request=order_request
        )

        print(f"✅ Payment order created: {api_response}")

        return jsonify({
            'status': 'success',
            'payment_session_id': api_response.payment_session_id,
            'order_id': api_response.order_id,
            'order_amount': api_response.order_amount
        })

    except Exception as e:
        print(f"❌ Payment order creation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to create payment order: {str(e)}'
        }), 500

@app.route('/api/payment-webhook', methods=['POST'])
def payment_webhook():
    """Handle Cashfree payment webhook"""
    try:
        data = request.get_json()
        print(f"🔄 Received payment webhook: {data}")

        # Verify signature (FIXED: removed self)
        signature = request.headers.get('x-webhook-signature')
        if not verify_webhook_signature(data, signature):
            print("❌ Invalid webhook signature")
            return jsonify({'status': 'error', 'message': 'Invalid signature'}), 401

        # Process webhook data
        order_id = data.get('orderId')
        order_status = data.get('orderStatus')

        print(f"💰 Payment update - Order: {order_id}, Status: {order_status}")

        # Here you would update your database with payment status
        # For now, just log it
        if order_status == 'PAID':
            print(f"✅ Payment successful for order: {order_id}")
        elif order_status in ['FAILED', 'CANCELLED']:
            print(f"❌ Payment failed for order: {order_id}")

        return jsonify({'status': 'success'})

    except Exception as e:
        print(f"❌ Webhook processing error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def verify_webhook_signature(data, signature):
    """Verify Cashfree webhook signature"""
    try:
        # Sort the data and create signature string
        sorted_data = dict(sorted(data.items()))
        signature_data = "".join([str(value) for value in sorted_data.values()])

        # Compute HMAC
        computed_signature = hmac.new(
            CASHFREE_SECRET_KEY.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return computed_signature == signature
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False

@app.route('/api/get-payment-status/<order_id>', methods=['POST', 'OPTIONS'])
@cross_origin()
def get_payment_status(order_id):
    if request.method == 'OPTIONS':
        return '', 200
    """Get payment status for an order"""
    try:
        if not CASHFREE_AVAILABLE:
            return jsonify({
                'status': 'error',
                'message': 'Payment service unavailable'
            }), 503

        api_instance = Cashfree.PGFetchOrderApi()
        api_response = api_instance.p_g_fetch_order(
            x_client_id=CASHFREE_APP_ID,
            x_client_secret=CASHFREE_SECRET_KEY,
            x_api_version=X_API_VERSION,
            order_id=order_id
        )

        return jsonify({
            'status': 'success',
            'order_status': api_response.order_status,
            'order_amount': api_response.order_amount,
            'payment_status': api_response.payment_status
        })

    except Exception as e:
        print(f"❌ Payment status check error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get payment status: {str(e)}'
        }), 500

# Railway.app specific configuration
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Lord Ganesha Astrology API on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"💰 Cashfree available: {CASHFREE_AVAILABLE}")
    print(f"📄 PDF engine: {PDF_ENGINE}")
    
    app.run(host='0.0.0.0', port=port, debug=False)