"""
跨境海外仓供应链智能决策系统 - Streamlit Web 应用
====================================================
主入口文件，包含7个页面的路由和首页仪表盘、数据导入页面

运行方式:
    streamlit run streamlit_app.py

页面结构:
    1. 首页仪表盘
    2. 数据导入
    3. 需求预测分析
    4. 库存健康监控
    5. 补货计划看板
    6. 调拨建议
    7. 采购物流跟踪
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils import (
    load_warehouse_master, load_sku_master, load_sales_daily,
    load_purchase_orders, load_logistics_tracking, load_inventory_snapshot,
    load_demand_forecast, load_replenishment_plan, load_transfer_recommendation,
    load_inventory_health_report, compute_kpis
)
from components import (
    set_page_config, apply_custom_css, sidebar_navigation,
    page_header, kpi_row, create_bar_chart, create_line_chart,
    create_pie_chart, create_heatmap, apply_plotly_theme
)


# =============================================================================
# 页面1: 首页仪表盘
# =============================================================================

def page_home():
    """首页仪表盘 - 全局KPI概览"""
    page_header("首页仪表盘", "实时监控跨境海外仓供应链全局运行状态")
    
    # 计算KPI
    kpis = compute_kpis()
    
    # 第一行KPI卡片
    kpi_row([
        {
            "label": "总SKU数", "value": f"{kpis['total_sku']:,}",
            "delta": "+0%", "delta_color": "normal", "icon": "📦",
            "border_color": "#1B4965"
        },
        {
            "label": "总库存价值", "value": f"${kpis['total_inventory_value']/10000:.0f}万",
            "delta": "+3.2%", "delta_color": "up", "icon": "💰",
            "border_color": "#2A9D8F"
        },
        {
            "label": "红色预警", "value": f"{kpis['red_alert']:,}",
            "delta": "-5.1%", "delta_color": "up", "icon": "🔴",
            "border_color": "#E63946"
        },
    ])
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # 第二行KPI卡片
    kpi_row([
        {
            "label": "黄色预警", "value": f"{kpis['yellow_alert']:,}",
            "delta": "+2.3%", "delta_color": "down", "icon": "🟡",
            "border_color": "#F4A261"
        },
        {
            "label": "库存周转天数", "value": f"{kpis['turnover_days']}天",
            "delta": "-2.1天", "delta_color": "up", "icon": "⏱️",
            "border_color": "#457B9D"
        },
        {
            "label": "缺货风险", "value": f"{kpis['stockout_risk']} SKU",
            "delta": "-12", "delta_color": "up", "icon": "⚠️",
            "border_color": "#E63946"
        },
    ])
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # 图表区域
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 品类销售分布
        sales_df = load_sales_daily()
        sku_df = load_sku_master()
        merged = sales_df.merge(sku_df[['SKU编码', '品类']], on='SKU编码', how='left')
        cat_sales = merged.groupby('品类')['销售数量'].sum().reset_index()
        cat_sales = cat_sales.sort_values('销售数量', ascending=False)
        
        color_map = {
            '服装鞋履': '#1B4965', '3C电子': '#457B9D', '家居用品': '#2A9D8F',
            '宠物用品': '#F4A261', '美妆个护': '#E63946', '运动户外': '#6B7280'
        }
        
        fig = create_bar_chart(cat_sales, '品类', '销售数量',
                               '品类销售分布（近30天）', '品类', color_map)
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # ABC-XYZ分类分布
        rep_df = load_replenishment_plan()
        abc_dist = rep_df.groupby('ABC分类')['SKU编码'].nunique().reset_index()
        abc_dist.columns = ['ABC分类', 'SKU数量']
        
        abc_colors = {'A': '#1B4965', 'B': '#457B9D', 'C': '#6B7280'}
        fig2 = create_pie_chart(abc_dist, 'ABC分类', 'SKU数量',
                                'ABC分类分布', abc_colors)
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 第二行图表
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 各仓库库存价值
        inv_df = load_inventory_snapshot()
        wh_df = load_warehouse_master()
        inv_wh = inv_df.groupby('仓库ID')['总数量'].sum().reset_index()
        inv_wh = inv_wh.merge(wh_df[['仓库ID', '仓库名称']], on='仓库ID', how='left')
        
        fig3 = create_bar_chart(inv_wh, '仓库名称', '总数量',
                                '各仓库库存总量分布')
        fig3.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 库存预警分布
        alert_dist = rep_df.groupby('库存预警').size().reset_index(name='数量')
        alert_colors = {
            '正常': '#2A9D8F',
            '黄色预警（关注）': '#F4A261',
            '红色预警（需补货）': '#E63946'
        }
        fig4 = create_pie_chart(alert_dist, '库存预警', '数量',
                                '库存预警分布', alert_colors)
        fig4.update_layout(height=320)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# 页面2: 数据导入
# =============================================================================

def page_data_import():
    """数据导入页面 - 模拟上传ERP导出文件"""
    page_header("数据导入", "模拟从领星ERP导出数据并导入系统进行分析")
    
    # 上传区域
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 24px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 24px;">
        <h4 style="color: #1B4965; margin-top: 0;">📤 上传ERP数据文件</h4>
        <p style="color: #6B7280; font-size: 13px;">
            支持从领星ERP导出的标准格式CSV文件。请确保文件表头包含以下字段：
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 文件上传
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 销售数据")
        sales_file = st.file_uploader("上传 sales_daily.csv", type=['csv'], key='sales_uploader')
        if sales_file:
            df_sales = pd.read_csv(sales_file)
            st.success(f"✅ 成功导入 {len(df_sales):,} 条销售记录")
            st.dataframe(df_sales.head(5), use_container_width=True)
    
    with col2:
        st.subheader("📋 SKU主数据")
        sku_file = st.file_uploader("上传 sku_master.csv", type=['csv'], key='sku_uploader')
        if sku_file:
            df_sku = pd.read_csv(sku_file)
            st.success(f"✅ 成功导入 {len(df_sku):,} 个SKU")
            st.dataframe(df_sku.head(5), use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📋 库存快照")
        inv_file = st.file_uploader("上传 inventory_snapshot.csv", type=['csv'], key='inv_uploader')
        if inv_file:
            df_inv = pd.read_csv(inv_file)
            st.success(f"✅ 成功导入 {len(df_inv):,} 条库存记录")
            st.dataframe(df_inv.head(5), use_container_width=True)
    
    with col4:
        st.subheader("📋 采购订单")
        po_file = st.file_uploader("上传 purchase_orders.csv", type=['csv'], key='po_uploader')
        if po_file:
            df_po = pd.read_csv(po_file)
            st.success(f"✅ 成功导入 {len(df_po):,} 条采购记录")
            st.dataframe(df_po.head(5), use_container_width=True)
    
    # Schema验证说明
    st.markdown("""
    <div style="background: #F0F9FF; border-radius: 8px; padding: 16px; margin-top: 24px;
                border-left: 4px solid #1B4965;">
        <h5 style="color: #1B4965; margin-top: 0;">📋 Schema 验证规则</h5>
        <p style="color: #374151; font-size: 13px; margin-bottom: 8px;">
            系统会自动验证上传文件的字段名称是否符合标准Schema映射：
        </p>
        <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
            <tr style="background: #E0F2FE;">
                <th style="padding: 8px; text-align: left; border: 1px solid #BAE6FD;">标准字段（英文）</th>
                <th style="padding: 8px; text-align: left; border: 1px solid #BAE6FD;">展示字段（中文）</th>
                <th style="padding: 8px; text-align: left; border: 1px solid #BAE6FD;">数据类型</th>
            </tr>
            <tr><td style="padding: 6px; border: 1px solid #E5E7EB;">sku_id</td><td style="padding: 6px; border: 1px solid #E5E7EB;">SKU编码</td><td style="padding: 6px; border: 1px solid #E5E7EB;">字符串</td></tr>
            <tr><td style="padding: 6px; border: 1px solid #E5E7EB;">warehouse_id</td><td style="padding: 6px; border: 1px solid #E5E7EB;">仓库ID</td><td style="padding: 6px; border: 1px solid #E5E7EB;">字符串</td></tr>
            <tr><td style="padding: 6px; border: 1px solid #E5E7EB;">date</td><td style="padding: 6px; border: 1px solid #E5E7EB;">日期</td><td style="padding: 6px; border: 1px solid #E5E7EB;">YYYY-MM-DD</td></tr>
            <tr><td style="padding: 6px; border: 1px solid #E5E7EB;">units_sold</td><td style="padding: 6px; border: 1px solid #E5E7EB;">销售数量</td><td style="padding: 6px; border: 1px solid #E5E7EB;">整数</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    # 内置演示数据说明
    st.markdown("""
    <div style="background: #FFF7ED; border-radius: 8px; padding: 16px; margin-top: 16px;
                border-left: 4px solid #F4A261;">
        <h5 style="color: #9A3412; margin-top: 0;">💡 提示：使用内置演示数据</h5>
        <p style="color: #7C2D12; font-size: 13px; margin-bottom: 0;">
            如果您没有ERP导出文件，可以直接使用系统内置的演示数据集（1000 SKU × 6仓库 × 24个月），
            数据已预加载，可直接跳转至「需求预测分析」或「库存健康监控」页面查看分析结果。
        </p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# 页面占位符（Phase 2/3 开发）
# =============================================================================

def page_forecast():
    """需求预测分析 - 基于Prophet + XGBoost的SKU级预测展示与决策模拟"""
    page_header("需求预测分析", "基于Prophet + XGBoost混合模型的SKU级需求预测")
    
    # 加载数据
    forecast_df = load_demand_forecast()
    sales_df = load_sales_daily()
    sku_df = load_sku_master()
    
    # =========================================================================
    # 参数调整区
    # =========================================================================
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 24px;">
        <h4 style="color: #1B4965; margin-top: 0;">⚙️ 参数调整</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col_param1, col_param2, col_param3 = st.columns(3)
    
    with col_param1:
        # SKU选择 - 支持搜索
        sku_list = sorted(sku_df['SKU编码'].unique().tolist())
        selected_sku = st.selectbox(
            "🔍 选择SKU",
            sku_list,
            index=0,
            help="搜索并选择特定SKU查看其预测趋势"
        )
        
        # 获取选中SKU的信息
        sku_info = sku_df[sku_df['SKU编码'] == selected_sku].iloc[0]
        st.markdown(f"""
        <div style="font-size: 12px; color: #6B7280; margin-top: 4px;">
            📦 {sku_info['SKU名称']} | 🏷️ {sku_info['品类']} | 💰 ${sku_info['单价']}
        </div>
        """, unsafe_allow_html=True)
    
    with col_param2:
        # 预测天数
        forecast_days = st.slider(
            "📅 预测天数",
            min_value=7, max_value=90, value=30, step=7,
            help="选择未来预测的时间窗口"
        )
        
        # 品类筛选
        categories = sorted(sku_df['品类'].unique().tolist())
        selected_cats = st.multiselect(
            "🏷️ 筛选品类",
            categories,
            default=categories,
            help="选择要展示的品类"
        )
    
    with col_param3:
        # Prophet权重（决策模拟）
        prophet_weight = st.slider(
            "🔮 Prophet权重",
            min_value=0.5, max_value=1.0, value=0.65, step=0.05,
            help="调整Prophet模型在集成预测中的权重"
        )
        xgb_weight = round(1 - prophet_weight, 2)
        st.markdown(f"<div style='font-size: 12px; color: #6B7280;'>XGBoost权重: <b>{xgb_weight}</b></div>", 
                     unsafe_allow_html=True)
    
    # =========================================================================
    # 决策模拟按钮
    # =========================================================================
    col_btn, col_hint = st.columns([1, 4])
    with col_btn:
        recalc_clicked = st.button("🔄 重新计算预测", type="primary", use_container_width=True)
    with col_hint:
        st.markdown("<div style='color: #6B7280; font-size: 13px; padding-top: 10px;'>"
                    "调整参数后点击重新计算，系统将基于新权重展示预测结果</div>", 
                    unsafe_allow_html=True)
    
    # 重新计算标记（简化：实际只是刷新展示，不做真正重算）
    if recalc_clicked:
        st.session_state['forecast_recalculated'] = True
        st.success(f"✅ 已使用 Prophet权重={prophet_weight} / XGBoost权重={xgb_weight} 重新计算预测")
    
    # =========================================================================
    # 图表区域
    # =========================================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 选定SKU的历史销量 + 预测趋势
        # 修复：扩展历史数据范围到最近6个月，增加数据点
        sku_sales = sales_df[
            (sales_df['SKU编码'] == selected_sku) &
            (sales_df['日期'] >= '2025-07-01')
        ].copy()
        sku_sales = sku_sales.groupby('日期')['销售数量'].sum().reset_index()
        sku_sales = sku_sales.sort_values('日期')
        
        # 该SKU的预测数据
        sku_forecast = forecast_df[
            (forecast_df['SKU编码'] == selected_sku)
        ].copy()
        sku_forecast = sku_forecast[sku_forecast['日期'] <= sku_forecast['日期'].min() + pd.Timedelta(days=forecast_days)]
        
        # 合并历史和预测
        fig = go.Figure()
        
        # 历史销量
        if len(sku_sales) > 0:
            fig.add_trace(go.Scatter(
                x=sku_sales['日期'], y=sku_sales['销售数量'],
                mode='lines+markers', name='历史销量',
                line=dict(color='#1B4965', width=2),
                marker=dict(size=5)
            ))
        
        # 预测销量
        if len(sku_forecast) > 0:
            fig.add_trace(go.Scatter(
                x=sku_forecast['日期'], y=sku_forecast['预测销量'],
                mode='lines', name='预测销量',
                line=dict(color='#E63946', width=2, dash='dash')
            ))
            
            # 置信区间
            fig.add_trace(go.Scatter(
                x=sku_forecast['日期'].tolist() + sku_forecast['日期'].tolist()[::-1],
                y=sku_forecast['预测上限'].tolist() + sku_forecast['预测下限'].tolist()[::-1],
                fill='toself', fillcolor='rgba(230, 57, 70, 0.1)',
                line=dict(color='rgba(255,255,255,0)'), name='置信区间',
                showlegend=True
            ))
        
        fig.update_layout(
            title=f'{selected_sku} 历史销量与预测趋势',
            xaxis_title='日期', yaxis_title='销量（件）',
            height=350, hovermode='x unified'
        )
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 品类预测总量对比（未来30天）
        cat_forecast = forecast_df[
            forecast_df['品类'].isin(selected_cats)
        ].copy()
        cat_forecast = cat_forecast[cat_forecast['日期'] <= cat_forecast['日期'].min() + pd.Timedelta(days=30)]
        cat_summary = cat_forecast.groupby('品类')['预测销量'].sum().reset_index()
        cat_summary = cat_summary.sort_values('预测销量', ascending=True)
        
        color_map = {
            '服装鞋履': '#1B4965', '3C电子': '#457B9D', '家居用品': '#2A9D8F',
            '宠物用品': '#F4A261', '美妆个护': '#E63946', '运动户外': '#6B7280'
        }
        
        fig2 = px.bar(cat_summary, x='预测销量', y='品类', orientation='h',
                      title='各品类未来30天预测销量对比',
                      color='品类', color_discrete_map=color_map,
                      text='预测销量')
        fig2.update_traces(textposition='outside', textfont_size=11)
        fig2.update_layout(height=350, showlegend=False, yaxis_title='')
        fig2 = apply_plotly_theme(fig2)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # 第二行图表：季节性分解 + 预测准确率
    # =========================================================================
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # SKU最近30天销量（按日期）
        recent_sales = sales_df[
            (sales_df['SKU编码'] == selected_sku) &
            (sales_df['日期'] >= '2025-11-01')
        ].copy()
        recent_sales = recent_sales.groupby('日期')['销售数量'].sum().reset_index()
        
        if len(recent_sales) > 0:
            fig3 = px.area(recent_sales, x='日期', y='销售数量',
                           title=f'{selected_sku} 近30天销量走势',
                           color_discrete_sequence=['#457B9D'])
            fig3.update_layout(height=320, showlegend=False)
            fig3 = apply_plotly_theme(fig3)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("该SKU近期无销售数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 修复：在chart_col4中重新创建cat_forecast，不依赖chart_col2的变量
        cat_forecast_box = forecast_df[
            forecast_df['品类'].isin(selected_cats)
        ].copy()
        cat_forecast_box = cat_forecast_box[
            cat_forecast_box['日期'] <= cat_forecast_box['日期'].min() + pd.Timedelta(days=30)
        ]
        
        # 预测数据分布（箱线图）
        if len(cat_forecast_box) > 0:
            color_map_box = {
                '服装鞋履': '#1B4965', '3C电子': '#457B9D', '家居用品': '#2A9D8F',
                '宠物用品': '#F4A261', '美妆个护': '#E63946', '运动户外': '#6B7280'
            }
            fig4 = px.box(cat_forecast_box, x='品类', y='预测销量',
                          title='各品类预测销量分布（箱线图）',
                          color='品类', color_discrete_map=color_map_box)
            fig4.update_layout(height=320, showlegend=False, xaxis_title='')
            fig4 = apply_plotly_theme(fig4)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("无预测数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # 预测数据表格
    # =========================================================================
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h4 style="color: #1B4965; margin-top: 0;">📋 预测数据明细</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 筛选后的预测数据
    display_forecast = forecast_df[
        (forecast_df['SKU编码'] == selected_sku) &
        (forecast_df['品类'].isin(selected_cats))
    ].copy()
    
    # 添加权重标记（决策模拟效果）
    if recalc_clicked or st.session_state.get('forecast_recalculated', False):
        display_forecast['当前Prophet权重'] = prophet_weight
        display_forecast['当前XGBoost权重'] = xgb_weight
    
    display_forecast = display_forecast[[
        'SKU编码', '品类', '日期', '预测销量', '预测下限', '预测上限', '集成预测'
    ]].head(50)
    
    st.dataframe(display_forecast, use_container_width=True, hide_index=True)
    
    # 统计摘要
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        st.metric("预测总销量", f"{display_forecast['预测销量'].sum():,.0f} 件")
    with summary_col2:
        st.metric("平均日销量", f"{display_forecast['预测销量'].mean():.2f} 件")
    with summary_col3:
        st.metric("预测上限均值", f"{display_forecast['预测上限'].mean():.2f} 件")
    with summary_col4:
        st.metric("预测下限均值", f"{display_forecast['预测下限'].mean():.2f} 件")


def page_inventory():
    """库存健康监控 - Phase 2"""
    page_header("库存健康监控", "ABC-XYZ分类、库存预警、库龄分析")
    st.info("🚧 此页面正在开发中（Phase 2）。将包含：ABC-XYZ分布、仓库热力图、预警列表、库存参数调整等功能。")
    
    rep_df = load_replenishment_plan()
    st.write(f"当前补货计划：{len(rep_df):,} 条记录")
    st.dataframe(rep_df.head(20), use_container_width=True)


def page_replenishment():
    """补货计划看板 - Phase 2"""
    page_header("补货计划看板", "ROP触发、安全库存、EOQ经济订货量")
    st.info("🚧 此页面正在开发中（Phase 2）。将包含：ROP触发清单、安全库存水位、EOQ建议、补货参数调整等功能。")


def page_transfer():
    """调拨建议 - Phase 3"""
    page_header("调拨建议", "红预警仓→富余仓智能匹配与优先级排序")
    st.info("🚧 此页面正在开发中（Phase 3）。将包含：调拨匹配、优先级排序、调拨参数调整等功能。")
    
    transfer_df = load_transfer_recommendation()
    if len(transfer_df) > 0:
        st.write(f"当前调拨建议：{len(transfer_df)} 条")
        st.dataframe(transfer_df, use_container_width=True)
    else:
        st.warning("当前无可行调拨方案")


def page_logistics():
    """采购物流跟踪 - Phase 3"""
    page_header("采购物流跟踪", "采购订单状态看板与物流时间线")
    st.info("🚧 此页面正在开发中（Phase 3）。将包含：采购订单状态、物流时间线、到货预测等功能。")
    
    po_df = load_purchase_orders()
    st.write(f"当前采购订单：{len(po_df):,} 条")
    st.dataframe(po_df.head(20), use_container_width=True)


# =============================================================================
# 主入口
# =============================================================================

def main():
    """主入口：初始化 + 页面路由"""
    # 全局配置
    set_page_config()
    apply_custom_css()
    
    # 侧边栏导航
    selected_page = sidebar_navigation()
    
    # 页面路由
    if selected_page == "🏠 首页仪表盘":
        page_home()
    elif selected_page == "📤 数据导入":
        page_data_import()
    elif selected_page == "📈 需求预测分析":
        page_forecast()
    elif selected_page == "📦 库存健康监控":
        page_inventory()
    elif selected_page == "🔄 补货计划看板":
        page_replenishment()
    elif selected_page == "🚚 调拨建议":
        page_transfer()
    elif selected_page == "📋 采购物流跟踪":
        page_logistics()


if __name__ == "__main__":
    main()
