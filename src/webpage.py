def webpage(): #DON'T FORGET TO UPLOAD THIS FILE TO THE FLASH MEMORY OF THE DEVICE
    return """
    <!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FloraCare</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

  :root {
    --green-bright: #1b663e;
    --green-mid: #185a37;
    --green-dark: #0f3923;
    --green-deeper: #092215;
    --green-abyss: #030b07;
    --bg: #080f0a;
    --surface: #0d1a10;
    --surface2: #111f14;
    --border: #1b663e55;
    --text-primary: #4dff8a;
    --text-dim: #2a9950;
    --text-muted: #1b663e;
    --glow: 0 0 12px #1b663e88, 0 0 30px #1b663e33;
    --glow-strong: 0 0 8px #4dff8a88, 0 0 20px #1b663e99;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text-primary);
    font-family: 'Share Tech Mono', monospace;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 16px 40px;
    position: relative;
    overflow-x: hidden;
  }

  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
      repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(27,102,62,0.03) 2px, rgba(27,102,62,0.03) 4px);
    pointer-events: none;
    z-index: 0;
  }

  body::after {
    content: '';
    position: fixed;
    top: -40%;
    left: -20%;
    width: 140%;
    height: 80%;
    background: radial-gradient(ellipse at center, rgba(27,102,62,0.07) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
  }

  .wrap {
    width: 100%;
    max-width: 480px;
    position: relative;
    z-index: 1;
  }

  /* ── HEADER ── */
  header {
    text-align: center;
    margin-bottom: 28px;
    padding-top: 8px;
  }

  .logo {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: clamp(28px, 8vw, 42px);
    letter-spacing: 0.08em;
    color: var(--text-primary);
    text-shadow: var(--glow-strong);
    animation: flicker 6s infinite;
  }

  .logo span {
    color: var(--text-dim);
  }

  .logo-sub {
    font-size: 11px;
    letter-spacing: 0.3em;
    color: var(--text-muted);
    margin-top: 4px;
    text-transform: uppercase;
  }

  @keyframes flicker {
    0%,100% { opacity: 1; }
    92% { opacity: 1; }
    93% { opacity: 0.85; }
    94% { opacity: 1; }
    96% { opacity: 0.9; }
    97% { opacity: 1; }
  }

  /* ── PLANT DISPLAY ── */
  .plant-display {
    background: #000;
    border: 1px solid var(--green-bright);
    border-radius: 20px;
    padding: 20px 24px;
    margin-bottom: 28px;
    box-shadow: var(--glow), inset 0 0 40px rgba(0,0,0,0.8);
    position: relative;
    overflow: hidden;
    min-height: 140px;
  }

  .plant-display::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(27,102,62,0.08) 0%, transparent 50%);
    pointer-events: none;
  }

  .plant-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
    text-shadow: var(--glow-strong);
    margin-bottom: 14px;
    letter-spacing: 0.1em;
  }

  .sensor-line {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }

  .sensor-label {
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 0.15em;
    width: 60px;
    flex-shrink: 0;
  }

  .sensor-bar-wrap {
    flex: 1;
    height: 4px;
    background: rgba(27,102,62,0.15);
    border-radius: 2px;
    overflow: hidden;
    position: relative;
  }

  .sensor-bar {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--green-mid), var(--text-primary));
    box-shadow: 0 0 8px var(--green-bright);
    transition: width 1s ease;
    animation: barPulse 3s ease-in-out infinite;
  }

  @keyframes barPulse {
    0%,100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  .sensor-val {
    font-size: 11px;
    color: var(--text-dim);
    width: 36px;
    text-align: right;
    flex-shrink: 0;
  }

  .corner-decor {
    position: absolute;
    width: 16px;
    height: 16px;
    border-color: var(--green-bright);
    border-style: solid;
    opacity: 0.5;
  }
  .corner-decor.tl { top: 8px; left: 8px; border-width: 1px 0 0 1px; }
  .corner-decor.tr { top: 8px; right: 8px; border-width: 1px 1px 0 0; }
  .corner-decor.bl { bottom: 8px; left: 8px; border-width: 0 0 1px 1px; }
  .corner-decor.br { bottom: 8px; right: 8px; border-width: 0 1px 1px 0; }

  /* ── SECTION TITLE ── */
  .section-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.25em;
    color: var(--text-primary);
    text-shadow: var(--glow);
    text-align: center;
    margin-bottom: 20px;
    text-transform: uppercase;
    position: relative;
  }

  .section-title::before,
  .section-title::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 25%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--green-bright));
  }
  .section-title::before { left: 0; }
  .section-title::after { right: 0; background: linear-gradient(90deg, var(--green-bright), transparent); }

  /* ── FORM ROWS ── */
  .form-row {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 16px;
  }

  label {
    font-size: 11px;
    letter-spacing: 0.15em;
    color: var(--text-dim);
    white-space: nowrap;
    width: 120px;
    flex-shrink: 0;
  }

  select {
    flex: 1;
    background: var(--surface);
    border: 1px solid var(--green-mid);
    border-radius: 8px;
    color: var(--text-primary);
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    padding: 10px 14px;
    cursor: pointer;
    appearance: none;
    -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%231b663e' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  select:focus {
    outline: none;
    border-color: var(--text-primary);
    box-shadow: var(--glow);
  }

  select option {
    background: var(--bg);
    color: var(--text-primary);
  }

  /* ── PLANT CARDS ── */
  .plant-cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 24px;
  }

  .plant-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 12px;
    cursor: pointer;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.1s;
    position: relative;
    overflow: hidden;
  }

  .plant-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(27,102,62,0.08) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.2s;
  }

  .plant-card:hover::before,
  .plant-card.active::before { opacity: 1; }

  .plant-card:hover {
    border-color: var(--text-dim);
    box-shadow: 0 0 10px rgba(27,102,62,0.3);
    transform: translateY(-1px);
  }

  .plant-card.active {
    border-color: var(--text-primary);
    box-shadow: var(--glow);
  }

  .card-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 10px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.08em;
    margin-bottom: 8px;
  }

  .card-stat {
    font-size: 10px;
    color: var(--text-muted);
    line-height: 1.6;
    letter-spacing: 0.05em;
  }

  .card-stat strong {
    color: var(--text-dim);
  }

  /* ── NOTICE ── */
  .notice {
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-align: center;
    margin-bottom: 20px;
    padding: 10px 16px;
    border: 1px solid rgba(27,102,62,0.2);
    border-radius: 8px;
    background: rgba(27,102,62,0.04);
    line-height: 1.6;
  }

  .notice::before {
    content: '⚠ ';
    color: var(--text-dim);
  }

  /* ── BUTTONS ── */
  .btn-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .btn {
    padding: 14px;
    border-radius: 10px;
    border: 1px solid;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.1em;
    cursor: pointer;
    text-transform: uppercase;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
  }

  .btn::after {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(255,255,255,0.05);
    opacity: 0;
    transition: opacity 0.15s;
  }

  .btn:active::after { opacity: 1; }

  .btn-save {
    background: var(--green-dark);
    border-color: var(--green-bright);
    color: var(--text-primary);
    text-shadow: var(--glow);
    box-shadow: var(--glow);
  }

  .btn-save:hover {
    background: var(--green-mid);
    box-shadow: var(--glow-strong);
  }

  .btn-wifi {
    background: rgba(200,40,40,0.12);
    border-color: #7a2020;
    color: #ff6666;
    text-shadow: 0 0 8px rgba(255,100,100,0.5);
  }

  .btn-wifi:hover {
    background: rgba(200,40,40,0.22);
    border-color: #ff6666;
    box-shadow: 0 0 12px rgba(255,100,100,0.2);
  }

  /* ── STATUS DOT ── */
  .status-bar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px;
    margin-bottom: 10px;
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 0.1em;
  }

  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--text-primary);
    box-shadow: var(--glow-strong);
    animation: dotBlink 2s ease-in-out infinite;
  }

  @keyframes dotBlink {
    0%,100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  /* ── DIVIDER ── */
  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 20px 0;
  }
</style>
</head>
<body>
<div class="wrap">

  <div class="status-bar">
    <div class="dot"></div>
    ESP32-S3 ONLINE
  </div>

  <header>
    <div class="logo">Flora<span>Care</span></div>
    <div class="logo-sub">Plant companion system v1.0</div>
  </header>

  <!-- Plant display panel -->
  <div class="plant-display">
    <div class="corner-decor tl"></div>
    <div class="corner-decor tr"></div>
    <div class="corner-decor bl"></div>
    <div class="corner-decor br"></div>

    <div class="plant-name" id="displayName">ORCHIDÉE</div>

    <div class="sensor-line">
      <span class="sensor-label">HUMIDITÉ</span>
      <div class="sensor-bar-wrap">
        <div class="sensor-bar" id="barHumid" style="width:65%"></div>
      </div>
      <span class="sensor-val" id="valHumid">65%</span>
    </div>

    <div class="sensor-line">
      <span class="sensor-label">TEMP</span>
      <div class="sensor-bar-wrap">
        <div class="sensor-bar" id="barTemp" style="width:72%"></div>
      </div>
      <span class="sensor-val" id="valTemp">22°C</span>
    </div>

    <div class="sensor-line">
      <span class="sensor-label">LUMIÈRE</span>
      <div class="sensor-bar-wrap">
        <div class="sensor-bar" id="barLight" style="width:45%"></div>
      </div>
      <span class="sensor-val" id="valLight">450lx</span>
    </div>
  </div>

  <div class="divider"></div>

  <div class="section-title">Customize ton compagnon</div>

  <!-- Couleur -->
  <div class="form-row">
    <label>Couleur LED :</label>
    <select id="colorSelect">
      <option value="vert">Vert</option>
      <option value="bleu" selected>Bleu</option>
      <option value="blanc">Blanc</option>
      <option value="rouge">Rouge</option>
      <option value="jaune">Jaune</option>
    </select>
  </div>

  <!-- Modèle de plante -->
  <div class="form-row">
    <label>Modèle plante :</label>
    <select id="plantSelect" onchange="selectPlant(this.value)">
      <option value="orchidee">Orchidée</option>
      <option value="cactus">Cactus</option>
      <option value="monstera">Monstera Deliciosa</option>
      <option value="jacinthe">Jacinthe</option>
    </select>
  </div>

  <div class="divider"></div>

  <!-- Plant cards -->
  <div class="plant-cards">
    <div class="plant-card active" id="card-orchidee" onclick="selectCard('orchidee')">
      <div class="card-name">Orchidée</div>
      <div class="card-stat">
        <strong>Temp :</strong> 18–25°C<br>
        <strong>Humid :</strong> 60–80%<br>
        <strong>Lumière :</strong> indirecte
      </div>
    </div>

    <div class="plant-card" id="card-cactus" onclick="selectCard('cactus')">
      <div class="card-name">Cactus</div>
      <div class="card-stat">
        <strong>Temp :</strong> 20–35°C<br>
        <strong>Humid :</strong> 10–30%<br>
        <strong>Lumière :</strong> directe
      </div>
    </div>

    <div class="plant-card" id="card-monstera" onclick="selectCard('monstera')">
      <div class="card-name">Monstera Deliciosa</div>
      <div class="card-stat">
        <strong>Temp :</strong> 18–30°C<br>
        <strong>Humid :</strong> 50–70%<br>
        <strong>Lumière :</strong> tamisée
      </div>
    </div>

    <div class="plant-card" id="card-jacinthe" onclick="selectCard('jacinthe')">
      <div class="card-name">Jacinthe</div>
      <div class="card-stat">
        <strong>Temp :</strong> 10–18°C<br>
        <strong>Humid :</strong> 40–60%<br>
        <strong>Lumière :</strong> vive
      </div>
    </div>
  </div>

  <div class="notice">
    Le WiFi réapparaîtra uniquement au redémarrage du FloraCare.
    Pensez à sauvegarder avant d'éteindre le point d'accès.
  </div>

  <div class="btn-row">
    <button class="btn btn-save" onclick="saveConfig()">&#x2713; Sauvegarder</button>
    <button class="btn btn-wifi" onclick="confirmWifi()">&#x2715; Éteindre WiFi</button>
  </div>

</div>

<script>
  const plants = {
    orchidee: { name: 'ORCHIDÉE', humid: 65, temp: 22, light: 45 },
    cactus:   { name: 'CACTUS',   humid: 18, temp: 28, light: 85 },
    monstera: { name: 'MONSTERA', humid: 58, temp: 24, light: 40 },
    jacinthe: { name: 'JACINTHE', humid: 50, temp: 14, light: 70 },
  };

  function selectPlant(val) {
    selectCard(val);
    document.getElementById('plantSelect').value = val;
  }

  function selectCard(key) {
    document.querySelectorAll('.plant-card').forEach(c => c.classList.remove('active'));
    document.getElementById('card-' + key).classList.add('active');
    document.getElementById('plantSelect').value = key;

    const p = plants[key];
    document.getElementById('displayName').textContent = p.name;

    document.getElementById('barHumid').style.width = p.humid + '%';
    document.getElementById('valHumid').textContent = p.humid + '%';

    const tempPct = ((p.temp - 5) / 35) * 100;
    document.getElementById('barTemp').style.width = tempPct + '%';
    document.getElementById('valTemp').textContent = p.temp + '°C';

    document.getElementById('barLight').style.width = p.light + '%';
    document.getElementById('valLight').textContent = Math.round(p.light * 10) + 'lx';
  }

  function saveConfig() {
    const color = document.getElementById('colorSelect').value;
    const plant = document.getElementById('plantSelect').value;

    // Send to ESP32 via fetch
    fetch('/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'color=' + encodeURIComponent(color) + '&plant=' + encodeURIComponent(plant)
    })
    .then(r => r.ok ? alert('✓ Configuration sauvegardée !') : alert('Erreur lors de la sauvegarde.'))
    .catch(() => alert('✓ Config sauvegardée (simulation).'));
  }

  function confirmWifi() {
    if (confirm('Éteindre le point d\'accès WiFi ? Le WiFi ne reviendra qu\'au redémarrage.')) {
      fetch('/wifi_off', { method: 'POST' })
        .then(() => alert('Point d\'accès WiFi éteint.'))
        .catch(() => alert('Commande envoyée (simulation).'));
    }
  }
</script>
</body>
</html>



"""