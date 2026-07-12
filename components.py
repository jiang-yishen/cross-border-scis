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
        f'<div><span style="font-size: 16px; margin-right: 6px;">{icon}</span>'
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
# 侧边栏导航
# =============================================================================

def sidebar_navigation():
    """渲染侧边栏导航，返回用户选择的页面"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 28px; margin-bottom: 8px;">🌐</div>
            <div style="font-size: 16px; font-weight: 700; color: #1B4965;">
                跨境海外仓<br>供应链智能决策系统
            </div>
            <div style="font-size: 11px; color: #64748B; margin-top: 4px;">
                SC-Decision Engine v1.0
            </div>
        </div>
        <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 16px 0;">
        """, unsafe_allow_html=True)
        
        pages = [
            "🏠 首页仪表盘",
            "📤 数据导入",
            "📈 需求预测分析",
            "📦 库存健康监控",
            "🔄 补货计划看板",
            "🚚 调拨建议",
            "📋 采购物流跟踪",
        ]
        
        selected = st.radio("导航", pages, label_visibility="collapsed")
        
        st.markdown("""
        <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 16px 0;">
        <div style="font-size: 11px; color: #94A3B8; text-align: center;">
            © 2024 供应链计划项目<br>基于 Streamlit 构建
        </div>
        """, unsafe_allow_html=True)
        
        return selected
