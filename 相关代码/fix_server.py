import re

with open('/opt/scis/streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改 c2 区域
old1 = """st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style=\\\"text-align:center;margin-bottom:24px;\\\"><div style=\\\"font-size:36px;margin-bottom:8px;\\\">🔐</div><h2 style=\\\"color:#1B4965;margin:0;font-size:22px;\\\">Welcome</h2><p style=\\\"color:#6B7280;margin:4px 0 0 0;font-size:13px;\\\">Please login</p></div>", unsafe_allow_html=True)"""

new1 = """st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style=\\\"background:#FFF8E7;border-radius:20px;padding:32px 28px;box-shadow:0 8px 32px rgba(139,69,19,0.12);border:1px solid rgba(222,184,135,0.35);\\\">", unsafe_allow_html=True)
        st.markdown("<div style=\\\"text-align:center;margin-bottom:24px;\\\"><div style=\\\"font-size:36px;margin-bottom:8px;\\\">🔐</div><h2 style=\\\"color:#5D4037;margin:0;font-size:22px;\\\">Welcome</h2><p style=\\\"color:#8D6E63;margin:4px 0 0 0;font-size:13px;\\\">Please login</p></div>", unsafe_allow_html=True)"""

if old1 in content:
    content = content.replace(old1, new1, 1)
    print('OK: c2 background')
else:
    print('FAIL: c2 not found')

# 2. 修改 Demo Accounts 卡片
old2 = """<div style=\\\"background:#F8FAFC;border-radius:10px;padding:16px;margin-top:16px;border:1px dashed #CBD5E1;\\\"><p style=\\\"color:#1B4965;font-weight:600;margin:0 0 8px 0;font-size:13px;\\\">Demo Accounts</p><div style=\\\"display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px;color:#4B5563;\\\"><div><b>admin</b> / jwyjys5210</div><div><span style=\\\"color:#9CA3AF;\\\">Full Access</span></div><div><b>planner</b> / scis2024</div><div><span style=\\\"color:#9CA3AF;\\\">Planner</span></div><div><b>viewer</b> / scis2024</div><div><span style=\\\"color:#9CA3AF;\\\">Read Only</span></div></div></div>"""

new2 = """<div style=\\\"background:#FFF0D4;border-radius:10px;padding:16px;margin-top:16px;border:1px dashed #DEB887;\\\"><p style=\\\"color:#5D4037;font-weight:600;margin:0 0 8px 0;font-size:13px;\\\">🐾 Demo Accounts</p><div style=\\\"display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px;color:#6D4C41;\\\"><div><b>admin</b> / jwyjys5210</div><div><span style=\\\"color:#A1887F;\\\">Full Access</span></div><div><b>planner</b> / scis2024</div><div><span style=\\\"color:#A1887F;\\\">Planner</span></div><div><b>viewer</b> / scis2024</div><div><span style=\\\"color:#A1887F;\\\">Read Only</span></div></div></div>"""

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('OK: demo card')
else:
    print('FAIL: demo card not found')

# 3. 在表单后添加闭合 div
old3 = """st.error("Invalid username or password")
        st.markdown("<div style=\\\"background:#F8FAFC"""
new3 = """st.error("Invalid username or password")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style=\\\"background:#FFF0D4"""

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('OK: closing div')
else:
    print('FAIL: closing div not found')

with open('/opt/scis/streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK: written')

import py_compile
py_compile.compile('/opt/scis/streamlit_app.py', doraise=True)
print('SYNTAX OK')
