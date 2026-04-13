import os

with open('templates/job_list.html', 'r', encoding='utf-8') as f:
    job_html = f.read()

# Extract the header and layout boilerplate up to <main class="main-content">
main_start = job_html.find('<main class="main-content">')
if main_start != -1:
    header_html = job_html[:main_start + len('<main class="main-content">')]
    footer_html = '\n  </main>\n</div>\n</body>\n</html>'
else:
    print('Failed to parse layout')
    exit(1)

# Modify header_html to activate the 'Dự án khách hàng' link and set the exact URL 
header_html = header_html.replace('<title>Tìm việc', '<title>Dự án khách hàng')
header_html = header_html.replace('nav-link active">Tổng quan', 'nav-link">Tổng quan')

# We'll use a placeholder URL # cho "Dự án khách hàng" links since the server handles url_for
header_html = header_html.replace('href="#" class="nav-link">Dự án khách hàng', 'href="{{ url_for(\'client_projects\') }}" class="nav-link active">Dự án khách hàng')


client_content = """
    <div class="projects-header" style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 30px;">
         <div>
             <h1 style="font-size: 24px; font-weight: 700; color: #111827; margin-bottom: 8px;">Dự án Khách hàng</h1>
             <p style="color: #64748b; font-size: 14px;">Thực chiến với các dự án thật từ mạng lưới đối tác doanh nghiệp của InternshipFinder.</p>
         </div>
         <div class="tabs" style="display:flex; gap: 10px; background: white; padding: 4px; border-radius: 8px; border: 1px solid #e2e8f0;">
             <button class="tab-btn active" onclick="switchTab('explore')">Khám phá</button>
             <button class="tab-btn" onclick="switchTab('my_projects')">Dự án của tôi</button>
         </div>
    </div>

    <!-- Tab 1: Khám phá -->
    <div id="tab-explore" class="tab-pane active" style="animation: fadeIn 0.3s;">
        <!-- Search -->
        <div class="search-bar" style="background:white; padding:15px 20px; border-radius:12px; border:1px solid #e2e8f0; display:flex; gap:15px; margin-bottom: 25px;">
            <div style="flex:1; display:flex; align-items:center; gap:10px; background:#f1f5f9; padding:10px 15px; border-radius:8px;">
                <svg width="15" height="15" fill="none" stroke="#64748b" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input type="text" placeholder="Tìm kiếm dự án (VD: Landing page, App Flutter...)" style="border:none; background:transparent; width:100%; outline:none; font-family:inherit; font-size:13px;">
            </div>
            <select style="padding:10px 15px; border-radius:8px; border:1px solid #e2e8f0; outline:none; font-family:inherit; font-size:13px; color:#4b5563;">
                 <option>Kỹ năng: Tất cả</option>
                 <option>UI/UX Design</option>
                 <option>Frontend Web</option>
                 <option>Mobile App</option>
            </select>
        </div>

        <div class="projects-grid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap:20px;">
             <!-- Project Card 1 -->
             <div class="project-card" style="background:white; border:1px solid #e2e8f0; border-radius:16px; padding:24px; transition:0.15s; cursor:pointer;" onclick="openProjectModal('1')">
                  <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
                       <div style="font-size:10px; font-weight:700; color:#2563eb; background:#eff6ff; padding:4px 10px; border-radius:12px;">ĐANG MỞ ĐĂNG KÝ</div>
                       <div style="color:#64748b; font-size:12px;">2 tuần</div>
                  </div>
                  <h3 style="font-size:16px; font-weight:700; color:#111827; margin-bottom:8px; line-height:1.4;">Phát triển Landing Page quảng bá Khóa học E-learning</h3>
                  <div style="color:#64748b; font-size:13px; margin-bottom:15px; font-weight:500;">VNG Corp - ZaloPay</div>
                  <div style="font-size:13px; color:#4b5563; line-height:1.5; margin-bottom:20px;">Yêu cầu tạo landing page chuyển đổi cao cho chiến dịch mùa hè. Đã có sẵn thiết kế Figma, cần cắt HTML/CSS/JS thuần hoặc React.</div>
                  <div style="display:flex; gap:8px; margin-bottom:25px; flex-wrap:wrap;">
                      <span style="font-size:11px; background:#f8fafc; padding:4px 10px; border-radius:4px; font-weight:600; color:#4b5563; border:1px solid #e2e8f0;">ReactJS</span>
                      <span style="font-size:11px; background:#f8fafc; padding:4px 10px; border-radius:4px; font-weight:600; color:#4b5563; border:1px solid #e2e8f0;">Tailwind CSS</span>
                  </div>
                  <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #e2e8f0; padding-top:15px;">
                      <div>
                          <div style="font-size:10px; color:#64748b; margin-bottom:2px; font-weight:600;">NGÂN SÁCH</div>
                          <div style="font-size:14px; font-weight:700; color:#10b981;">2.000.000 VNĐ</div>
                      </div>
                      <button style="background:#2563eb; color:white; border:none; padding:8px 16px; border-radius:8px; font-weight:600; font-size:12px; cursor:pointer;">Nhận dự án</button>
                  </div>
             </div>
             
             <!-- Project Card 2 -->
             <div class="project-card" style="background:white; border:1px solid #e2e8f0; border-radius:16px; padding:24px; transition:0.15s; cursor:pointer;" onclick="openProjectModal('2')">
                  <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
                       <div style="font-size:10px; font-weight:700; color:#2563eb; background:#eff6ff; padding:4px 10px; border-radius:12px;">ĐANG MỞ ĐĂNG KÝ</div>
                       <div style="color:#64748b; font-size:12px;">4 tuần</div>
                  </div>
                  <h3 style="font-size:16px; font-weight:700; color:#111827; margin-bottom:8px; line-height:1.4;">App Đặt Trà Sữa (Giao Diện Khách Hàng)</h3>
                  <div style="color:#64748b; font-size:13px; margin-bottom:15px; font-weight:500;">FPT Software</div>
                  <div style="font-size:13px; color:#4b5563; line-height:1.5; margin-bottom:20px;">Tái cấu trúc UI/UX luồng mua hàng và chọn topping. Khách hàng mong đợi phong cách GenZ năng động.</div>
                  <div style="display:flex; gap:8px; margin-bottom:25px; flex-wrap:wrap;">
                      <span style="font-size:11px; background:#f8fafc; padding:4px 10px; border-radius:4px; font-weight:600; color:#4b5563; border:1px solid #e2e8f0;">Figma</span>
                      <span style="font-size:11px; background:#f8fafc; padding:4px 10px; border-radius:4px; font-weight:600; color:#4b5563; border:1px solid #e2e8f0;">UI/UX</span>
                  </div>
                  <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #e2e8f0; padding-top:15px;">
                      <div>
                          <div style="font-size:10px; color:#64748b; margin-bottom:2px; font-weight:600;">NGÂN SÁCH</div>
                          <div style="font-size:14px; font-weight:700; color:#10b981;">Thỏa thuận</div>
                      </div>
                      <button style="background:#2563eb; color:white; border:none; padding:8px 16px; border-radius:8px; font-weight:600; font-size:12px; cursor:pointer;">Nhận dự án</button>
                  </div>
             </div>

             <!-- Project Card 3 -->
             <div class="project-card" style="background:white; border:1px solid #e2e8f0; border-radius:16px; padding:24px;">
                  <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
                       <div style="font-size:10px; font-weight:700; color:#94a3b8; background:#f1f5f9; padding:4px 10px; border-radius:12px;">ĐÃ ĐÓNG GẦN ĐÂY</div>
                       <div style="color:#64748b; font-size:12px;">3 tuần</div>
                  </div>
                  <h3 style="font-size:16px; font-weight:700; color:#111827; margin-bottom:8px; line-height:1.4;">Bot Telegram Trích Xuất Dữ Liệu</h3>
                  <div style="color:#64748b; font-size:13px; margin-bottom:15px; font-weight:500;">Momo</div>
                  <div style="font-size:13px; color:#4b5563; line-height:1.5; margin-bottom:20px;">Xây dựng Bot nhận lệnh qua Telegram và crawl kết quả chứng khoán từ nguồn chỉ định trả về file thống kê.</div>
                  <div style="display:flex; gap:8px; margin-bottom:25px; flex-wrap:wrap;">
                      <span style="font-size:11px; background:#f8fafc; padding:4px 10px; border-radius:4px; font-weight:600; color:#4b5563; border:1px solid #e2e8f0;">Python</span>
                      <span style="font-size:11px; background:#f8fafc; padding:4px 10px; border-radius:4px; font-weight:600; color:#4b5563; border:1px solid #e2e8f0;">Data Scraping</span>
                  </div>
                  <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #e2e8f0; padding-top:15px;">
                      <div>
                          <div style="font-size:10px; color:#64748b; margin-bottom:2px; font-weight:600;">NGÂN SÁCH</div>
                          <div style="font-size:14px; font-weight:700; color:#64748b;">Kín chỗ (3/3)</div>
                      </div>
                      <button style="background:#f1f5f9; color:#94a3b8; border:none; padding:8px 16px; border-radius:8px; font-weight:600; font-size:12px; pointer-events:none;">Đã đủ người</button>
                  </div>
             </div>
        </div>
    </div>

    <!-- Tab 2: Dự án của tôi -->
    <div id="tab-my_projects" class="tab-pane" style="display:none; animation: fadeIn 0.3s;">
         <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:30px;">
              <h3 style="font-size: 18px; font-weight: 700; margin-bottom: 20px;">Dự án đang thực hiện</h3>
              
              <!-- Progress Item -->
              <div style="border:1px solid #e2e8f0; border-radius:12px; padding:20px; display:flex; justify-content:space-between; align-items:center;">
                   <div style="flex:1;">
                       <h4 style="font-size:16px; font-weight:700; margin-bottom:8px; color:#111827;">Hệ thống Check-in Quét Mã QR</h4>
                       <div style="font-size:13px; color:#64748b; margin-bottom:15px;">Bắt đầu: 10/04/2026 &bull; Deadline: 25/04/2026</div>
                       <div style="max-width:400px;">
                            <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:700; color:#4b5563; margin-bottom:8px;">
                                 <span>Tiến độ</span>
                                 <span style="color:#2563eb;">60%</span>
                            </div>
                            <div style="width:100%; height:8px; background:#f1f5f9; border-radius:4px; overflow:hidden;">
                                 <div style="width:60%; height:100%; background:#2563eb; border-radius:4px;"></div>
                            </div>
                       </div>
                   </div>
                   <div style="width: 250px; text-align:right;">
                        <div style="font-size:11px; font-weight:800; color:#d97706; background:#fef3c7; padding:6px 12px; border-radius:12px; display:inline-block; margin-bottom:15px;">ĐANG THỰC HIỆN</div>
                        <br>
                        <button style="background:#2563eb; color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:600; font-size:13px; cursor:pointer;" onclick="alert('Mở Workspace làm việc Nhóm')">Mở Workspace</button>
                   </div>
              </div>

         </div>
    </div>
    
    <!-- Modal Details Sidebar -->
    <div id="project-modal" style="position:fixed; top:0; right:-600px; width:550px; height:100vh; background:white; z-index:1001; box-shadow:-5px 0 30px rgba(0,0,0,0.1); transition:0.3s ease; display:flex; flex-direction:column;">
        <div style="padding:25px 30px; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
             <h2 style="font-size:18px; font-weight:700;">Chi tiết dự án</h2>
             <span style="font-size:24px; color:#64748b; cursor:pointer; line-height:1;" onclick="closeProjectModal()">&times;</span>
        </div>
        <div style="flex:1; overflow-y:auto; padding:30px;">
             <div style="font-size:10px; font-weight:800; color:#2563eb; background:#eff6ff; padding:6px 12px; border-radius:12px; display:inline-block; margin-bottom:15px;">ĐANG MỞ ĐĂNG KÝ</div>
             <h1 id="modal-title" style="font-size:22px; font-weight:800; color:#111827; margin-bottom:12px; line-height:1.4;">App Đặt Trà Sữa (Giao Diện Khách Hàng)</h1>
             <div style="display:flex; gap:20px; font-size:13px; color:#4b5563; margin-bottom:30px; font-weight:500;">
                  <div id="modal-company">Boba Tea Studio</div>
                  <div>Thời lượng: 4 tuần</div>
             </div>
             
             <h3 style="font-size:15px; font-weight:700; margin-bottom:12px; color:#1f2937;">Mô tả chung</h3>
             <p style="font-size:14px; color:#4b5563; line-height:1.6; margin-bottom:25px;">Khách hàng của chúng tôi là một chuỗi nhượng quyền trà sữa hoặc công ty dịch vụ giáo dục. Nhiệm vụ của bạn là tái cấu trúc trải nghiệm người dùng theo các form yêu cầu đính kèm lúc nhận dự án.</p>

             <h3 style="font-size:15px; font-weight:700; margin-bottom:12px; color:#1f2937;">Yêu cầu chi tiết (Deliverables)</h3>
             <ul style="font-size:14px; color:#4b5563; line-height:1.6; padding-left:20px; margin-bottom:25px;">
                 <li style="margin-bottom:8px;">Bản phác thảo rẽ nhánh UX (User Flow).</li>
                 <li style="margin-bottom:8px;">Ít nhất 10 màn hình giao diện UI chính trên Figma/Code.</li>
                 <li style="margin-bottom:8px;">Prototype bản mềm có thể truyền tải đến tay khách hàng.</li>
             </ul>

             <h3 style="font-size:15px; font-weight:700; margin-bottom:12px; color:#1f2937;">Kỹ năng yêu cầu</h3>
             <div style="display:flex; gap:10px; margin-bottom:30px; flex-wrap:wrap;">
                 <span style="font-size:12px; background:#f8fafc; padding:8px 14px; border-radius:6px; font-weight:600; color:#4b5563; border:1px solid #e2e8f0;">Cơ bản nền tảng React/Figma</span>
                 <span style="font-size:12px; background:#f8fafc; padding:8px 14px; border-radius:6px; font-weight:600; color:#4b5563; border:1px solid #e2e8f0;">Thiết kế UI/UX</span>
             </div>
             
             <div style="background:#f8fafc; border-radius:12px; padding:20px; border:1px solid #e2e8f0;">
                 <div style="font-size:11px; font-weight:700; color:#64748b; margin-bottom:5px; letter-spacing:0.5px;">QUYỀN LỢI TÀI CHÍNH</div>
                 <div style="font-size:20px; font-weight:800; color:#10b981; margin-bottom:12px;">Theo Thỏa thuận / Ngân sách dự kiến</div>
                 <div style="font-size:13px; color:#4b5563; line-height:1.5;">Đánh giá dựa trên portfolio và năng lực phân tích khi phỏng vấn qua Zoom với đại diện của khách hàng.</div>
             </div>
        </div>
        <div style="padding:20px 30px; border-top:1px solid #e2e8f0; background:#f8fafc; display:flex; gap:15px; justify-content:flex-end;">
             <button style="background:white; color:#4b5563; border:1px solid #cbd5e1; padding:12px 24px; border-radius:8px; font-weight:600; font-size:14px; cursor:pointer;" onclick="closeProjectModal()">Bỏ qua</button>
             <button style="background:#2563eb; color:white; border:none; padding:12px 30px; border-radius:8px; font-weight:600; font-size:14px; cursor:pointer;" onclick="alert('Đã gửi yêu cầu ứng tuyển! Khách hàng sẽ xem CV của bạn.')">Ứng tuyển ngay</button>
        </div>
    </div>
    <!-- Modal Backdrop -->
    <div id="modal-backdrop" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.4); z-index:1000; display:none; opacity:0; transition:0.3s ease;" onclick="closeProjectModal()"></div>

    <style>
      @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      .tab-btn { background: transparent; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; color: #64748b; cursor: pointer; transition: 0.15s; }
      .tab-btn.active { background: #f1f5f9; color: #111827; }
      .tab-btn:hover:not(.active) { color: #111827; background: #f8fafc; }
      .project-card:hover { box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-color: #cbd5e1 !important; transform: translateY(-2px); }
    </style>

    <script>
    function switchTab(tabId) {
        document.querySelectorAll('.tab-pane').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        document.getElementById('tab-' + tabId).style.display = 'block';
        
        const btns = document.querySelectorAll('.tab-btn');
        if(tabId === 'explore') btns[0].classList.add('active');
        if(tabId === 'my_projects') btns[1].classList.add('active');
    }

    function openProjectModal(id) {
        if (id === '1') {
            document.getElementById('modal-title').innerText = 'Phát triển Landing Page quảng bá Khóa học E-learning';
            document.getElementById('modal-company').innerText = 'VNG Corp - ZaloPay';
        } else {
            document.getElementById('modal-title').innerText = 'App Đặt Trà Sữa (Giao Diện Khách Hàng)';
            document.getElementById('modal-company').innerText = 'FPT Software';
        }
        
        document.getElementById('modal-backdrop').style.display = 'block';
        setTimeout(() => {
            document.getElementById('modal-backdrop').style.opacity = '1';
            document.getElementById('project-modal').style.right = '0';
        }, 10);
    }

    function closeProjectModal() {
        document.getElementById('project-modal').style.right = '-600px';
        document.getElementById('modal-backdrop').style.opacity = '0';
        setTimeout(() => {
            document.getElementById('modal-backdrop').style.display = 'none';
        }, 300);
    }
    </script>
"""

with open('templates/client_projects.html', 'w', encoding='utf-8') as f:
    f.write(header_html + client_content + footer_html)

# Also patch all other templates' navs
import glob
for filepath in glob.glob('templates/*.html'):
    if filepath != 'templates/client_projects.html':
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content.replace('href="#" class="nav-link">Dự án khách hàng', "href=\"{{ url_for('client_projects') }}\" class=\"nav-link\">Dự án khách hàng")
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

print('Generated client_projects.html and patched Navbars!')
