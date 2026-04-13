import glob

nav_right_html = """    <div class="nav-right">
      <div class="icon-btn" title="Thông báo"><i class="far fa-bell" style="font-size: 16px;"></i></div>
      <a href="{{ url_for('edit_profile') }}" class="icon-btn" title="Cài đặt"><i class="fas fa-cog" style="font-size: 16px;"></i></a>
      <a href="{{ url_for('logout') }}" class="icon-btn" title="Đăng xuất"><i class="fas fa-sign-out-alt" style="font-size: 16px; color: #ef4444;"></i></a>
      <div class="avatar">
        {% if session.get('user_picture') %}<img src="{{ session.get('user_picture') }}">
        {% else %}{{ (session.get('user_name', 'U') or 'U')[0].upper() }}{% endif %}
      </div>
    </div>"""

FA_LINK = '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">'

TARGET_FILES = ['templates/job_list.html', 'templates/profile.html', 'templates/job_detail.html']

for filepath in TARGET_FILES:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add FontAwesome if missing
        if 'font-awesome/6.4.0' not in content:
            content = content.replace('</title>\n', '</title>\n  ' + FA_LINK + '\n')

        # Find .nav-right bounds
        start_idx = content.find('<div class="nav-right">')
        if start_idx != -1:
            end_idx = content.find('</nav>', start_idx)
            if end_idx != -1:
                # Replace the block
                content = content[:start_idx] + nav_right_html + '\n  ' + content[end_idx:]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Updated {filepath}")
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
