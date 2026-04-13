import os
import secrets
from datetime import timedelta, date
from io import BytesIO

from flask import Flask, render_template, redirect, url_for, session, request, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
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
        return 'Lỗi xác thực (State mismatch) - Vui lòng thử lại', 400
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

# --------------------- CLIENT PROJECTS ---------------------
@app.route('/client-projects')
@login_required
def client_projects():
    return render_template('client_projects.html')

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
            # session['user_picture'] = user.picture  # Không cập nhật header bằng ảnh CV

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
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
            
        flash('Cập nhật hồ sơ thành công!', 'success')
        return redirect(url_for('edit_profile'))
    
    cvs = CV.query.filter_by(user_id=user.id).order_by(CV.created_at.desc()).all()
    return render_template('edit_profile.html', user=user, cvs=cvs)

@app.route('/profile/cv/save', methods=['POST'])
@login_required
def save_cv():
    import json
    user_id = session['user_id']
    cv_data = {
        'name': request.form.get('name'),
        'job_title': request.form.get('job_title'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'address': request.form.get('address'),
        'bio': request.form.get('bio'),
        'skills': request.form.get('skills'),
        'education': request.form.get('education'),
        'experience': request.form.get('experience'),
        'languages': request.form.get('languages'),
        'template': request.form.get('cv_template', 'minimalist')
    }
    
    cv_id = request.form.get('cv_id')
    if cv_id and cv_id.isdigit():
        cv = CV.query.filter_by(id=int(cv_id), user_id=user_id).first()
        if cv:
            cv.content = json.dumps(cv_data)
            cv.version += 1
            db.session.commit()
            return jsonify({'success': True, 'cv_id': cv.id})
    
    new_cv = CV(user_id=user_id, content=json.dumps(cv_data))
    db.session.add(new_cv)
    db.session.commit()
    return jsonify({'success': True, 'cv_id': new_cv.id})

@app.route('/profile/cv/delete/<int:cv_id>', methods=['POST'])
@login_required
def delete_cv(cv_id):
    cv = CV.query.filter_by(id=cv_id, user_id=session['user_id']).first_or_404()
    db.session.delete(cv)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/profile/cv/load/<int:cv_id>')
@login_required
def load_cv(cv_id):
    import json
    cv = CV.query.filter_by(id=cv_id, user_id=session['user_id']).first_or_404()
    data = json.loads(cv.content)
    return jsonify(data)

@app.route('/profile/export-pdf')
@login_required
def export_pdf():
    import json
    user = User.query.get(session['user_id'])
    
    # Check if exporting a specific CV version or current profile
    cv_id = request.args.get('cv_id')
    template_type = request.args.get('template', 'minimalist')
    
    cv_data = {
        'name': user.name,
        'job_title': user.job_title,
        'email': user.email,
        'phone': user.phone,
        'address': user.address,
        'bio': user.bio,
        'skills': user.skills,
        'education': user.education,
        'experience': user.experience,
        'languages': user.languages
    }

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Register Times New Roman for Vietnamese support
    try:
        font_path = "C:/Windows/Fonts/times.ttf"
        font_path_bold = "C:/Windows/Fonts/timesbd.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path))
            pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', font_path_bold))
            font_main = 'TimesNewRoman'
            font_bold = 'TimesNewRoman-Bold'
        else:
            font_main = 'Helvetica'
            font_bold = 'Helvetica-Bold'
    except:
        font_main = 'Helvetica'
        font_bold = 'Helvetica-Bold'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=0.3*inch, leftMargin=0.3*inch,
                            topMargin=0.3*inch, bottomMargin=0.3*inch)
    styles = getSampleStyleSheet()

    # Shared Styles using Times New Roman
    style_normal = ParagraphStyle('Normal', parent=styles['Normal'], fontName=font_main, fontSize=10, leading=14, textColor=colors.HexColor('#4b5563'))
    style_section = ParagraphStyle('Section', parent=styles['Heading2'], fontName=font_bold, fontSize=14, 
                                   textColor=colors.HexColor('#111827'), spaceAfter=8, spaceBefore=12)
    
    story = []

    if template_type == 'contemporary':
        # Contemporary: Two-column layout with sidebar
        # Left column (Blue Sidebar)
        left_items = []
        
        # Profile Picture Placeholder
        if user.picture:
            try:
                # Check if it's a relative path from static
                img_path = user.picture.replace('/static/', 'static/')
                if os.path.exists(img_path):
                    from reportlab.lib.utils import ImageReader
                    img = ImageReader(img_path)
                    left_items.append(Image(img_path, width=1.4*inch, height=1.4*inch)) # Adjusted to match web circle feel
                    left_items.append(Spacer(1, 0.2*inch))
            except:
                pass

        name_style = ParagraphStyle('ContempName', fontName=font_bold, fontSize=20, textColor=colors.white, alignment=TA_CENTER)
        job_style = ParagraphStyle('ContempJob', fontName=font_main, fontSize=11, textColor=colors.HexColor('#93c5fd'), alignment=TA_CENTER, spaceAfter=20)
        
        left_items.append(Paragraph(cv_data['name'], name_style))
        left_items.append(Paragraph(cv_data['job_title'] or 'Ứng viên', job_style))
        
        sidebar_section = ParagraphStyle('SideSection', fontName=font_bold, fontSize=11, textColor=colors.white, spaceBefore=15, spaceAfter=8)
        sidebar_text = ParagraphStyle('SideText', fontName=font_main, fontSize=9, textColor=colors.HexColor('#bfdbfe'), leading=12)
        
        left_items.append(Paragraph("LIÊN HỆ", sidebar_section))
        left_items.append(Paragraph(f"<b>Email:</b><br/>{cv_data['email']}", sidebar_text))
        if cv_data['phone']:
            left_items.append(Paragraph(f"<b>Số điện thoại:</b><br/>{cv_data['phone']}", sidebar_text))
        if cv_data['address']:
            left_items.append(Paragraph(f"<b>Địa chỉ:</b><br/>{cv_data['address']}", sidebar_text))
        
        if cv_data['skills']:
            left_items.append(Paragraph("KỸ NĂNG", sidebar_section))
            for s in cv_data['skills'].split(','):
                if s.strip():
                    left_items.append(Paragraph(f"• {s.strip()}", sidebar_text))
        
        if cv_data['education']:
            left_items.append(Paragraph("HỌC VẤN", sidebar_section))
            left_items.append(Paragraph(cv_data['education'], sidebar_text))

        # Right column (Main Area)
        right_items = []
        main_section = ParagraphStyle('MainSection', fontName=font_bold, fontSize=13, textColor=colors.HexColor('#1d4ed8'), spaceBefore=10, spaceAfter=10)
        
        if cv_data['bio']:
            right_items.append(Paragraph("GIỚI THIỆU BẢN THÂN", main_section))
            right_items.append(Paragraph(cv_data['bio'], style_normal))
            right_items.append(Spacer(1, 0.15*inch))
        
        if cv_data['experience']:
            right_items.append(Paragraph("KINH NGHIỆM LÀM VIỆC", main_section))
            for exp in cv_data['experience'].split('\n'):
                if exp.strip():
                    right_items.append(Paragraph(exp.strip(), style_normal))

        if cv_data['languages']:
            right_items.append(Paragraph("NGÔN NGỮ", main_section))
            right_items.append(Paragraph(cv_data['languages'], style_normal))

        # Table for Sidebar Layout
        table_data = [[left_items, right_items]]
        col_widths = [doc.width * 0.35, doc.width * 0.65]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor('#1964d3')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (0,0), 20),
            ('RIGHTPADDING', (0,0), (0,0), 15),
            ('TOPPADDING', (0,0), (-1,-1), 25),
            ('BOTTOMPADDING', (0,0), (-1,-1), 25),
            # Ensure the table expands to full height if possible (approximate)
        ]))
        story.append(table)
    else:
        # Minimalist Layout (Existing or similar)
        style_name = ParagraphStyle('Name', fontName=font_bold, fontSize=28, textColor=colors.HexColor('#111827'), alignment=TA_CENTER, spaceAfter=4)
        style_job = ParagraphStyle('Job', fontName=font_main, fontSize=14, textColor=colors.HexColor('#3b82f6'), alignment=TA_CENTER, spaceAfter=20)
        
        story.append(Paragraph(cv_data['name'], style_name))
        story.append(Paragraph((cv_data['job_title'] or 'Ứng viên').upper(), style_job))
        
        contact_line = f"{cv_data['email']}  |  {cv_data['phone'] or ''}  |  {cv_data['address'] or ''}"
        story.append(Paragraph(contact_line, ParagraphStyle('Contact', fontName=font_main, alignment=TA_CENTER, fontSize=9, textColor=colors.grey)))
        from reportlab.platypus import HRFlowable
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), spaceBefore=15, spaceAfter=15))

        if cv_data['bio']:
            story.append(Paragraph("MỤC TIÊU NGHỀ NGHIỆP", style_section))
            story.append(Paragraph(cv_data['bio'], style_normal))

        if cv_data['experience']:
            story.append(Paragraph("KINH NGHIỆM LÀM VIỆC", style_section))
            for line in cv_data['experience'].split('\n'):
                if line.strip():
                    story.append(Paragraph(f"• {line.strip()}", style_normal))

        if cv_data['education']:
            story.append(Paragraph("HỌC VẤN", style_section))
            story.append(Paragraph(cv_data['education'], style_normal))

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