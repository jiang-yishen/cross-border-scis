"""

跨境海外仓供应链智能决策系统 - 共用组件库

============================================

提供KPI卡片、图表主题、数据表格等共用UI组件

"""

import streamlit as st

import plotly.express as px

import plotly.graph_objects as go

from plotly.subplots import make_subplots





# =============================================================================

# 全局样式配置

# =============================================================================



def set_page_config():

    """设置页面全局配置"""

    st.set_page_config(

        page_title="跨境海外仓供应链智能决策系统",

        page_icon="🌐",

        layout="wide",

        initial_sidebar_state="expanded"

    )





def apply_custom_css():

    """注入自定义CSS样式"""

    st.markdown("""

    <style>

    /* 主色调变量 */

    :root {

        --primary: #1B4965;

        --success: #2A9D8F;

        --warning: #F4A261;

        --danger: #E63946;

        --text-secondary: #6B7280;

        --bg: #F5F7FA;

    }

    

    /* 隐藏Streamlit默认元素 */

    #MainMenu {visibility: hidden;}

    footer {visibility: hidden;}

    /* 只隐藏header中的Streamlit logo和装饰，保留侧边栏按钮 */

    header [data-testid="stDecoration"] {display: none;}

    header [data-testid="stHeaderActionElements"] {display: none;}

    

    /* 侧边栏样式 - 改为浅色背景，深色文字 */

    [data-testid="stSidebar"] {

        background-color: #F8FAFC;

        border-right: 1px solid #E2E8F0;

    }

    [data-testid="stSidebar"] .css-1d391kg {

        background-color: #F8FAFC;

    }

    [data-testid="stSidebar"] .stRadio label {

        color: #334155 !important;

        font-size: 14px;

        font-weight: 500;

    }

    [data-testid="stSidebar"] .stRadio > div {

        gap: 4px;

    }

    /* 侧边栏选中项高亮 */

    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {

        background-color: #1B4965 !important;

        border-color: #1B4965 !important;

    }

    /* 侧边栏标题文字 */

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {

        color: #1B4965 !important;

    }

    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div {

        color: #64748B;

    }

    

    /* KPI卡片容器 */

    .kpi-container {

        background: white;

        border-radius: 12px;

        padding: 20px;

        box-shadow: 0 2px 8px rgba(0,0,0,0.08);

        border-left: 4px solid var(--primary);

        height: 120px;

        display: flex;

        flex-direction: column;

        justify-content: space-between;

        transition: all 0.2s ease;

    }

    .kpi-container:hover {

        transform: translateY(-2px);

        box-shadow: 0 6px 16px rgba(0,0,0,0.12);

    }

    

    .kpi-label {

        color: var(--text-secondary);

        font-size: 13px;

        font-weight: 500;

    }

    

    .kpi-value {

        font-size: 28px;

        font-weight: 700;

        color: var(--primary);

        line-height: 1.2;

    }

    

    .kpi-delta {

        font-size: 12px;

        font-weight: 600;

    }

    

    .kpi-delta.up { color: var(--success); }

    .kpi-delta.down { color: var(--danger); }

    

    /* 页面标题 */

    .page-title {

        font-size: 24px;

        font-weight: 700;

        color: var(--primary);

        margin-bottom: 4px;

        display: flex;

        align-items: center;

        gap: 10px;

    }

    .page-title::before {

        content: "";

        display: inline-block;

        width: 4px;

        height: 24px;

        background: linear-gradient(180deg, #1B4965 0%, #2A9D8F 100%);

        border-radius: 2px;

    }

    

    .page-subtitle {

        font-size: 14px;

        color: var(--text-secondary);

        margin-bottom: 24px;

    }

    

    /* 图表容器 */

    .chart-container {

        background: white;

        border-radius: 12px;

        padding: 16px;

        box-shadow: 0 2px 8px rgba(0,0,0,0.08);

        transition: all 0.2s ease;

    }

    .chart-container:hover {

        box-shadow: 0 4px 16px rgba(0,0,0,0.1);

    }

    </style>

    """, unsafe_allow_html=True)





# =============================================================================

# KPI 卡片组件

# =============================================================================



def kpi_card(label: str, value: str, delta: str = None, delta_color: str = "normal", 

             icon: str = "📊", border_color: str = "#1B4965"):

    """

    渲染一个KPI指标卡片

    

    Args:

        label: 指标名称

        value: 指标数值（字符串，可包含单位）

        delta: 变化值（如 "+3.2%"、"-5"）

        delta_color: "up"(绿色) / "down"(红色) / "normal"(灰色)

        icon: 图标emoji

        border_color: 左侧边框颜色

    """

    if delta:

        delta_html = f'<span class="kpi-delta {delta_color}">{delta}</span>'

        bottom_html = f'<span class="kpi-value" style="color: {border_color};">{value}</span>{delta_html}'

    else:

        bottom_html = f'<span class="kpi-value" style="color: {border_color};">{value}</span>'

    

    st.markdown(

        f'<div class="kpi-container" style="border-left-color: {border_color};">'

        f'<div style="display: flex; align-items: center; gap: 8px;">'

        f'<span style="display: inline-flex; align-items: center; justify-content: center; '

        f'width: 32px; height: 32px; border-radius: 8px; background: {border_color}15; '

        f'font-size: 18px;">{icon}</span>'

        f'<span class="kpi-label">{label}</span></div>'

        f'<div style="display: flex; justify-content: space-between; align-items: flex-end;">{bottom_html}</div>'

        f'</div>',

        unsafe_allow_html=True

    )





def kpi_row(cards: list):

    """

    渲染一行KPI卡片

    

    Args:

        cards: list of dict, 每个dict包含 label, value, delta, delta_color, icon, border_color

    """

    cols = st.columns(len(cards))

    for col, card in zip(cols, cards):

        with col:

            kpi_card(**card)





# =============================================================================

# Plotly 图表主题

# =============================================================================



def apply_plotly_theme(fig: go.Figure) -> go.Figure:

    """应用统一的Plotly主题样式"""

    fig.update_layout(

        font=dict(family="Arial, sans-serif", color="#374151"),

        paper_bgcolor="white",

        plot_bgcolor="white",

        margin=dict(l=40, r=40, t=80, b=40),

        title_font=dict(size=16, color="#1B4965"),

        title=dict(x=0.02, xanchor='left'),

        legend=dict(

            orientation="v",

            yanchor="top",

            y=0.99,

            xanchor="right",

            x=0.99,

            bgcolor="rgba(255,255,255,0.85)",

            bordercolor="#E5E7EB",

            borderwidth=1

        ),

    )

    fig.update_xaxes(

        showgrid=True, gridwidth=1, gridcolor="#F3F4F6",

        showline=True, linewidth=1, linecolor="#E5E7EB"

    )

    fig.update_yaxes(

        showgrid=True, gridwidth=1, gridcolor="#F3F4F6",

        showline=True, linewidth=1, linecolor="#E5E7EB"

    )

    return fig





def create_bar_chart(df, x_col, y_col, title, color_col=None, color_map=None):

    """创建统一风格的柱状图"""

    if color_col and color_map:

        fig = px.bar(df, x=x_col, y=y_col, color=color_col, color_discrete_map=color_map,

                     title=title, text=y_col)

    else:

        fig = px.bar(df, x=x_col, y=y_col, title=title, text=y_col,

                     color_discrete_sequence=["#1B4965"])

    fig.update_traces(textposition='outside', textfont_size=11)

    return apply_plotly_theme(fig)





def create_line_chart(df, x_col, y_col, title, color_col=None, color_map=None):

    """创建统一风格的折线图"""

    if color_col and color_map:

        fig = px.line(df, x=x_col, y=y_col, color=color_col, color_discrete_map=color_map,

                      title=title, markers=True)

    else:

        fig = px.line(df, x=x_col, y=y_col, title=title, markers=True,

                      color_discrete_sequence=["#1B4965"])

    fig.update_traces(line_width=2.5, marker_size=8)

    return apply_plotly_theme(fig)





def create_pie_chart(df, names_col, values_col, title, color_map=None):

    """创建统一风格的饼图"""

    fig = px.pie(df, names=names_col, values=values_col, title=title,

                 color_discrete_map=color_map)

    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)

    return apply_plotly_theme(fig)





def create_heatmap(z_data, x_labels, y_labels, title):

    """创建统一风格的热力图"""

    fig = go.Figure(data=go.Heatmap(

        z=z_data,

        x=x_labels,

        y=y_labels,

        colorscale=[[0, '#E8F4F8'], [0.5, '#457B9D'], [1, '#1B4965']],

        showscale=True,

        colorbar=dict(title="数量", thickness=15)

    ))

    fig.update_layout(title=title, xaxis_title="仓库", yaxis_title="品类")

    return apply_plotly_theme(fig)





# =============================================================================

# 页面标题组件

# =============================================================================



def page_header(title: str, subtitle: str = ""):

    """渲染页面标题和副标题"""

    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)

    if subtitle:

        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

    st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #E5E7EB;'>", 

                unsafe_allow_html=True)





# =============================================================================

# 侧边栏导航（大卡片样式）

# =============================================================================



# 页面配置：每个页面包含图标、标题、描述、颜色

NAV_GROUPS = [

    {

        "title": "核心运营",

        "pages": [

            {"key": "home",      "icon": "🏠", "title": "首页仪表盘",     "desc": "全局KPI概览与实时监控",     "color": "#1B4965"},

            {"key": "import",    "icon": "📤", "title": "数据导入",       "desc": "ERP数据导入与Schema验证",   "color": "#457B9D"},

            {"key": "forecast",  "icon": "📈", "title": "需求预测分析",   "desc": "Prophet+XGBoost混合预测",   "color": "#2A9D8F"},

            {"key": "inventory", "icon": "📦", "title": "库存健康监控",   "desc": "ABC-XYZ分类与智能预警",     "color": "#E63946"},

            {"key": "replenish", "icon": "🔄", "title": "补货计划看板",   "desc": "ROP触发与EOQ建议",         "color": "#F4A261"},

        ]

    },

    {

        "title": "物流调度",

        "pages": [

            {"key": "transfer",  "icon": "🚚", "title": "调拨建议",       "desc": "智能库存调拨与成本优化",     "color": "#6B7280"},

            {"key": "logistics", "icon": "📋", "title": "采购物流跟踪",   "desc": "在途订单与到货跟踪",         "color": "#1B4965"},

        ]

    },

    {

        "title": "系统管理",

        "pages": [

            {"key": "guide",     "icon": "📘", "title": "使用指南",       "desc": "系统操作手册与流程说明",     "color": "#457B9D"},

            {"key": "ops",       "icon": "⚙️", "title": "运维中心",       "desc": "问题反馈与系统维护",         "color": "#6B7280"},

        ]

    },

]



NAV_PAGES = []
for g in NAV_GROUPS:
    NAV_PAGES.extend(g["pages"])

# =========================================================================
# 用户权限配置
# =========================================================================
USERS = {
    "admin":   {"password": "jwyjys5210", "role": "admin",   "name": "系统管理员"},
    "planner": {"password": "scis2024", "role": "planner", "name": "计划主管"},
    "viewer":  {"password": "scis2024", "role": "viewer",  "name": "业务查看员"},
}

ROLE_PERMISSIONS = {
    "admin":   ["home", "import", "forecast", "inventory", "replenish", "transfer", "logistics", "guide", "ops"],
    "planner": ["home", "import", "forecast", "inventory", "replenish", "transfer", "logistics", "guide"],
    "viewer":  ["home", "guide"],
}

ROLE_ICONS = {"admin": "👑", "planner": "👤", "viewer": "🔍"}


def get_user():
    import streamlit as st
    return st.session_state.get("user_info")

def is_logged_in():
    import streamlit as st
    return st.session_state.get("user_logged_in", False) is True

def get_allowed_pages():
    user = get_user()
    if not user:
        return []
    role = user.get("role", "viewer")
    allowed_keys = set(ROLE_PERMISSIONS.get(role, []))
    return [p for p in NAV_PAGES if p["key"] in allowed_keys]


def sidebar_navigation():

for g in NAV_GROUPS:

    NAV_PAGES.extend(g["pages"])



def sidebar_navigation():

    """渲染侧边栏大卡片导航，返回用户选择的页面标题字符串"""

    # 注入导航卡片CSS（加宽侧边栏 + 美化按钮为大卡片）

    st.markdown("""

    <style>

    /* 加宽侧边栏 */

    [data-testid="stSidebar"] {

        min-width: 225px !important;

        max-width: 230px !important;

    }

    [data-testid="stSidebarContent"] {

        padding: 0 10px !important;

    }

    /* 导航按钮 - 侧边栏内所有按钮 */

    [data-testid="stSidebar"] button {

        display: flex !important;

        align-items: center !important;

        justify-content: flex-start !important;

        padding: 14px 16px !important;

        border-radius: 10px !important;

        border: 1.5px solid transparent !important;

        border-left: 4px solid #CBD5E1 !important;

        background: #FFFFFF !important;

        color: #1E293B !important;

        font-size: 15px !important;

        font-weight: 600 !important;

        text-align: left !important;

        height: auto !important;

        min-height: 56px !important;

        width: 100% !important;

        transition: all 0.2s ease !important;

        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;

    }

    [data-testid="stSidebar"] button:hover {

        background: #F8FAFC !important;

        border-color: #94A3B8 !important;

        border-left-color: #1B4965 !important;

        transform: translateX(3px) translateY(-1px) !important;

        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;

    }

    /* 选中状态 - 渐变背景 + 白色左侧竖条 */

    [data-testid="stSidebar"] button[kind="primary"] {

        background: linear-gradient(135deg, #1B4965 0%, #234B6B 100%) !important;

        border-color: #1B4965 !important;

        border-left: 4px solid #FFFFFF !important;

        color: #FFFFFF !important;

        box-shadow: 0 4px 12px rgba(27,73,101,0.3) !important;

    }

    [data-testid="stSidebar"] button[kind="primary"]:hover {

        background: linear-gradient(135deg, #234B6B 0%, #2A5A7A 100%) !important;

        transform: translateX(2px) !important;

    }

    </style>

    """, unsafe_allow_html=True)

    

    with st.sidebar:

        # Logo区域 - 深蓝渐变卡片

        st.markdown("""

        <div style="text-align: center; padding: 20px 12px 16px 12px; 

                    background: linear-gradient(135deg, #1B4965 0%, #234B6B 100%);

                    border-radius: 12px; margin: 0 0 14px 0;

                    box-shadow: 0 2px 8px rgba(27,73,101,0.2);">

            <div style="font-size: 36px; margin-bottom: 8px;">🌐</div>

            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; line-height: 1.4;">

                跨境海外仓<br>供应链智能决策系统

            </div>

            <div style="display: inline-block; background: rgba(255,255,255,0.15); 

                        color: #FFFFFF; font-size: 9px; font-weight: 600; 

                        padding: 3px 12px; border-radius: 20px; margin-top: 10px;">

                SC-Decision Engine v1.0

            </div>

        </div>

        """, unsafe_allow_html=True)

        

        # 初始化 session state（保持与旧版radio返回格式一致）

        if "nav_page" not in st.session_state:

            st.session_state.nav_page = "🏠 首页仪表盘"

        

        # 渲染分组导航

        for group in NAV_GROUPS:

            # 分组标题（居中 + 两侧装饰线）

            st.markdown(f"""

            <div style="margin: 10px 0 6px 0; padding: 0 8px; display: flex; align-items: center; justify-content: center;">

                <span style="flex: 1; height: 1px; background: #E2E8F0; max-width: 24px;"></span>

                <span style="font-size: 12px; font-weight: 700; color: #94A3B8;

                            text-transform: uppercase; letter-spacing: 0.5px; margin: 0 8px;">

                    {group['title']}

                </span>

                <span style="flex: 1; height: 1px; background: #E2E8F0; max-width: 24px;"></span>

            </div>

            """, unsafe_allow_html=True)

            

            for pg in group_pages:

                display_label = f"{pg['icon']} {pg['title']}"

                is_active = st.session_state.nav_page == display_label

                btn_type = "primary" if is_active else "secondary"

                

                with st.container():

                    st.markdown('<div class="nav-card-wrapper">', unsafe_allow_html=True)

                    if st.button(

                        display_label,

                        key=f"nav_{pg['key']}",

                        use_container_width=True,

                        type=btn_type,

                        help=pg['desc']

                    ):

                        st.session_state.nav_page = display_label

                    st.markdown('</div>', unsafe_allow_html=True)

        

        # 底部信息

        st.markdown("""

        <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 14px 0 10px 0;">

        <div style="text-align: center; padding: 0 0 4px 0;">

            <div style="font-size: 10px; color: #94A3B8; font-weight: 500; margin-bottom: 3px;">

                © 2026 供应链计划项目

            </div>

            <div style="font-size: 9px; color: #CBD5E1;">

                Powered by Streamlit · Python · Plotly

            </div>

        </div>

        """, unsafe_allow_html=True)

        

        if allowed_pages:
            _current = st.session_state.get("nav_page")
            _valid = {f"{p['icon']} {p['title']}" for p in allowed_pages}
            if _current is None or _current not in _valid:
                st.session_state.nav_page = f"{allowed_pages[0]['icon']} {allowed_pages[0]['title']}"
            return st.session_state.nav_page
        return None

