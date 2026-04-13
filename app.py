import os
import secrets
from datetime import timedelta, date
from io import BytesIO

from flask import Flask, render_template, redirect, url_for, session, request, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

# Cấu hình session
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SESSION_COOKIE_NAME'] = 'jobfinder_session'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobfinder.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ===================== MODELS =====================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=True)
    password_hash = db.Column(db.String(200), nullable=True)
    name = db.Column(db.String(100))
    picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    job_title = db.Column(db.String(100))
    dob = db.Column(db.String(20))
    marital_status = db.Column(db.String(20))
    languages = db.Column(db.String(100))

    cvs = db.relationship('CV', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class CV(db.Model):
    __tablename__ = 'cvs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    version = db.Column(db.Integer, default=1)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user = db.relationship('User', back_populates='cvs')
    def __repr__(self):
        return f'<CV user_id={self.user_id} version={self.version}>'

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text)
    salary_range = db.Column(db.String(100))
    location = db.Column(db.String(200))
    job_type = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    application_deadline = db.Column(db.Date)
    apply_url = db.Column(db.String(500))
    source = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>'

# ===================== OAUTH =====================
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile', 'prompt': 'select_account'}
)

# ===================== DECORATOR =====================
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            session['next_url'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ===================== ROUTES =====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('job_list'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session.permanent = True
            session['user_id'] = user.id
            session['user_name'] = user.name or user.username
            session['user_email'] = user.email
            session['user_picture'] = user.picture or None
            next_url = session.pop('next_url', url_for('job_list'))  # thay dashboard bằng job_list
            return redirect(next_url)
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

import re

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        name = request.form.get('name')
        dob = request.form.get('dob')
        address = request.form.get('address')

        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp', 'danger')
            return redirect(url_for('register'))

        if not re.search(r'[A-Z]', password) or not re.search(r'\d', password) or not re.search(r'[\W_]', password):
            flash('Mật khẩu phải chứa ít nhất 1 chữ in hoa, 1 chữ số và 1 ký tự đặc biệt', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng', 'danger')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            name=name or username,
            dob=dob,
            address=address
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session.permanent = True
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_picture'] = None

           # ... trong route register, sau khi commit
        flash('Đăng ký thành công!', 'success')
        return redirect(url_for('job_list'))  # thay dashboard

    return render_template('register.html')

@app.route('/google-login')
def google_login():
    redirect_uri = url_for('callback', _external=True)
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    return google.authorize_redirect(redirect_uri, state=state)

@app.route('/google/callback')
def callback():
    if request.args.get('state') != session.get('oauth_state'):
        return 'State mismatch - possible CSRF attack', 400
    try:
        token = google.authorize_access_token()
        user_info = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()

        google_id = user_info['sub']
        email = user_info['email']
        name = user_info.get('name', email.split('@')[0])
        picture = user_info.get('picture', '')

        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                picture=picture
            )
            db.session.add(user)
            db.session.commit()

        session.permanent = True
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_picture'] = user.picture

        session.pop('oauth_state', None)

        next_url = session.pop('next_url', url_for('job_list'))  # thay dashboard
        return redirect(next_url)

    except Exception as e:
        return f"Đã xảy ra lỗi: {str(e)}", 500



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --------------------- PROFILE & CV ---------------------
@app.route('/profile')
@login_required
def profile():
    return redirect(url_for('edit_profile'))

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        # Lưu avatar nếu có
        file = request.files.get('profile_picture')
        if file and file.filename != '':
            from werkzeug.utils import secure_filename
            import os
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))
            user.picture = url_for('static', filename='uploads/' + filename)
            session['user_picture'] = user.picture

        user.name = request.form.get('name') or user.name
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')
        user.bio = request.form.get('bio')
        user.skills = request.form.get('skills')
        user.education = request.form.get('education')
        user.experience = request.form.get('experience')
        user.job_title = request.form.get('job_title')
        user.dob = request.form.get('dob')
        user.marital_status = request.form.get('marital_status')
        user.languages = request.form.get('languages')
        
        db.session.commit()
        flash('Cập nhật hồ sơ thành công!', 'success')
        return redirect(url_for('edit_profile'))  # Ở lại trang edit để check kết quả
    return render_template('edit_profile.html', user=user)

@app.route('/profile/export-pdf')
@login_required
def export_pdf():
    user = User.query.get(session['user_id'])
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()

    style_name = ParagraphStyle('Name', parent=styles['Heading1'], fontSize=28,
                                textColor=colors.HexColor('#2c3e50'), alignment=TA_CENTER, spaceAfter=6)
    style_position = ParagraphStyle('Position', parent=styles['Heading2'], fontSize=16,
                                    textColor=colors.HexColor('#3498db'), alignment=TA_CENTER, spaceAfter=12)
    style_section = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14,
                                   textColor=colors.HexColor('#2c3e50'), spaceAfter=6, spaceBefore=12)
    style_normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, leading=12)
    style_contact = ParagraphStyle('Contact', parent=styles['Normal'], fontSize=9,
                                   textColor=colors.grey, alignment=TA_CENTER, spaceAfter=12)
    style_subsection = ParagraphStyle('Subsection', parent=styles['Heading3'], fontSize=12,
                                      textColor=colors.HexColor('#2c3e50'), spaceAfter=4, spaceBefore=8)

    story = []
    story.append(Paragraph(user.name, style_name))
    story.append(Paragraph(user.job_title or 'Ứng viên', style_position))

    contact_parts = [f"Email: {user.email}"]
    if user.phone:
        contact_parts.append(f"Phone: {user.phone}")
    if user.address:
        contact_parts.append(f"Address: {user.address}")
    story.append(Paragraph(" | ".join(contact_parts), style_contact))
    story.append(Spacer(1, 0.2*inch))

    # Cột trái
    left_items = []
    left_items.append(Paragraph("Personal Details", style_section))
    left_items.append(Paragraph(f"Date of Birth: {user.dob or 'Not provided'}", style_normal))
    left_items.append(Paragraph(f"Marital Status: {user.marital_status or 'Not provided'}", style_normal))
    left_items.append(Paragraph(f"Languages: {user.languages or 'Not provided'}", style_normal))
    left_items.append(Paragraph(f"Address: {user.address or 'Not provided'}", style_normal))
    left_items.append(Spacer(1, 0.1*inch))

    if user.skills:
        left_items.append(Paragraph("Professional Skills", style_section))
        for line in user.skills.split('\n'):
            if ':' in line:
                group, skills_text = line.split(':', 1)
                left_items.append(Paragraph(f"<b>{group.strip()}</b>", style_subsection))
                for skill in [s.strip() for s in skills_text.split(',') if s.strip()]:
                    left_items.append(Paragraph(f"• {skill}", style_normal))
            elif line.strip():
                left_items.append(Paragraph(f"• {line.strip()}", style_normal))
        left_items.append(Spacer(1, 0.1*inch))

    if user.education:
        left_items.append(Paragraph("Education", style_section))
        for edu in user.education.split('\n'):
            if edu.strip():
                left_items.append(Paragraph(f"• {edu.strip()}", style_normal))
        left_items.append(Spacer(1, 0.1*inch))

    # Cột phải
    right_items = []
    if user.bio:
        right_items.append(Paragraph("Summary", style_section))
        right_items.append(Paragraph(user.bio, style_normal))
        right_items.append(Spacer(1, 0.1*inch))

    if user.experience:
        right_items.append(Paragraph("Work Experience", style_section))
        lines = user.experience.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if ' - ' in line or '(' in line:
                right_items.append(Paragraph(line, style_subsection))
                i += 1
                while i < len(lines) and (lines[i].strip().startswith('-') or lines[i].strip().startswith('•')):
                    desc = lines[i].strip().lstrip('-• ').strip()
                    if desc:
                        right_items.append(Paragraph(f"• {desc}", style_normal))
                    i += 1
            else:
                right_items.append(Paragraph(f"• {line}", style_normal))
                i += 1
        right_items.append(Spacer(1, 0.1*inch))

    col_widths = [doc.width * 0.35, doc.width * 0.65]
    table = Table([[left_items, right_items]], colWidths=col_widths, rowHeights=None)
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"CV_{user.name}.pdf", mimetype='application/pdf')

# --------------------- JOB MANAGEMENT ---------------------
@app.route('/jobs')
@login_required
def job_list():
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    query = Job.query
    if keyword:
        query = query.filter(
            Job.title.contains(keyword) | 
            Job.description.contains(keyword) | 
            Job.required_skills.contains(keyword) |
            Job.company.contains(keyword)
        )
    if location:
        query = query.filter(Job.location.contains(location))
    if job_type:
        query = query.filter_by(job_type=job_type)
    jobs = query.order_by(Job.created_at.desc()).all()
    return render_template('job_list.html', jobs=jobs, keyword=keyword, location=location, job_type=job_type)

@app.route('/jobs/<int:job_id>')
@login_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

# ===================== TẠO DATABASE & DỮ LIỆU MẪU =====================
with app.app_context():
    db.create_all()
    print("[SUCCESS] Database created successfully!")

    if Job.query.count() == 0:
        sample_jobs = [
            Job(
                title="Frontend Developer Intern",
                company="Viettel Solutions",
                description="Phát triển giao diện ReactJS, làm việc với đội ngũ product.",
                required_skills="React, HTML/CSS, JavaScript",
                salary_range="3-5 triệu",
                location="Hà Nội",
                job_type="internship",
                industry="IT",
                application_deadline=date(2025, 12, 31),
                apply_url="https://www.vietnamworks.com/vi/tim-viec-lam/all-jobs",
                source="VietnamWorks"
            ),
            Job(
                title="Part-time Marketing Assistant",
                company="VinGroup",
                description="Hỗ trợ chiến dịch marketing, viết content, thiết kế ảnh cơ bản.",
                required_skills="Canva, Viết content, Sử dụng mạng xã hội",
                salary_range="2-3 triệu",
                location="Hồ Chí Minh",
                job_type="part-time",
                industry="Marketing",
                application_deadline=date(2025, 12, 15),
                apply_url="https://topdev.vn/it-jobs",
                source="TopDev"
            ),
            Job(
                title="Data Science Intern",
                company="FPT Software",
                description="Hỗ trợ phân tích dữ liệu, xây dựng mô hình ML.",
                required_skills="Python, Pandas, Scikit-learn",
                salary_range="4-6 triệu",
                location="Đà Nẵng",
                job_type="internship",
                industry="IT",
                application_deadline=date(2025, 12, 20),
                apply_url="https://itviec.com/it-jobs",
                source="ITviec"
            )
        ]
        db.session.add_all(sample_jobs)
        db.session.commit()
        print("✅ Đã thêm 3 công việc mẫu.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)