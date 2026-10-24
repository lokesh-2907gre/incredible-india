from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import urllib.request
import urllib.parse
import json
import re
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# TiDB Cloud MySQL Connection
DB_HOST = os.environ.get('DB_HOST', 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com')
DB_PORT = int(os.environ.get('DB_PORT', 4000))
DB_USER = os.environ.get('DB_USER', '32Dy7US6LhUVFag.root')
DB_PASS = os.environ.get('DB_PASS', '74OaLE6s5DRpimPC')
DB_NAME = os.environ.get('DB_NAME', 'test')

INDIAN_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 
    'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 
    'Delhi', 'Jammu & Kashmir', 'Ladakh', 'Chandigarh', 'Puducherry', 'Andaman and Nicobar'
]

MUST_VISIT_PRESETS = {
    'Agra': 'Taj Mahal (Sunrise vantage) | Agra Fort & Royal Palaces | Mehtab Bagh Sunset Gardens',
    'Varanasi': 'Kashi Vishwanath Corridor | Dashashwamedh Ghat Evening Aarti | Sarnath Deer Park & Stupa',
    'Delhi': 'Qutub Minar UNESCO Complex | Humayun’s Tomb Gardens | Red Fort & Chandni Chowk',
    'Jaipur': 'Amber Palace & Maota Lake | Hawa Mahal & City Palace | Nahargarh Fort Sunset Viewpoint',
    'Udaipur': 'City Palace & Lake Pichola | Jag Mandir Island Sanctuary | Saheliyon Ki Bari & Monsoon Palace',
    'Jodhpur': 'Mehrangarh Fort & Citadel | Jaswant Thada White Marble Cenotaph | Umaid Bhawan Palace & Museum',
    'Amritsar': 'Sri Harmandir Sahib (Golden Temple) | Jallianwala Bagh Historic Memorial | Wagah Border Retreat Ceremony',
    'Srinagar': 'Dal Lake Shikara & Floating Market | Mughal Gardens (Nishat & Shalimar) | Shankaracharya Hilltop Temple',
    'Leh': 'Pangong Tso High-Altitude Lake | Thiksey Monastery | Khardung La Pass (17,582 ft)',
    'Rishikesh': 'Triveni Ghat Ganga Aarti | Laxman & Ram Suspension Bridges | Beatles Ashram (Chaurasi Kutia)',
    'Mumbai': 'Gateway of India & Colaba | Marine Drive (Queen’s Necklace) | Elephanta Island Basalt Caves',
    'Aurangabad': 'Ajanta Buddhist Rock Caves | Ellora Kailasa Monolithic Temple | Bibi Ka Maqbara',
    'Khajuraho': 'Kandariya Mahadeva Temple | Western Group Sculpted Temples | Raneh Falls Granite Canyon',
    'Bhopal': 'Sanchi Great Stupa Complex | Bhimbetka 30,000-Yr Rock Shelters | Upper Lake (Bhojtal) & Van Vihar',
    'Goa': 'Basilica of Bom Jesus & Old Goa | Dudhsagar Four-Tier Waterfalls | Chapora Fort & Vagator Coast',
    'Hampi': 'Virupaksha Temple & Ancient Bazaar | Vijaya Vittala Stone Chariot | Matanga Hill Sunrise Ridge',
    'Mysuru': 'Mysore Palace Illumination | Chamundi Hills & Nandi Bull | Brindavan Gardens & Musical Fountains',
    'Bengaluru': 'Bangalore Palace & Royal Grounds | Lalbagh Botanical Glass House | Tipu Sultan’s Summer Palace',
    'Hyderabad': 'Charminar & Laad Bazaar | Golconda Fort Acoustic Citadel | Salar Jung Historic Museum',
    'Chennai': 'Kapaleeshwarar Temple | Marina Beach Coastline | San Thome Cathedral Basilica',
    'Madurai': 'Meenakshi Amman Temple Complex | Thirumalai Nayakkar Mahal | Gandhi Memorial Heritage Museum',
    'Kochi': 'Fort Kochi & Chinese Fishing Nets | Mattancherry Dutch Palace | Jew Town & Paradesi Synagogue',
    'Alleppey': 'Vembanad Lake Houseboat Cruise | Marari Secluded Palm Beach | Alappuzha Historic Lighthouse',
    'Kolkata': 'Victoria Memorial & Maidan | Howrah Bridge & Riverfront Market | Dakshineswar Kali Temple',
    'Puri': 'Shree Jagannath Temple | Konark Sun Temple (Black Pagoda) | Raghurajpur Artisan Village',
    'Shillong': 'Umiam Lake Serene Viewpoint | Elephant Falls & Shillong Peak | Laitlum Canyons Ridge Trail',
    'Kaziranga': 'Central Range One-Horned Rhino Safari | Kaziranga Orchid National Park | Kakochang Waterfalls',
    'Manali': 'Solang Valley & Atal Tunnel | Hadimba Temple & Cedar Groves | Jogini Waterfalls & Old Manali',
    'Kodagu district': 'Abbey Waterfalls & Coffee Trail | Raja’s Seat Panoramic Sunset | Namdroling Golden Monastery',
    'Ooty': 'Nilgiri Mountain Toy Train | Doddabetta Peak Viewpoint | Pykara Lake & Cascades',
    'Mathura': 'Shri Krishna Janmabhoomi Complex | Vishram Ghat Yamuna Aarti | Dwarkadhish Ancient Temple',
    'Kohima': 'Kohima War Cemetery & Memorial | Kisama Heritage Village | Dzukou Valley Flower Sanctuary',
    'Vaishno Devi Temple': 'Holy Bhawan Cave Shrine | Bhairon Temple Scenic Ropeway | Ardhkuwari Cave (Garbhjun)',
    'Vrindavan': 'Banke Bihari Temple | Prem Mandir Grand Illumination | ISKCON Krishna Balaram Temple',
    'Guwahati': 'Kamakhya Devi Hilltop Temple | Umananda Peacock Island | Brahmaputra River Sunset Cruise',
    'Hanle': 'Hanle Indian Astronomical Observatory | Dark Sky Reserve Stargazing | 17th-Century Hanle Monastery',
    'Kargil': 'Dras Kargil War Memorial | Suru Valley & Nun-Kun View | Hunderman Broq Century-Old Village',
    'Kargi': 'Dras Kargil War Memorial | Suru Valley & Nun-Kun View | Hunderman Broq Century-Old Village'
}

def get_db():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/cities', methods=['GET'])
def get_cities():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                id,
                city, 
                state, 
                monument, 
                image_url AS image, 
                hidden_spot AS hiddenSpot,
                best_time AS bestTime,
                timings_entry AS timingsEntry,
                how_to_reach AS howToReach,
                pro_tip AS proTip,
                must_visit AS mustVisit,
                category
            FROM destinations
            ORDER BY id ASC
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/discover', methods=['POST', 'GET'])
def discover_location():
    data = request.get_json(silent=True) or {}
    raw_query = ''
    if isinstance(data, dict):
        raw_query = data.get('query', '')
    if not raw_query:
        raw_query = request.form.get('query') or request.args.get('query') or ''
    raw_query = raw_query.strip()
    
    if not raw_query:
        return jsonify({"error": "Location query is required"}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # 1. Check if already in MySQL
    cursor.execute("""
        SELECT 
            id, city, state, monument, 
            image_url AS image, hidden_spot AS hiddenSpot,
            best_time AS bestTime, timings_entry AS timingsEntry,
            how_to_reach AS howToReach, pro_tip AS proTip,
            must_visit AS mustVisit, category
        FROM destinations
        WHERE LOWER(city) = %s OR LOWER(city) LIKE %s OR LOWER(monument) LIKE %s
        LIMIT 1
    """, (raw_query.lower(), f"%{raw_query.lower()}%", f"%{raw_query.lower()}%"))
    
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        conn.close()
        return jsonify({"destination": existing, "from_db": True})

    # 2. Live Discovery across India via Wikipedia & Open Data
    try:
        search_query = urllib.parse.quote(raw_query)
        opensearch_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={search_query}&limit=1&namespace=0&format=json"
        req = urllib.request.Request(opensearch_url, headers={'User-Agent': 'IncredibleIndiaApp/1.0'})
        with urllib.request.urlopen(req, timeout=6) as res:
            search_res = json.loads(res.read().decode('utf-8'))
        
        target_title = raw_query.title()
        if search_res and len(search_res) > 1 and len(search_res[1]) > 0:
            target_title = search_res[1][0]
        
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(target_title)}"
        req2 = urllib.request.Request(summary_url, headers={'User-Agent': 'IncredibleIndiaApp/1.0'})
        with urllib.request.urlopen(req2, timeout=6) as res2:
            wiki_data = json.loads(res2.read().decode('utf-8'))

        city_name = wiki_data.get('title', target_title)
        clean_city = re.sub(r'\(.*?\)', '', city_name).split(',')[0].strip()

        extract = wiki_data.get('extract', f"Explore the peaceful trails, ancient culture and timeless beauty of {clean_city}.")
        detected_state = next((s for s in INDIAN_STATES if s.lower() in extract.lower()), 'India')

        # High-res photo
        img_url = wiki_data.get('originalimage', {}).get('source')
        if not img_url:
            img_url = wiki_data.get('thumbnail', {}).get('source')
        if not img_url:
            img_url = "https://images.unsplash.com/photo-1506461883276-594a12b11cf3?auto=format&fit=crop&w=1000&q=80"

        monument = f"Historic Trails & Landmarks of {clean_city}"
        hidden_spot = f"Secret paths of {clean_city}: {extract[:240]}..." if len(extract) > 240 else extract

        best_time = "October to March"
        timings_entry = "Open Daily · Free Exploration"
        how_to_reach = f"Connected via nearest highway & railway to {clean_city}, {detected_state}"
        pro_tip = f"Explore the dawn trails and historical routes around {clean_city}."
        category = "Offbeat"

        must_visit = MUST_VISIT_PRESETS.get(clean_city)
        if not must_visit:
            must_visit = f"Historic Old Quarter & Fort of {clean_city} | Scenic Mountain & Valley Viewpoint | Ancient Temple & Heritage Bazaar of {clean_city}"

        cursor.execute("""
            INSERT INTO destinations (
                city, state, monument, image_url, hidden_spot,
                best_time, timings_entry, how_to_reach, pro_tip, must_visit, category
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (clean_city, detected_state, monument, img_url, hidden_spot, best_time, timings_entry, how_to_reach, pro_tip, must_visit, category))
        
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        new_dest = {
            "id": new_id,
            "city": clean_city,
            "state": detected_state,
            "monument": monument,
            "image": img_url,
            "hiddenSpot": hidden_spot,
            "bestTime": best_time,
            "timingsEntry": timings_entry,
            "howToReach": how_to_reach,
            "proTip": pro_tip,
            "mustVisit": must_visit,
            "category": category
        }
        return jsonify({"destination": new_dest, "from_db": False})

    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"error": f"Could not discover '{raw_query}': {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🌍 Website live on port {port}")
    app.run(host='0.0.0.0', debug=True, port=port)
