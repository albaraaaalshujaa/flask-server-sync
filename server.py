from flask import Flask, render_template, request, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = "your_secret_key"  # تستخدم لحماية الجلسات

# تحميل مفتاح الخدمة Firebase
cred = credentials.Certificate("hi.json")  # استبدل 'hi.json' باسم ملفك
firebase_admin.initialize_app(cred)

# الاتصال بقاعدة بيانات Firestore
db = firestore.client()
users_ref = db.collection("users")

# دالة لتسجيل المستخدم
def register(email, password):
    # تحقق إذا كان المستخدم مسجلًا بالفعل
    doc = users_ref.document(email)
    if doc.get().exists:
        return False  # يعني أن البريد الإلكتروني موجود بالفعل

    # حفظ بيانات المستخدم في Firestore
    doc.set({"email": email, "password": password})
    return True

# دالة لتسجيل الدخول
def login(email, password):
    # جلب بيانات المستخدم من Firestore
    doc = users_ref.document(email).get()
    if doc.exists and doc.to_dict()["password"] == password:
        return True
    return False

@app.route('')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if register(email, password):
            flash("✅ Registered successfully.", "success")
            return redirect(url_for('dashboard'))  # تحويل المستخدم إلى صفحة لوحة التحكم بعد التسجيل
        else:
            flash("❌ Email already registered.", "danger")
            return redirect(url_for('register_page'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if login(email, password):
            flash("✅ Login successful.", "success")
            return redirect(url_for('dashboard'))  # تحويل المستخدم إلى صفحة لوحة التحكم بعد تسجيل الدخول
        else:
            flash("❌ Invalid credentials.", "danger")
            return redirect(url_for('login_page'))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)
