CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zaman TEXT NOT NULL,
    mesaj TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS engellenen_ipler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_adresi TEXT UNIQUE NOT NULL,
    engelleme_zamani TEXT NOT NULL,
    durum TEXT DEFAULT 'BLOKE'
);

CREATE TABLE IF NOT EXISTS ai_teshisleri (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zaman TEXT NOT NULL,
    hedef_ip TEXT NOT NULL,
    paket_sayisi INTEGER,
    teshis_raporu TEXT NOT NULL
);
