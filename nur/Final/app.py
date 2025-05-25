from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from urllib.parse import urlparse, urljoin
import json 
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Gelistirme_Anahtari'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///talep.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    talepler = db.relationship('Talep', back_populates='kullanici')
    is_admin = db.Column(db.Boolean, default=False)
    reply = db.Column(db.Text, nullable=True) 

class Talep(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    reply = db.Column(db.String(5000), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Beklemede')
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    kullanici = db.relationship('User', back_populates='talepler')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/')
def index():
    # Örnek: bu ay açılan talepler
    opened_requests = Talep.query.filter(
        db.extract('month', Talep.created_at) == datetime.now().month,
        db.extract('year', Talep.created_at) == datetime.now().year
    ).count()

    # Çözülen talepler
    resolved_requests = Talep.query.filter(
        Talep.status == 'Çözüldü'
    ).count()

    # Memnuniyet oranı - örnek olarak; cevabı olan taleplerin yüzdesi
    total_requests = Talep.query.count()
    replied_requests = Talep.query.filter(Talep.reply.isnot(None)).count()
    satisfaction_rate = 0
    if total_requests > 0:
        satisfaction_rate = int((replied_requests / total_requests) * 100)

    return render_template('index.html',
                           opened_requests=opened_requests,
                           resolved_requests=resolved_requests,
                           satisfaction_rate=satisfaction_rate)


@app.route('/admin/update-status', methods=['POST'])
@login_required
def update_status():
    if not current_user.is_admin:
        return "Erişim reddedildi", 403

    talep_id = request.form.get('talep_id')
    status = request.form.get('status')

    talep = Talep.query.get(talep_id)
    if not talep:
        flash("Talep bulunamadı!", "danger")
        return redirect(url_for('admin_panel'))

    if status not in ['Beklemede', 'İnceleniyor', 'Çözüldü', 'Reddedildi']:
        flash("Geçersiz durum seçildi!", "warning")
        return redirect(url_for('admin_panel'))

    talep.status = status
    db.session.commit()
    flash(f"Talep durumu '{status}' olarak güncellendi.", "success")
    return redirect(url_for('admin_panel'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        if not name or not email:
            flash('Lütfen tüm alanları doldurun.', 'warning')
            return redirect(url_for('profile'))

        existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            flash('Bu e-posta başka bir kullanıcıda kayıtlı!', 'danger')
            return redirect(url_for('profile'))

        current_user.name = name
        current_user.email = email
        db.session.commit()
        flash('Profil güncellendi!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        new_password2 = request.form.get('new_password2')

        if not old_password or not new_password or not new_password2:
            flash('Lütfen tüm alanları doldurun.', 'warning')
            return redirect(url_for('settings'))

        if not check_password_hash(current_user.password, old_password):
            flash('Eski şifre yanlış!', 'danger')
            return redirect(url_for('settings'))

        if new_password != new_password2:
            flash('Yeni şifreler uyuşmuyor!', 'danger')
            return redirect(url_for('settings'))

        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Şifre başarıyla değiştirildi!', 'success')
        return redirect(url_for('settings'))

    return render_template('settings.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        next_page = request.form.get('next')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Hoşgeldin {user.name}!', 'success')

            if not next_page or not is_safe_url(next_page):
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            flash('E-posta veya şifre hatalı!', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash('Tüm alanları doldurmalısınız.', 'warning')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Bu e-posta zaten kayıtlı!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Kayıt başarılı, hoş geldiniz!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '').strip().lower()

    # Sorguyu oluştur
    query = Talep.query.filter_by(kullanici_id=user.id)

    if status_filter != 'all':
        query = query.filter(Talep.status == status_filter)

    if search_query:
        query = query.filter(Talep.subject.ilike(f'%{search_query}%'))

    talepler = query.order_by(Talep.created_at.desc()).all()

    stats = {
        "opened_requests": Talep.query.filter_by(kullanici_id=user.id, reply=None).count(),
        "resolved_requests": Talep.query.filter(Talep.kullanici_id==user.id, Talep.reply.isnot(None)).count(),
        "avg_resolution_time": "-"  # Basitleştirildi
    }
    return render_template("dashboard.html", user=user, talepler=talepler, stats=stats, status_filter=status_filter, search_query=search_query)


@app.route('/dashboard/create', methods=['GET', 'POST'])
@login_required
def create_talep():
    if request.method == 'POST':
        priority = request.form.get('priority')
        tags = request.form.get('tags')
        subject = request.form.get('subject')
        description = request.form.get('description')

        yeni_talep = Talep(priority=priority, tags=tags, subject=subject, description=description, kullanici_id=current_user.id)
        db.session.add(yeni_talep)
        db.session.commit()

        flash('Talep başarıyla kaydedildi!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return "Erişim reddedildi", 403
    talepler = Talep.query.order_by(Talep.created_at.desc()).all()
    return render_template("admin.html", talepler=talepler)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if user.is_admin:
                login_user(user)
                flash('Admin girişi başarılı!', 'success')
                return redirect(url_for('admin_panel'))
            else:
                flash('Bu kullanıcı admin değil!', 'danger')
        else:
            flash('Geçersiz e-posta veya şifre!', 'danger')

    return render_template('admin-login.html')

@app.route('/admin/reply', methods=['POST'])
@login_required
def reply_talep():
    if not current_user.is_admin:
        return "Erişim reddedildi", 403

    talep_id = request.form.get('talep_id')
    reply_text = request.form.get('reply')

    talep = Talep.query.get(talep_id)
    if not talep:
        flash("Talep bulunamadı!", "danger")
        return redirect(url_for('admin_panel'))

    talep.reply = reply_text
    db.session.commit()
    flash("Yanıt başarıyla kaydedildi!", "success")
    return redirect(url_for('admin_panel'))


@app.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        if not name or not email or not password:
            flash('Tüm alanları doldurun.', 'warning')
            return redirect(url_for('create_admin'))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            existing_user.is_admin = True
            db.session.commit()
            login_user(existing_user)
            flash(f"{email} artık admin ve giriş yapıldı!", 'success')
            return redirect(url_for('admin_panel'))
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_admin = User(name=name, email=email, password=hashed_password, is_admin=True)
            db.session.add(new_admin)
            db.session.commit()
            login_user(new_admin)
            flash('Yeni admin oluşturuldu ve giriş yapıldı!', 'success')
            return redirect(url_for('admin_panel'))

    # GET isteği ise admin oluşturma formunu göster
    return '''
        <h2>Admin Oluştur</h2>
        <form method="post">
            <input type="text" name="name" placeholder="Ad Soyad" required><br>
            <input type="email" name="email" placeholder="Email" required><br>
            <input type="password" name="password" placeholder="Şifre" required><br>
            <button type="submit">Admin Yap</button>
        </form>
    '''


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    talep = Talep.query.get_or_404(id)
    if request.method == 'POST':
        talep.subject = request.form.get('subject')
        talep.description = request.form.get('description')
        talep.priority = request.form.get('priority')
        tags_value = request.form.get('tags')
        if not tags_value:
            tags_value = ''  # boş string olarak ata
        talep.tags = tags_value

        db.session.commit()
        flash('Talep güncellendi!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit.html', talep=talep)

#if __name__ == '__main__':
#    with app.app_context():
  #      db.create_all()
  #  app.run(debug=True)

 import os
 if __name__ == "__main__":
app.run(host"0.0.0.0",port=int(os.environ.get("PORT",5000)))
