import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
import secrets
from datetime import datetime, timedelta, date, timezone
from io import BytesIO

from flask import Flask, render_template, redirect, url_for, session, request, flash, send_file, jsonify
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
import json

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

# ===================== HELPERS =====================
def get_vietnam_time():
    """Returns current time in Vietnam timezone (GMT+7)"""
    return datetime.now(timezone(timedelta(hours=7)))

# ===================== MODELS =====================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=True)
    password_hash = db.Column(db.String(200), nullable=True)
    name = db.Column(db.String(100))
    picture = db.Column(db.String(200)) # Ảnh tài khoản (Header)
    cv_picture = db.Column(db.String(200)) # Ảnh trong hồ sơ CV
    created_at = db.Column(db.DateTime, default=get_vietnam_time)

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
    created_at = db.Column(db.DateTime, default=get_vietnam_time)
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
    created_at = db.Column(db.DateTime, default=get_vietnam_time)
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
            flash('Incorrect username or password', 'danger')
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
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        if not re.search(r'[A-Z]', password) or not re.search(r'\d', password) or not re.search(r'[\W_]', password):
            flash('Password must contain at least 1 uppercase letter, 1 digit, and 1 special character', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email is already in use', 'danger')
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

        flash('Registration successful!', 'success')
        return redirect(url_for('job_list'))  # thay dashboard

    return render_template('register.html')

@app.route('/google-login')
def google_login():
    redirect_uri = url_for('callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/google/callback')
def callback():
    try:
        token = google.authorize_access_token()
        user_info = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()

        google_id = user_info['sub']
        email = user_info['email']
        name = user_info.get('name', email.split('@')[0])
        picture = user_info.get('picture', '')

        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            # Check if a user with the same email already exists (e.g., registered via password)
            user = User.query.filter_by(email=email).first()
            if user:
                # Link the Google account to the existing email account
                user.google_id = google_id
                if not user.picture:
                    user.picture = picture
            else:
                # Create a completely new user
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
        return f"An error occurred: {str(e)}", 500



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --------------------- CLIENT PROJECTS ---------------------
@app.route('/client-projects')
@login_required
def client_projects():
    return render_template('client_projects.html')

# --------------------- RESOURCES & SETTINGS ---------------------
@app.route('/resources')
@login_required
def resources():
    return redirect(url_for('settings'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        # Xử lý upload ảnh đại diện
        file = request.files.get('avatar')
        if file and file.filename != '':
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))
            user.picture = url_for('static', filename='uploads/' + filename)
            session['user_picture'] = user.picture # Chỉ cập nhật ảnh tài khoản/header
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'picture_url': user.picture})
            flash('Profile picture updated successfully!', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html', user=user)

@app.route('/settings/update_password', methods=['POST'])
@login_required
def update_password():
    user = User.query.get(session['user_id'])
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not user.check_password(current_password):
        flash('Incorrect current password.', 'danger')
        return redirect(url_for('settings'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('settings'))
        
    if not re.search(r'[A-Z]', new_password) or not re.search(r'\d', new_password) or not re.search(r'[\W_]', new_password):
        flash('Password must contain at least 1 uppercase letter, 1 digit, and 1 special character.', 'danger')
        return redirect(url_for('settings'))

    user.set_password(new_password)
    db.session.commit()
    flash('Password updated successfully!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(session['user_id'])
    # Optional: Delete all related CVs (if cascade delete is not set on DB level)
    cvs = CV.query.filter_by(user_id=user.id).all()
    for cv in cvs:
        db.session.delete(cv)
    
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash('Your account has been successfully deleted.', 'success')
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
            user.cv_picture = url_for('static', filename='uploads/' + filename) # Chỉ cập nhật ảnh CV
            # session['user_picture'] = user.cv_picture  # KHÔNG cập nhật ảnh header
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                db.session.commit()
                return jsonify({'success': True, 'cv_picture_url': user.cv_picture})

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
            
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('edit_profile'))
    
    cvs = CV.query.filter_by(user_id=user.id).order_by(CV.created_at.desc()).all()
    for cv in cvs:
        try:
            data = json.loads(cv.content)
            cv.parsed_title = data.get('job_title') or f"Version {cv.version}"
            cv.template_name = "Blue" if data.get('template') in ['blue', 'contemporary'] else "White"
        except:
            cv.parsed_title = f"Version {cv.version}"
            cv.template_name = "White"

    return render_template('edit_profile.html', user=user, cvs=cvs)

@app.route('/profile/cv/save', methods=['POST'])
@login_required
def save_cv():
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
        'template': request.form.get('cv_template', 'white')
    }
    
    cv_id = request.form.get('cv_id')
    if cv_id and cv_id.isdigit():
        cv = CV.query.filter_by(id=int(cv_id), user_id=user_id).first()
        if cv:
            cv.content = json.dumps(cv_data)
            cv.version += 1
            cv.created_at = get_vietnam_time()
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
    cv = CV.query.filter_by(id=cv_id, user_id=session['user_id']).first_or_404()
    data = json.loads(cv.content)
    return jsonify(data)

@app.route('/profile/cv/list')
@login_required
def list_cvs():
    user_id = session['user_id']
    cvs = CV.query.filter_by(user_id=user_id).order_by(CV.created_at.desc()).all()
    result = []
    for cv in cvs:
        try:
            data = json.loads(cv.content)
            title = data.get('job_title') or data.get('name') or f"Version {cv.version}"
            tpl_raw = data.get('template', 'white')
            template = 'Blue' if tpl_raw in ['blue', 'contemporary'] else 'White'
        except Exception:
            title = f"Version {cv.version}"
            template = 'White'
        result.append({'id': cv.id, 'title': title, 'template': template})
    return jsonify(result)

@app.route('/profile/export-pdf')
@login_required
def export_pdf():
    user = User.query.get(session['user_id'])
    
    # Check if exporting a specific CV version or current profile
    cv_id = request.args.get('cv_id')
    template_type = request.args.get('template', 'white')
    
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

    # Override with specific CV data if requested
    if cv_id and cv_id.isdigit():
        cv = CV.query.filter_by(id=int(cv_id), user_id=user.id).first()
        if cv:
            saved_data = json.loads(cv.content)
            cv_data.update(saved_data)
            if 'template' in saved_data:
                template_type = saved_data['template']

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Register Times New Roman for display support from local fonts folder
    try:
        font_path = os.path.join(app.root_path, 'static', 'fonts', 'times.ttf')
        font_path_bold = os.path.join(app.root_path, 'static', 'fonts', 'timesbd.ttf')
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
    # Remove default margins to allow full-bleed sidebar background
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0, leftMargin=0, topMargin=0, bottomMargin=0)
    
    def draw_blue_sidebar(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor('#1964d3'))
        # Using absolute points for A4 (595.27 x 841.89)
        canvas.rect(0, 0, 2.8*inch, 842, fill=1, stroke=0)
        canvas.restoreState()

    styles = getSampleStyleSheet()

    # Shared Styles using Times New Roman
    style_normal = ParagraphStyle('Normal', parent=styles['Normal'], fontName=font_main, fontSize=10, leading=14, textColor=colors.HexColor('#4b5563'))
    
    story = []

    if template_type == 'blue':
        sidebar_items = []
        main_items = []

        # Sidebar: Profile Picture - Increased size to match Web prominence
        pic = user.cv_picture or user.picture
        if pic:
            try:
                img_path = pic.replace('/static/', 'static/').split('?')[0]
                if os.path.exists(img_path):
                    sidebar_items.append(Image(img_path, width=2.4*inch, height=2.4*inch))
                    sidebar_items.append(Spacer(1, 0.4*inch))
            except:
                pass

        name_style = ParagraphStyle('PdfBlueName', fontName=font_bold, fontSize=24, textColor=colors.white, alignment=TA_CENTER, leading=28)
        job_style = ParagraphStyle('PdfBlueJob', fontName=font_main, fontSize=12, textColor=colors.HexColor('#bfdbfe'), alignment=TA_CENTER, spaceAfter=40, letterSpacing=2)
        
        sidebar_items.append(Paragraph(cv_data['name'].upper(), name_style))
        sidebar_items.append(Paragraph((cv_data['job_title'] or 'Candidate').upper(), job_style))
        
        from reportlab.platypus import HRFlowable
        def get_divider():
            return HRFlowable(width="100%", thickness=1, color=colors.HexColor('#60a5fa'), spaceAfter=15)

        side_section_style = ParagraphStyle('PdfSideSec', fontName=font_bold, fontSize=13, textColor=colors.white, spaceBefore=25, spaceAfter=8)
        side_text_style = ParagraphStyle('PdfSideText', fontName=font_main, fontSize=10, textColor=colors.HexColor('#eff6ff'), leading=18)
        
        sidebar_items.append(Paragraph("CONTACT", side_section_style))
        sidebar_items.append(get_divider())
        sidebar_items.append(Paragraph(f"<b>Email:</b><br/>{cv_data['email']}", side_text_style))
        if cv_data['phone']:
            sidebar_items.append(Paragraph(f"<b>Phone:</b><br/>{cv_data['phone']}", side_text_style))
        if cv_data['address']:
            sidebar_items.append(Paragraph(f"<b>Address:</b><br/>{cv_data['address']}", side_text_style))
        
        if cv_data['skills']:
            sidebar_items.append(Paragraph("SKILLS", side_section_style))
            sidebar_items.append(get_divider())
            for s in cv_data['skills'].split(','):
                if s.strip():
                    sidebar_items.append(Paragraph(f"• {s.strip()}", side_text_style))
        
        if cv_data['education']:
            sidebar_items.append(Paragraph("EDUCATION", side_section_style))
            sidebar_items.append(get_divider())
            sidebar_items.append(Paragraph(cv_data['education'], side_text_style))

        # Main Column items
        main_section_style = ParagraphStyle('PdfMainSec', fontName=font_bold, fontSize=15, textColor=colors.HexColor('#1e40af'), letterSpacing=1.5)
        main_text_style = ParagraphStyle('PdfMainText', fontName=font_main, fontSize=12, textColor=colors.HexColor('#1f2937'), leading=20)
        
        def add_main_section(title, content):
            if content:
                # Table-based header to achieve "Text ———" effect (matches Web flex)
                # Fixed widths prevent word-wrap/collapse issues seen in previous version
                header_table = Table([[Paragraph(title.upper(), main_section_style), ""]], colWidths=[1.8*inch, 3.2*inch])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LINEBELOW', (1,0), (1,0), 1, colors.HexColor('#94a3b8')), # Sharper line color
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ]))
                main_items.append(Spacer(1, 0.3*inch))
                main_items.append(header_table)
                main_items.append(Paragraph(content.replace('\n', '<br/>'), main_text_style))

        add_main_section("ABOUT ME", cv_data['bio'])
        add_main_section("EXPERIENCE", cv_data['experience'])
        add_main_section("LANGUAGES", cv_data['languages'])

        data = [[sidebar_items, main_items]]
        # Sidebar 3 inch, Main 5.27 inch (Total A4 width is 8.27 inch)
        t = Table(data, colWidths=[3*inch, 5.27*inch])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (0,0), 30),
            ('RIGHTPADDING', (0,0), (0,0), 30),
            ('LEFTPADDING', (1,0), (1,0), 45),
            ('RIGHTPADDING', (1,0), (1,0), 45),
            ('TOPPADDING', (0,0), (-1,-1), 40), # Reduced to align with sidebar content
        ]))
        story.append(t)
        
        doc.build(story, onFirstPage=draw_blue_sidebar, onLaterPages=draw_blue_sidebar)
    else:
        # White Layout (Centered & Elegant) - Fine-tuned for visual parity
        doc.topMargin = 0.7*inch
        doc.leftMargin = 0.8*inch
        doc.rightMargin = 0.8*inch
        
        # Name Header - Increased spaceAfter for better separation
        style_white_name = ParagraphStyle('WhiteName', fontName=font_bold, fontSize=22, textColor=colors.HexColor('#111827'), alignment=TA_CENTER, letterSpacing=4, spaceAfter=18)
        story.append(Paragraph(cv_data['name'].upper(), style_white_name))
        
        # Contact line - More spaced from name and divider
        contact_parts = []
        if cv_data['address']: contact_parts.append(cv_data['address'].upper())
        contact_parts.append(cv_data['email'].upper())
        if cv_data['phone']: contact_parts.append(cv_data['phone'].upper())
        
        style_white_contact = ParagraphStyle('WhiteContact', fontName=font_main, fontSize=8.5, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER, letterSpacing=1.5, spaceAfter=30)
        story.append(Paragraph("  •  ".join(contact_parts), style_white_contact))
        
        # Thinner Main Divider for elegance
        from reportlab.platypus import HRFlowable
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#111827'), spaceAfter=40))
        
        # Section Styles - Increased spaceBefore for "breathable" layout
        white_section_style = ParagraphStyle('WhiteSec', fontName=font_bold, fontSize=12, textColor=colors.HexColor('#111827'), spaceBefore=35, spaceAfter=12, letterSpacing=2)
        white_text_style = ParagraphStyle('WhiteText', fontName=font_main, fontSize=11, textColor=colors.HexColor('#374151'), leading=20)
        
        def add_white_section(title, content):
            if content:
                story.append(Paragraph(title.upper(), white_section_style))
                # Very thin section divider
                story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#e5e7eb'), spaceAfter=15, spaceBefore=-8))
                story.append(Paragraph(content.replace('\n', '<br/>'), white_text_style))

        add_white_section("ABOUT ME", cv_data['bio'])
        add_white_section("EXPERIENCE", cv_data['experience'])
        add_white_section("EDUCATION", cv_data['education'])
        add_white_section("SKILLS", cv_data['skills'])
        add_white_section("LANGUAGES", cv_data['languages'])

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

# ===================== CREATE DATABASE & SAMPLE DATA =====================
with app.app_context():
    db.create_all()
    # Automatically add cv_picture column if not exists (for SQLite)
    try:
        from sqlalchemy import text
        db.session.execute(text('ALTER TABLE users ADD COLUMN cv_picture VARCHAR(200)'))
        db.session.commit()
    except:
        db.session.rollback()
    print("[SUCCESS] Database created/updated successfully!")

    if Job.query.count() == 0:
        sample_jobs = [
            Job(
                title="Frontend Developer Intern",
                company="Viettel Solutions",
                description="Develop ReactJS interfaces, work with the product team.",
                required_skills="React, HTML/CSS, JavaScript",
                salary_range="3-5 million",
                location="Hanoi",
                job_type="internship",
                industry="IT",
                application_deadline=date(2025, 12, 31),
                apply_url="https://www.vietnamworks.com/vi/tim-viec-lam/all-jobs",
                source="VietnamWorks"
            ),
            Job(
                title="Part-time Marketing Assistant",
                company="VinGroup",
                description="Support marketing campaigns, content writing, basic graphic design.",
                required_skills="Canva, Content writing, Social media management",
                salary_range="2-3 million",
                location="Ho Chi Minh City",
                job_type="part-time",
                industry="Marketing",
                application_deadline=date(2025, 12, 15),
                apply_url="https://topdev.vn/it-jobs",
                source="TopDev"
            ),
            Job(
                title="Data Science Intern",
                company="FPT Software",
                description="Support data analysis, build ML models.",
                required_skills="Python, Pandas, Scikit-learn",
                salary_range="4-6 million",
                location="Da Nang",
                job_type="internship",
                industry="IT",
                application_deadline=date(2025, 12, 20),
                apply_url="https://itviec.com/it-jobs",
                source="ITviec"
            )
        ]
        db.session.add_all(sample_jobs)
        db.session.commit()
        print("✅ Added 3 sample jobs.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)