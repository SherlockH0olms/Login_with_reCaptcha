# Klickon Auth System 🔐

Modern və təhlükəsiz authentication sistemi Flask, Redis, MongoDB və Google reCAPTCHA ilə.

## ✨ Xüsusiyyətlər

- **Redis Sessions**: Sürətli və scalable session management
- **MongoDB**: NoSQL database user məlumatları üçün  
- **Rate Limiting**: Brute force hücumlarına qarşı qoruma
- **Google reCAPTCHA**: Yalnız qeydiyyat zamanı bot qoruması
- **Password Hashing**: bcrypt ilə güclü şifrə qoruması
- **Email Validation**: Düzgün email format yoxlanması
- **Responsive Design**: Mobil və desktop uyğun interfeys

## 🚀 Quraşdırma

### 1. Layihəni klonlayın
```bash
git clone [your-repo]
cd klickon-auth
```

### 2. Virtual environment yaradın
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# və ya
venv\Scripts\activate     # Windows
```

### 3. Dependencies quraşdırın
```bash
pip install -r requirements.txt
```

### 4. Database servislərini işə salın

**Docker ilə (Tövsiyə edilir):**
```bash
# Redis
docker run -d --name klickon-redis -p 6379:6379 redis:7

# MongoDB  
docker run -d --name klickon-mongo -p 27017:27017 mongo:7
```

**Və ya lokal quraşdırma:**
- Redis: https://redis.io/download
- MongoDB: https://www.mongodb.com/try/download/community

### 5. Environment variables

`.env` faylı yaradın (`.env.example` əsasında):
```bash
cp .env.example .env
```

`.env` faylını redaktə edin:
```bash
FLASK_SECRET_KEY=your_very_strong_secret_key_here
REDIS_URL=redis://localhost:6379/0  
MONGO_URI=mongodb://localhost:27017/klickon_auth
RECAPTCHA_SITE_KEY=your_recaptcha_site_key
RECAPTCHA_SECRET_KEY=your_recaptcha_secret_key
```

### 6. Google reCAPTCHA Keys alın

1. https://www.google.com/recaptcha/admin saytına daxil olun
2. Yeni sayt əlavə edin
3. reCAPTCHA v2 seçin ("I'm not a robot" Checkbox)
4. Domain əlavə edin (local test üçün `localhost`)
5. SITE_KEY və SECRET_KEY alın

### 7. Tətbiqi işə salın
```bash
python app.py
```

Tətbiq http://localhost:5000 ünvanında əlçatan olacaq.

## 📂 Fayl Strukturu

```
klickon-auth/
├── app.py                 # Ana Flask tətbiq faylı
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables nümunəsi  
├── .env                  # Environment variables (yaratmalısınız)
├── migrate_sqlite_to_mongo.py  # SQLite-dan MongoDB-ə migrate
├── templates/
│   ├── index.html        # Login/Register səhifəsi
│   └── dashboard.html    # İstifadəçi dashboard
├── static/
│   ├── style.css        # Styles (enhanced)
│   └── script.js        # Frontend JavaScript
└── README.md            # Bu fayl
```

## 🛡️ Təhlükəsizlik Xüsusiyyətləri

- **Session Security**: Redis-based sessions, secure secret key
- **Password Security**: bcrypt hashing (cost=12) 
- **Rate Limiting**: 5 login/register attempt per minute
- **reCAPTCHA**: Yalnız qeydiyyatda bot qoruması
- **Input Validation**: Email format, password strength
- **CSRF Protection**: Flask-WTF token protection
- **Database Security**: MongoDB unique indexes

## ⚙️ Konfiqurasiya

### Rate Limits Dəyişmək
```python
# app.py faylında
@limiter.limit("5 per minute")  # Bu rəqəmi dəyişə bilərsiniz
```

### Session Müddəti
```python
# app.py faylında  
app.config["SESSION_PERMANENT"] = False  # True etməklə uzun müddətli
```

### MongoDB Collection Adı
```python
# app.py faylında
users_coll = db.get_collection("users")  # "users" yerinə başqa ad
```

## 🐛 Debugging

### Logs yoxlamaq:
```bash
# Redis logs
docker logs klickon-redis

# MongoDB logs  
docker logs klickon-mongo
```

### Manual test:
```bash
# Redis connection
redis-cli ping

# MongoDB connection
mongo --eval "db.runCommand('ping')"
```

## 🔄 SQLite-dan Migration

Əgər köhnə SQLite database varsa:
```bash
python migrate_sqlite_to_mongo.py
```

## 📱 Frontend Xüsusiyyətlər

- **Responsive Design**: Mobil uyğun  
- **Password Strength**: Real-time şifrə gücü göstəricisi
- **Form Validation**: Client-side validation
- **Loading States**: Submit zamanı loading animation
- **Auto-hide Messages**: Mesajlar avtomatik gizlənir
- **Keyboard Shortcuts**: Alt+R (register), Alt+L (login)

## 🚀 Production Deployment

1. **Environment**: `debug=False` edin
2. **Secret Key**: Güclü və unikal key istifadə edin  
3. **Database**: Production MongoDB cluster
4. **Redis**: Redis cluster və ya managed service
5. **HTTPS**: SSL sertifikatı istifadə edin
6. **Firewall**: Yalnız lazımi portları açın

## 🤝 Töhfə və Dəstək

Bu sistem açıq mənbə və təkmilləşdirilə biləndir. Pull request və issue-lar məmnuniyyətlə qarşılanır.

## 📄 Lisenziya

MIT License - istədiyiniz kimi istifadə edə bilərsiniz.