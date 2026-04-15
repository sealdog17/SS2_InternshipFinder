import os

with open("templates/edit_profile.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Surround main-content with a FORM tag
main_start = html.find('<div class="main-content"')
main_close = html.find('</div>\n  </div>\n</div>') # Look for closing of main-content

if main_start != -1 and main_close != -1:
    before = html[:main_start]
    # Keep the div class=main-content
    first_div_end = html.find('>', main_start) + 1
    
    middle = html[first_div_end:main_close]
    
    # Prepend FORM right inside main-content
    form_start = '<form id="cvForm" action="{{ url_for(\'edit_profile\') }}" method="POST" enctype="multipart/form-data" style="display:contents;">\n'
    form_end = '</form>\n'
    
    after = html[main_close:]
    html = before + html[main_start:first_div_end] + form_start + middle + form_end + after
else:
    print("Could not wrap in FORM")


# 2. Add 'name' attributes to Step 1 & update photo upload handling
html = html.replace('id="photo-upload" style="display: none;"', 'id="photo-upload" name="profile_picture" style="display: none;" onchange="previewAvatar(this)"')
html = html.replace('<div class="photo-box" onclick="document.getElementById(\'photo-upload\').click()">', 
                    '<div class="photo-box" id="avatarPreviewBox" onclick="document.getElementById(\'photo-upload\').click()"' + 
                    '{% if user and user.picture %} style="background: url(\'{{ user.picture }}\') center/cover;" {% endif %}>')

html = html.replace('placeholder="Ví dụ: Nguyễn Văn A"', 'name="name" placeholder="Ví dụ: Nguyễn Văn A"')
html = html.replace('placeholder="email@vi-du.com"', 'name="email" placeholder="email@vi-du.com"')
html = html.replace('placeholder="+84 900 000 000"', 'name="phone" placeholder="+84 900 000 000"')
html = html.replace('placeholder="Thành phố, Tỉnh"', 'name="address" placeholder="Thành phố, Tỉnh"')

# Add Job Title to Step 1
job_title_html = """
            <div class="form-group row-2" style="grid-column: span 2;">
                <div>
                    <label>CHỨC DANH ỨNG TUYỂN</label>
                    <div class="input-wrapper"><i class="fas fa-briefcase"></i><input type="text" name="job_title" placeholder="VD: Data Scientist, Kế toán..." value="{{ user.job_title if user else '' }}"></div>
                </div>
            </div>"""
html = html.replace('<div class="form-group row-2" style="grid-column: span 2;">\n                <div>\n                    <label>HỌ TÊN</label>',
                    job_title_html + '\n            <div class="form-group row-2" style="grid-column: span 2;">\n                <div>\n                    <label>HỌ TÊN</label>')


# 3. Add 'name' attributes to Step 2 
html = html.replace('placeholder="Đại học Công Nghệ TP.HCM"', 'name="education_school" placeholder="Đại học Công Nghệ TP.HCM" value="{{ user.education if user else \'\' }}"')
html = html.replace('placeholder="Công nghệ phần mềm"', 'name="education_major" placeholder="Công nghệ phần mềm"')
html = html.replace('placeholder="3.8 / 4.0"', 'name="education_gpa" placeholder="3.8 / 4.0"')

# Add skills field into Widget side of Step 2
skills_html = """
                 <div style="margin-top:20px;">
                     <label style="font-size:10px;">CÁC KỸ NĂNG CHÍNH (CÁCH NHAU DẤU PHẨY)</label>
                     <input type="text" name="skills" placeholder="Java, Python, Leadership..." value="{{ user.skills if user else '' }}" style="width:100%; border-bottom:1px solid #e2e8f0; border-radius:0; padding:10px 5px; outline:none; font-size:13px; font-weight:600; font-family:inherit;">
                 </div>"""
html = html.replace('<div class="skill-bar">', skills_html + '\n                 <div class="skill-bar">')


# 4. Build Step 3
step_3_new = """
      <!-- ================= STEP 3: Experience ================= -->
      <div class="wizard-step" id="step_3" style="padding: 50px 70px;">
        <div class="page-header">
          <h1>Kinh nghiệm làm việc</h1>
          <p>Nêu bật những thành tựu sự nghiệp và lịch sử làm việc của bạn.</p>
        </div>
        
        <div class="form-card" style="padding: 30px;">
            <div class="form-group">
                <label>TÓM TẮT KINH NGHIỆM CHI TIẾT</label>
                <textarea name="experience" style="width: 100%; height: 200px; padding: 15px; border: 1px solid #e5e7eb; border-radius: 8px; font-family: inherit; font-size: 14px; outline: none; margin-top: 5px; resize:vertical; font-weight:500;" placeholder="Thời gian | Tên Công Ty | Vị Trí&#10;&#10;Mô tả công việc và thành tựu cá nhân nổi bật...">{{ user.experience if user else '' }}</textarea>
                <div style="font-size:11px; color:#64748b; margin-top:10px;"><i class="fas fa-magic"></i> Mẹo AI: Dùng động từ mạnh (Hoàn thành, Tối ưu, Đạt được số liệu X) sẽ giúp vượt qua hệ thống quét lọc ATS dễ hơn.</div>
            </div>
            
            <div class="form-group" style="margin-top:20px;">
                <label>NGÔN NGỮ NGOẠI NGỮ</label>
                <div class="input-wrapper"><i class="fas fa-language"></i><input type="text" name="languages" placeholder="English (IELTS 7.0), Tiếng Nhật (N3)..." value="{{ user.languages if user else '' }}"></div>
            </div>
        </div>

        <div class="bottom-actions" style="margin-top: 20px;">
           <button type="button" class="btn btn-outline" onclick="showStep(2)"><i class="fas fa-arrow-left"></i> Quay lại</button>
           <button type="button" class="btn btn-primary" onclick="showStep(5)">Bước tiếp theo <i class="fas fa-arrow-right"></i></button>
        </div>
      </div>
"""
step_3_start = html.find('<!-- ================= STEP 3: Experience ================= -->')
if step_3_start != -1:
    step_5_start = html.find('<!-- ================= STEP 5: Templates ================= -->', step_3_start)
    if step_5_start != -1:
        html = html[:step_3_start] + step_3_new + html[step_5_start:]

# 5. Add AJAX JS logic
js_logic = """
<script>
  function previewAvatar(input) {
      if (input.files && input.files[0]) {
          var reader = new FileReader();
          reader.onload = function(e) {
              const bg = "url('" + e.target.result + "') center/cover no-repeat";
              const box = document.getElementById('avatarPreviewBox');
              box.style.background = bg;
              box.innerHTML = ''; // Hide internal icons safely
          }
          reader.readAsDataURL(input.files[0]);
      }
  }

  function saveProfileData() {
      let form = document.getElementById('cvForm');
      let formData = new FormData(form);
      let btn = document.getElementById('ajax-save-btn');
      
      if(btn) btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lưu...';
      
      fetch('{{ url_for("edit_profile") }}', {
          method: 'POST',
          body: formData
      }).then(res => {
          if(res.ok) {
             if(btn) {
                 btn.innerHTML = '<i class="fas fa-check"></i> Đã lưu thành công';
                 btn.classList.add('btn-light');
                 btn.classList.remove('btn-primary');
             }
             setTimeout(() => { 
                 if(btn) {
                     btn.innerHTML = '<i class="fas fa-save"></i> Cập nhật vào Hồ sơ'; 
                     btn.classList.remove('btn-light');
                     btn.classList.add('btn-primary');
                 }
             }, 2000);
          } else {
             if(btn) btn.innerHTML = '<i class="fas fa-times"></i> Lỗi lưu';
          }
      });
  }
</script>
"""
html = html.replace('</body>', js_logic + '\n</body>')

# 6. Add "Save" buttons dynamically
ajax_btn = '<button type="button" id="ajax-save-btn" class="btn btn-primary" onclick="saveProfileData()"><i class="fas fa-save"></i> Cập nhật vào Hồ sơ</button>'

# Inject next to the "Tiếp theo" in Step 1
html = html.replace('<button class="btn btn-primary" onclick="showStep(2)">Tiếp theo', ajax_btn + ' <button type="button" class="btn btn-light" onclick="showStep(2)">Tiếp theo')
html = html.replace('<button class="btn btn-primary" onclick="showStep(3)">Bước tiếp theo', ajax_btn + ' <button type="button" class="btn btn-light" onclick="showStep(3)">Tiếp theo')
html = html.replace('<button type="button" class="btn btn-primary" onclick="showStep(5)">Bước tiếp theo', ajax_btn + ' <button type="button" class="btn btn-light" onclick="showStep(5)">Tiếp theo')
html = html.replace('<button class="btn btn-primary" onclick="showStep(6)">Xem Trước CV', ajax_btn + ' <button type="button" class="btn btn-light" onclick="showStep(6)">Hiển thị CV')
html = html.replace('type="submit"', 'type="button"')

# Convert all raw <button> inside .main-content to <button type="button">, or they trigger traditional submit natively
html = html.replace('<button class="btn', '<button type="button" class="btn')

with open("templates/edit_profile.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Finalized edit_profile HTML and injected JS save.")
