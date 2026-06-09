from flask import Flask, render_template_string, jsonify, request
import json

app = Flask(__name__)

# In-memory store: province name -> population count
populations = {}

# Thai province name translations
THAI_NAMES = {
    "Mae Hong Son": "แม่ฮ่องสอน",
    "Chumphon": "ชุมพร",
    "Nakhon Si Thammarat": "นครศรีธรรมราช",
    "Phuket": "ภูเก็ต",
    "Phangnga": "พังงา",
    "Ranong": "ระนอง",
    "Surat Thani": "สุราษฎร์ธานี",
    "Krabi": "กระบี่",
    "Phatthalung": "พัทลุง",
    "Satun": "สตูล",
    "Songkhla": "สงขลา",
    "Trang": "ตรัง",
    "Yala": "ยะลา",
    "Chiang Rai": "เชียงราย",
    "Chiang Mai": "เชียงใหม่",
    "Lampang": "ลำปาง",
    "Lamphun": "ลำพูน",
    "Nan": "น่าน",
    "Phayao": "พะเยา",
    "Phrae": "แพร่",
    "Phitsanulok": "พิษณุโลก",
    "Sukhothai": "สุโขทัย",
    "Uttaradit": "อุตรดิตถ์",
    "Kanchanaburi": "กาญจนบุรี",
    "Kamphaeng Phet": "กำแพงเพชร",
    "Phichit": "พิจิตร",
    "Phetchabun": "เพชรบูรณ์",
    "Suphan Buri": "สุพรรณบุรี",
    "Tak": "ตาก",
    "Uthai Thani": "อุทัยธานี",
    "Ang Thong": "อ่างทอง",
    "Chai Nat": "ชัยนาท",
    "Lop Buri": "ลพบุรี",
    "Nakhon Nayok": "นครนายก",
    "Prachin Buri": "ปราจีนบุรี",
    "Nakhon Sawan": "นครสวรรค์",
    "Phra Nakhon Si Ayutthaya": "พระนครศรีอยุธยา",
    "Pathum Thani": "ปทุมธานี",
    "Sing Buri": "สิงห์บุรี",
    "Saraburi": "สระบุรี",
    "Bangkok Metropolis": "กรุงเทพมหานคร",
    "Nonthaburi": "นนทบุรี",
    "Nakhon Pathom": "นครปฐม",
    "Phetchaburi": "เพชรบุรี",
    "Prachuap Khiri Khan": "ประจวบคีรีขันธ์",
    "Ratchaburi": "ราชบุรี",
    "Samut Prakan": "สมุทรปราการ",
    "Samut Sakhon": "สมุทรสาคร",
    "Samut Songkhram": "สมุทรสงคราม",
    "Si Sa Ket": "ศรีสะเกษ",
    "Ubon Ratchathani": "อุบลราชธานี",
    "Amnat Charoen": "อำนาจเจริญ",
    "Yasothon": "ยโสธร",
    "Chon Buri": "ชลบุรี",
    "Chachoengsao": "ฉะเชิงเทรา",
    "Chanthaburi": "จันทบุรี",
    "Sa Kaeo": "สระแก้ว",
    "Rayong": "ระยอง",
    "Trat": "ตราด",
    "Buri Ram": "บุรีรัมย์",
    "Chaiyaphum": "ชัยภูมิ",
    "Khon Kaen": "ขอนแก่น",
    "Kalasin": "กาฬสินธุ์",
    "Maha Sarakham": "มหาสารคาม",
    "Nakhon Ratchasima": "นครราชสีมา",
    "Roi Et": "ร้อยเอ็ด",
    "Surin": "สุรินทร์",
    "Loei": "เลย",
    "Nong Khai": "หนองคาย",
    "Sakon Nakhon": "สกลนคร",
    "Udon Thani": "อุดรธานี",
    "Nong Bua Lam Phu": "หนองบัวลำภู",
    "Nakhon Phanom": "นครพนม",
    "Mukdahan": "มุกดาหาร",
    "Narathiwat": "นราธิวาส",
    "Pattani": "ปัตตานี",
    "Bueng Kan": "บึงกาฬ",
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>🗺️ Thailand Live Population Map</title>
<link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css"/>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Sarabun', sans-serif;
    background: #0d1117;
    color: #e6edf3;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  header {
    background: linear-gradient(90deg, #161b22, #1f2937);
    border-bottom: 1px solid #30363d;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
    z-index: 1000;
  }
  header h1 {
    font-size: 1.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #58a6ff, #ff6b6b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .legend {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.75rem;
    color: #8b949e;
  }
  .legend-bar {
    width: 140px;
    height: 12px;
    border-radius: 6px;
    background: linear-gradient(90deg, #1565c0, #42a5f5, #fff9c4, #ef5350, #b71c1c);
    border: 1px solid #30363d;
  }
  .legend-labels {
    display: flex;
    justify-content: space-between;
    width: 140px;
    font-size: 0.65rem;
    color: #8b949e;
    margin-top: 2px;
  }
  .main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }
  #map {
    flex: 1;
    background: #0d1117;
  }
  .panel {
    width: 320px;
    background: #161b22;
    border-left: 1px solid #30363d;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    flex-shrink: 0;
  }
  .panel-header {
    padding: 16px;
    border-bottom: 1px solid #30363d;
    font-size: 0.85rem;
    font-weight: 600;
    color: #58a6ff;
    background: #1f2937;
  }
  .add-section {
    padding: 16px;
    border-bottom: 1px solid #30363d;
    background: #161b22;
  }
  .add-section label {
    display: block;
    font-size: 0.75rem;
    color: #8b949e;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .add-section select, .add-section input[type="number"] {
    width: 100%;
    padding: 8px 12px;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    font-family: 'Sarabun', sans-serif;
    font-size: 0.85rem;
    margin-bottom: 10px;
    outline: none;
    transition: border-color 0.2s;
  }
  .add-section select:focus, .add-section input[type="number"]:focus {
    border-color: #58a6ff;
  }
  .btn-group { display: flex; gap: 8px; }
  .btn {
    flex: 1;
    padding: 8px;
    border: none;
    border-radius: 6px;
    font-family: 'Sarabun', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  .btn-add { background: #1f6feb; color: #fff; }
  .btn-add:hover { background: #388bfd; transform: translateY(-1px); }
  .btn-remove { background: #21262d; color: #f85149; border: 1px solid #f85149; }
  .btn-remove:hover { background: #2d1f1f; }
  .btn-reset { background: #21262d; color: #8b949e; border: 1px solid #30363d; }
  .btn-reset:hover { background: #30363d; color: #e6edf3; }
  .province-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }
  .province-list::-webkit-scrollbar { width: 6px; }
  .province-list::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
  .province-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 10px;
    border-radius: 6px;
    margin-bottom: 3px;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.15s;
    font-size: 0.8rem;
  }
  .province-item:hover { background: #21262d; border-color: #30363d; }
  .province-item.active { background: #1f2937; border-color: #58a6ff; }
  .prov-name { font-weight: 600; color: #e6edf3; }
  .prov-thai { font-size: 0.72rem; color: #8b949e; }
  .prov-count {
    font-size: 0.78rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 10px;
    min-width: 40px;
    text-align: center;
  }
  .count-zero { background: #1a2332; color: #58a6ff; }
  .count-low { background: #1a2d3a; color: #4fc3f7; }
  .count-mid { background: #2d2a1e; color: #ffd54f; }
  .count-high { background: #2d1f1f; color: #ff6b6b; }
  .count-max { background: #3d0f0f; color: #ff1744; }
  .tooltip-custom {
    background: rgba(13, 17, 23, 0.95) !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    padding: 8px 12px !important;
    font-family: 'Sarabun', sans-serif !important;
    font-size: 0.82rem !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5) !important;
  }
  .stats-bar {
    padding: 10px 16px;
    border-top: 1px solid #30363d;
    background: #161b22;
    font-size: 0.72rem;
    color: #8b949e;
    display: flex;
    gap: 16px;
  }
  .stat { display: flex; flex-direction: column; }
  .stat-val { font-size: 1rem; font-weight: 700; color: #e6edf3; }
  .search-box {
    padding: 10px 16px;
    border-bottom: 1px solid #30363d;
  }
  .search-box input {
    width: 100%;
    padding: 7px 12px;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    font-family: 'Sarabun', sans-serif;
    font-size: 0.82rem;
    outline: none;
  }
  .search-box input:focus { border-color: #58a6ff; }
  .search-box input::placeholder { color: #484f58; }
  .leaflet-container { background: #0d1117 !important; }
</style>
</head>
<body>
<header>
  <h1>🗺️ Thailand Live Population Heatmap</h1>
  <div>
    <div class="legend">
      <span>Empty</span>
      <div>
        <div class="legend-bar"></div>
        <div class="legend-labels"><span>0</span><span>Low</span><span>Mid</span><span>High</span><span>Max</span></div>
      </div>
      <span>Crowded</span>
    </div>
  </div>
</header>
<div class="main">
  <div id="map"></div>
  <div class="panel">
    <div class="panel-header">📊 Population Control Panel</div>
    <div class="add-section">
      <label>Select Province / จังหวัด</label>
      <select id="province-select">
        <option value="">-- Choose Province --</option>
      </select>
      <label>People to Add / Remove</label>
      <input type="number" id="people-count" value="100" min="1" max="100000" step="50"/>
      <div class="btn-group">
        <button class="btn btn-add" onclick="modifyPop(1)">➕ Add People</button>
        <button class="btn btn-remove" onclick="modifyPop(-1)">➖ Remove</button>
      </div>
      <div style="margin-top:8px;">
        <button class="btn btn-reset" style="width:100%" onclick="resetProv()">🔄 Reset Province</button>
      </div>
    </div>
    <div class="search-box">
      <input type="text" id="search" placeholder="🔍 Search province..." oninput="filterList()"/>
    </div>
    <div class="province-list" id="province-list"></div>
    <div class="stats-bar">
      <div class="stat"><span class="stat-val" id="total-pop">0</span><span>Total People</span></div>
      <div class="stat"><span class="stat-val" id="occupied-provs">0</span><span>Occupied Provinces</span></div>
      <div class="stat"><span class="stat-val" id="max-prov">—</span><span>Most Crowded</span></div>
    </div>
  </div>
</div>

<script>
const GEOJSON_URL = 'https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json';

const THAI_NAMES = {{ thai_names | safe }};

let map, geojsonLayer, populations = {}, allProvinces = [], selectedProvince = null;
let geoData = null;
let layerMap = {}; // province name -> leaflet layer

function getColor(pop) {
  if (pop === 0) return { fill: '#1565c0', opacity: 0.15 };
  if (pop < 100) return { fill: '#1976d2', opacity: 0.35 };
  if (pop < 500) return { fill: '#42a5f5', opacity: 0.5 };
  if (pop < 1000) return { fill: '#80deea', opacity: 0.55 };
  if (pop < 2000) return { fill: '#fff9c4', opacity: 0.6 };
  if (pop < 5000) return { fill: '#ffcc02', opacity: 0.65 };
  if (pop < 10000) return { fill: '#ff9800', opacity: 0.7 };
  if (pop < 20000) return { fill: '#ef5350', opacity: 0.75 };
  if (pop < 50000) return { fill: '#e53935', opacity: 0.82 };
  return { fill: '#b71c1c', opacity: 0.92 };
}

function styleFeature(feature) {
  const name = feature.properties.name;
  const pop = populations[name] || 0;
  const c = getColor(pop);
  return {
    fillColor: c.fill,
    fillOpacity: c.opacity,
    color: '#58a6ff',
    weight: 1.2,
    opacity: 0.8
  };
}

function highlightFeature(e) {
  const layer = e.target;
  layer.setStyle({ weight: 2.5, color: '#ffffff', opacity: 1 });
  layer.bringToFront();
}

function resetHighlight(e) {
  geojsonLayer.resetStyle(e.target);
}

function onEachFeature(feature, layer) {
  const name = feature.properties.name;
  layerMap[name] = layer;

  layer.on({
    mouseover: function(e) {
      highlightFeature(e);
      const pop = populations[name] || 0;
      const thai = THAI_NAMES[name] || name;
      layer.bindTooltip(
        `<strong>${name}</strong><br/>${thai}<br/>👥 ${pop.toLocaleString()} people`,
        { className: 'tooltip-custom', sticky: true, direction: 'top' }
      ).openTooltip(e.latlng);
    },
    mouseout: function(e) {
      resetHighlight(e);
      layer.closeTooltip();
    },
    click: function() {
      selectProvince(name);
    }
  });
}

function initMap() {
  map = L.map('map', {
    center: [13.0, 101.5],
    zoom: 6,
    zoomControl: true,
    attributionControl: false
  });

  // Dark tile layer
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
    maxZoom: 19
  }).addTo(map);

  fetch(GEOJSON_URL)
    .then(r => r.json())
    .then(data => {
      geoData = data;
      allProvinces = data.features.map(f => f.properties.name).sort();
      allProvinces.forEach(n => { populations[n] = 0; });

      geojsonLayer = L.geoJSON(data, {
        style: styleFeature,
        onEachFeature: onEachFeature
      }).addTo(map);

      map.fitBounds(geojsonLayer.getBounds(), { padding: [10, 10] });

      populateSelect();
      renderList();
    });
}

function populateSelect() {
  const sel = document.getElementById('province-select');
  sel.innerHTML = '<option value="">-- Choose Province --</option>';
  allProvinces.forEach(name => {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = `${name} (${THAI_NAMES[name] || ''})`;
    sel.appendChild(opt);
  });
}

function selectProvince(name) {
  selectedProvince = name;
  document.getElementById('province-select').value = name;

  // Highlight in list
  document.querySelectorAll('.province-item').forEach(el => {
    el.classList.toggle('active', el.dataset.name === name);
  });

  // Zoom to province
  if (layerMap[name]) {
    const bounds = layerMap[name].getBounds();
    map.flyToBounds(bounds, { padding: [40, 40], duration: 0.8 });
  }
}

function modifyPop(sign) {
  const sel = document.getElementById('province-select').value;
  if (!sel) { alert('Please select a province first!'); return; }
  const count = parseInt(document.getElementById('people-count').value) || 100;
  const current = populations[sel] || 0;
  populations[sel] = Math.max(0, current + sign * count);

  refreshLayer(sel);
  renderList();
  updateStats();
}

function resetProv() {
  const sel = document.getElementById('province-select').value;
  if (!sel) return;
  populations[sel] = 0;
  refreshLayer(sel);
  renderList();
  updateStats();
}

function refreshLayer(name) {
  if (!geojsonLayer || !geoData) return;
  geojsonLayer.eachLayer(layer => {
    if (layer.feature && layer.feature.properties.name === name) {
      const pop = populations[name] || 0;
      const c = getColor(pop);
      layer.setStyle({
        fillColor: c.fill,
        fillOpacity: c.opacity,
        color: '#58a6ff',
        weight: 1.2,
        opacity: 0.8
      });
    }
  });
}

function getCountClass(pop) {
  if (pop === 0) return 'count-zero';
  if (pop < 500) return 'count-low';
  if (pop < 5000) return 'count-mid';
  if (pop < 20000) return 'count-high';
  return 'count-max';
}

function renderList(filter = '') {
  const list = document.getElementById('province-list');
  const f = filter.toLowerCase();
  const sorted = [...allProvinces].sort((a, b) => (populations[b] || 0) - (populations[a] || 0));

  list.innerHTML = sorted
    .filter(name => !f || name.toLowerCase().includes(f) || (THAI_NAMES[name]||'').includes(f))
    .map(name => {
      const pop = populations[name] || 0;
      const thai = THAI_NAMES[name] || '';
      const cls = getCountClass(pop);
      const active = selectedProvince === name ? 'active' : '';
      return `<div class="province-item ${active}" data-name="${name}" onclick="selectProvince('${name}')">
        <div>
          <div class="prov-name">${name}</div>
          <div class="prov-thai">${thai}</div>
        </div>
        <span class="prov-count ${cls}">${pop >= 1000 ? (pop/1000).toFixed(1)+'k' : pop}</span>
      </div>`;
    }).join('');
}

function filterList() {
  renderList(document.getElementById('search').value);
}

function updateStats() {
  const vals = Object.values(populations);
  const total = vals.reduce((a, b) => a + b, 0);
  const occupied = vals.filter(v => v > 0).length;
  const maxEntry = Object.entries(populations).sort((a, b) => b[1] - a[1])[0];

  document.getElementById('total-pop').textContent = total.toLocaleString();
  document.getElementById('occupied-provs').textContent = occupied;
  document.getElementById('max-prov').textContent = maxEntry && maxEntry[1] > 0
    ? maxEntry[0].split(' ').slice(-1)[0]
    : '—';
}

// Sync select → selectedProvince
document.getElementById('province-select').addEventListener('change', function() {
  if (this.value) selectProvince(this.value);
});

initMap();
setInterval(() => { renderList(document.getElementById('search').value); updateStats(); }, 2000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    thai_names_json = json.dumps(THAI_NAMES, ensure_ascii=False)
    return render_template_string(HTML_TEMPLATE, thai_names=thai_names_json)

@app.route('/api/populations', methods=['GET'])
def get_populations():
    return jsonify(populations)

@app.route('/api/populations', methods=['POST'])
def set_populations():
    data = request.json
    province = data.get('province')
    count = data.get('count', 0)
    if province:
        populations[province] = max(0, count)
    return jsonify({'ok': True, 'province': province, 'count': populations.get(province, 0)})

if __name__ == '__main__':
    print("\n🗺️  Thailand Population Map is running!")
    print("👉  Open: http://localhost:5000\n")
    app.run(debug=True, port=5000)
