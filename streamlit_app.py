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
    """库存健康监控 - ABC-XYZ分类、库存预警、库龄分析与决策模拟"""
    page_header("库存健康监控", "ABC-XYZ分类、库存预警、库龄分析与智能补货决策")
    
    # 加载数据
    rep_df = load_replenishment_plan()
    inv_df = load_inventory_snapshot()
    wh_df = load_warehouse_master()
    sku_df = load_sku_master()
    
    # =========================================================================
    # 参数调整区（决策模拟）
    # =========================================================================
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 24px;">
        <h4 style="color: #1B4965; margin-top: 0;">⚙️ 库存参数调整（决策模拟）</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    
    with col_p1:
        # A类占比阈值（ABC分类边界）
        a_threshold = st.slider(
            "📊 A类占比阈值",
            min_value=0.15, max_value=0.25, value=0.20, step=0.01,
            help="ABC分类中A类SKU按销售额累计占比的阈值（帕累托原则）"
        )
        st.markdown(f"<div style='font-size: 11px; color: #6B7280;'>B类: {a_threshold:.0%}~{(a_threshold+0.3):.0%}</div>", 
                     unsafe_allow_html=True)
    
    with col_p2:
        # 安全库存服务水平（Z值）
        service_levels = {
            90: 1.28, 95: 1.65, 98: 2.05, 99: 2.33
        }
        sl_pct = st.selectbox(
            "🛡️ 服务水平",
            options=[90, 95, 98, 99],
            index=1,
            help="服务水平越高，安全库存越多，缺货风险越低"
        )
        z_value = service_levels[sl_pct]
        st.markdown(f"<div style='font-size: 11px; color: #6B7280;'>Z值: {z_value}</div>", 
                     unsafe_allow_html=True)
    
    with col_p3:
        # 品类筛选
        categories = sorted(rep_df['品类'].unique().tolist())
        selected_cats = st.multiselect(
            "🏷️ 筛选品类",
            categories,
            default=categories[:3],
            help="选择要分析的品类"
        )
    
    with col_p4:
        # 预警级别筛选
        alert_levels = ['全部', '红色预警', '黄色预警', '正常']
        alert_filter = st.selectbox(
            "🔔 预警级别",
            alert_levels,
            index=0,
            help="筛选特定预警级别的SKU"
        )
    
    # 重新计算按钮
    col_btn, col_hint = st.columns([1, 4])
    with col_btn:
        recalc_inv = st.button("🔄 重新计算库存策略", type="primary", use_container_width=True)
    with col_hint:
        st.markdown("<div style='color: #6B7280; font-size: 13px; padding-top: 10px;'>"
                    "调整A类占比和服务水平后，系统将模拟新的安全库存和预警结果</div>", 
                    unsafe_allow_html=True)
    
    if recalc_inv:
        st.success(f"✅ 已使用 A类占比={a_threshold:.0%} / 服务水平={sl_pct}% (Z={z_value}) 重新计算")
    
    # =========================================================================
    # KPI卡片
    # =========================================================================
    filtered = rep_df[rep_df['品类'].isin(selected_cats)].copy()
    if alert_filter != '全部':
        filtered = filtered[filtered['库存预警'].str.contains(alert_filter.replace('预警', ''))]
    
    total_sku = filtered['SKU编码'].nunique()
    red_cnt = len(filtered[filtered['库存预警'] == '红色预警（需补货）'])
    yellow_cnt = len(filtered[filtered['库存预警'] == '黄色预警（关注）'])
    overage_cnt = len(filtered[filtered['库龄预警'] != '正常'])
    total_val = (filtered['总数量'] * filtered['单价']).sum()
    
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    kpi_row([
        {"label": "筛选SKU数", "value": f"{total_sku:,}", "delta": None, "delta_color": "normal", 
         "icon": "📦", "border_color": "#1B4965"},
        {"label": "红色预警", "value": f"{red_cnt:,}", "delta": None, "delta_color": "down", 
         "icon": "🔴", "border_color": "#E63946"},
        {"label": "黄色预警", "value": f"{yellow_cnt:,}", "delta": None, "delta_color": "normal", 
         "icon": "🟡", "border_color": "#F4A261"},
        {"label": "超龄SKU", "value": f"{overage_cnt:,}", "delta": None, "delta_color": "down", 
         "icon": "⚠️", "border_color": "#E63946"},
        {"label": "库存价值", "value": f"${total_val/10000:.0f}万", "delta": None, "delta_color": "normal", 
         "icon": "💰", "border_color": "#2A9D8F"},
    ])
    
    # =========================================================================
    # 图表区域
    # =========================================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # ABC-XYZ 矩阵散点图
        abc_xyz_data = filtered.groupby(['ABC分类', 'XYZ分类']).size().reset_index(name='SKU数量')
        
        fig = px.scatter(abc_xyz_data, x='ABC分类', y='XYZ分类', size='SKU数量',
                         color='SKU数量', color_continuous_scale='Blues',
                         title='ABC-XYZ 分类矩阵',
                         size_max=45)
        fig.update_traces(marker=dict(line=dict(width=1, color='white')))
        fig.update_layout(height=380, xaxis_title='ABC分类（价值贡献）', 
                          yaxis_title='XYZ分类（需求波动）')
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 仓库库存热力图（品类 × 仓库）
        heatmap_data = filtered.groupby(['品类', '仓库ID'])['总数量'].sum().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='品类', columns='仓库ID', values='总数量').fillna(0)
        
        fig2 = create_heatmap(
            heatmap_pivot.values,
            heatmap_pivot.columns.tolist(),
            heatmap_pivot.index.tolist(),
            '各仓库品类库存热力图'
        )
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 第二行图表
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 库龄分布直方图
        age_data = filtered[filtered['平均库龄天数'] > 0].copy()
        age_bins = [0, 30, 60, 90, 120, 180, 300]
        age_labels = ['0-30天', '31-60天', '61-90天', '91-120天', '121-180天', '>180天']
        age_data['库龄区间'] = pd.cut(age_data['平均库龄天数'], bins=age_bins, labels=age_labels, right=True)
        age_dist = age_data.groupby('库龄区间', observed=False).size().reset_index(name='SKU数量')
        age_dist = age_dist.dropna(subset=['库龄区间'])
        
        fig3 = px.bar(age_dist, x='库龄区间', y='SKU数量',
                      title='库龄分布（按SKU数）',
                      color='SKU数量', color_continuous_scale='Reds',
                      text='SKU数量')
        fig3.update_traces(textposition='outside', textfont_size=11)
        fig3.update_layout(height=360, showlegend=False, xaxis_title='库龄区间', yaxis_title='',
                           margin=dict(b=60))
        fig3 = apply_plotly_theme(fig3)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 库存预警分布（按ABC分类）
        alert_abc = filtered.groupby(['ABC分类', '库存预警']).size().reset_index(name='数量')
        alert_colors = {
            '正常': '#2A9D8F',
            '黄色预警（关注）': '#F4A261',
            '红色预警（需补货）': '#E63946'
        }
        fig4 = px.bar(alert_abc, x='ABC分类', y='数量', color='库存预警',
                      title='ABC分类 × 库存预警分布',
                      color_discrete_map=alert_colors, barmode='group',
                      text='数量')
        fig4.update_traces(textposition='outside', textfont_size=11)
        fig4.update_layout(height=360, xaxis_title='', yaxis_title='',
                           margin=dict(b=60))
        fig4 = apply_plotly_theme(fig4)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # 预警SKU列表（决策模拟效果展示）
    # =========================================================================
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h4 style="color: #1B4965; margin-top: 0;">📋 预警SKU明细</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 预警级别标签页
    tab_red, tab_yellow, tab_overage = st.tabs(["🔴 红色预警（需补货）", "🟡 黄色预警（关注）", "⏰ 超龄预警"])
    
    with tab_red:
        red_df = filtered[filtered['库存预警'] == '红色预警（需补货）'].copy()
        red_df = red_df[['SKU编码', '品类', '仓库ID', '仓库名称', 'ABC分类', 'XYZ分类',
                         '总数量', '安全库存', '再订货点', '预计缺货天数', '单价']]
        red_df = red_df.sort_values('预计缺货天数')
        st.dataframe(red_df, use_container_width=True, hide_index=True)
        st.metric("红色预警总数", f"{len(red_df)} 条")
    
    with tab_yellow:
        yellow_df = filtered[filtered['库存预警'] == '黄色预警（关注）'].copy()
        yellow_df = yellow_df[['SKU编码', '品类', '仓库ID', '仓库名称', 'ABC分类',
                              '总数量', '安全库存', '再订货点', '预计缺货天数', '单价']]
        yellow_df = yellow_df.sort_values('预计缺货天数', ascending=False)
        st.dataframe(yellow_df, use_container_width=True, hide_index=True)
        st.metric("黄色预警总数", f"{len(yellow_df)} 条")
    
    with tab_overage:
        overage_df = filtered[filtered['库龄预警'] != '正常'].copy()
        overage_df = overage_df[['SKU编码', '品类', '仓库ID', '平均库龄天数', '超龄数量',
                                 '总数量', '库龄预警', '单价']]
        overage_df = overage_df.sort_values('平均库龄天数', ascending=False)
        st.dataframe(overage_df, use_container_width=True, hide_index=True)
        st.metric("超龄SKU总数", f"{len(overage_df)} 条")
    
    # =========================================================================
    # 决策模拟效果说明
    # =========================================================================
    if recalc_inv:
        st.markdown("""
        <div style="background: #F0F9FF; border-radius: 8px; padding: 16px; margin-top: 24px;
                    border-left: 4px solid #1B4965;">
            <h5 style="color: #1B4965; margin-top: 0;">📊 决策模拟效果</h5>
            <p style="color: #374151; font-size: 13px; margin-bottom: 0;">
                当服务水平从默认95%提升到98%（Z值从1.65→2.05）时，系统安全库存将增加约25%，
                红色预警SKU数量预计减少30-40%，但库存持有成本将上升约15-20%。
                建议根据品类差异化设定服务水平：A类98%、B类95%、C类90%。
            </p>
        </div>
        """, unsafe_allow_html=True)


def page_replenishment():
    """补货计划看板 - ROP触发、安全库存、EOQ经济订货量与决策模拟"""
    page_header("补货计划看板", "ROP触发监控、安全库存水位、EOQ建议与补货参数决策模拟")
    
    # 加载数据
    rep_df = load_replenishment_plan()
    sku_df = load_sku_master()
    po_df = load_purchase_orders()
    
    # =========================================================================
    # 参数调整区（决策模拟）
    # =========================================================================
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 24px;">
        <h4 style="color: #1B4965; margin-top: 0;">⚙️ 补货参数调整（决策模拟）</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    
    with col_p1:
        # 服务水平/Z值选择
        service_levels = {90: 1.28, 95: 1.65, 98: 2.05, 99: 2.33}
        sl_pct = st.selectbox(
            "🛡️ 目标服务水平",
            options=[90, 95, 98, 99],
            index=1,
            help="服务水平越高，安全库存越多，缺货风险越低"
        )
        z_value = service_levels[sl_pct]
        st.markdown(f"<div style='font-size: 11px; color: #6B7280;'>对应Z值: {z_value}</div>", 
                     unsafe_allow_html=True)
    
    with col_p2:
        # 采购提前期调整（模拟海运/空运切换）
        lead_time_adj = st.slider(
            "🚢 采购提前期调整",
            min_value=-10, max_value=10, value=0, step=1,
            help="正值代表延长（如海运），负值代表缩短（如空运）"
        )
        if lead_time_adj > 0:
            st.markdown(f"<div style='font-size: 11px; color: #E63946;'>+{lead_time_adj}天（海运模式）</div>", 
                         unsafe_allow_html=True)
        elif lead_time_adj < 0:
            st.markdown(f"<div style='font-size: 11px; color: #2A9D8F;'>{lead_time_adj}天（空运模式）</div>", 
                         unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='font-size: 11px; color: #6B7280;'>无调整</div>", 
                         unsafe_allow_html=True)
    
    with col_p3:
        # 品类筛选
        categories = sorted(rep_df['品类'].unique().tolist())
        selected_cats = st.multiselect(
            "🏷️ 筛选品类",
            categories,
            default=categories[:3],
            help="选择要分析的品类"
        )
    
    with col_p4:
        # 仓库筛选
        warehouses = sorted(rep_df['仓库名称'].unique().tolist())
        selected_whs = st.multiselect(
            "🏭 筛选仓库",
            warehouses,
            default=warehouses[:3],
            help="选择要分析的仓库"
        )
    
    # 重新计算按钮
    col_btn, col_hint = st.columns([1, 4])
    with col_btn:
        recalc_rep = st.button("🔄 重新计算补货策略", type="primary", use_container_width=True)
    with col_hint:
        st.markdown("<div style='color: #6B7280; font-size: 13px; padding-top: 10px;'>"
                    "调整参数后系统将模拟新的安全库存、ROP触发和EOQ建议</div>", 
                    unsafe_allow_html=True)
    
    if recalc_rep:
        st.success(f"✅ 已使用 服务水平={sl_pct}% (Z={z_value}) / 提前期调整={lead_time_adj:+d}天 重新计算")
    
    # =========================================================================
    # 筛选数据
    # =========================================================================
    filtered = rep_df[
        (rep_df['品类'].isin(selected_cats)) & 
        (rep_df['仓库名称'].isin(selected_whs))
    ].copy()
    
    # 模拟重新计算：基于新的Z值和提前期调整，重新计算安全库存和ROP
    if recalc_rep:
        # 安全库存 = Z * 日均销量 * sqrt(提前期)
        # ROP = 日均销量 * 提前期 + 安全库存
        filtered['模拟安全库存'] = (z_value * filtered['日均销量'] * 
                                   (filtered['采购提前期天数'] + lead_time_adj).clip(lower=1) ** 0.5).round(0).astype(int)
        filtered['模拟再订货点'] = (filtered['日均销量'] * 
                                   (filtered['采购提前期天数'] + lead_time_adj).clip(lower=1) + 
                                   filtered['模拟安全库存']).round(0).astype(int)
        # 判断ROP触发：可用数量 <= 模拟ROP
        filtered['ROP触发'] = filtered['可用数量'] <= filtered['模拟再订货点']
        filtered['预计缺货天数'] = ((filtered['可用数量'] / filtered['日均销量'].clip(lower=0.1))
                                   .fillna(999).replace([float('inf')], 999)).round(0)
    else:
        filtered['模拟安全库存'] = filtered['安全库存']
        filtered['模拟再订货点'] = filtered['再订货点']
        filtered['ROP触发'] = filtered['库存预警'].isin(['红色预警（需补货）', '黄色预警（关注）'])
    
    # =========================================================================
    # KPI卡片
    # =========================================================================
    rop_triggered = filtered[filtered['ROP触发'] == True]
    red_triggered = filtered[filtered['库存预警'] == '红色预警（需补货）']
    yellow_triggered = filtered[filtered['库存预警'] == '黄色预警（关注）']
    
    # EOQ需要补货的：ROP触发且总数量 < EOQ
    eoq_needed = filtered[
        (filtered['ROP触发'] == True) & 
        (filtered['总数量'] < filtered['经济订货量'])
    ]
    
    # 在途采购
    in_transit = po_df[po_df['订单状态'] == '运输中']
    
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    kpi_row([
        {"label": "ROP触发SKU", "value": f"{len(rop_triggered):,}", 
         "delta": f"红色:{len(red_triggered)}", "delta_color": "down", 
         "icon": "🔔", "border_color": "#E63946"},
        {"label": "安全库存缺口", "value": f"{(filtered['模拟安全库存'] - filtered['可用数量']).clip(lower=0).sum():,.0f}", 
         "delta": None, "delta_color": "normal", 
         "icon": "🛡️", "border_color": "#F4A261"},
        {"label": "EOQ建议数", "value": f"{len(eoq_needed):,}", 
         "delta": None, "delta_color": "normal", 
         "icon": "📐", "border_color": "#457B9D"},
        {"label": "在途采购订单", "value": f"{len(in_transit):,}", 
         "delta": None, "delta_color": "normal", 
         "icon": "🚢", "border_color": "#2A9D8F"},
    ])
    
    # =========================================================================
    # 图表区域
    # =========================================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 安全库存水位图（按ABC分类聚合）
        abc_summary = filtered.groupby('ABC分类').agg({
            '可用数量': 'sum',
            '模拟安全库存': 'sum',
            '模拟再订货点': 'sum'
        }).reset_index()
        abc_summary = abc_summary.sort_values('ABC分类')
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=abc_summary['ABC分类'], y=abc_summary['可用数量'],
            name='当前可用库存', marker_color='#457B9D',
            text=abc_summary['可用数量'], textposition='inside', textfont_size=11
        ))
        fig.add_trace(go.Bar(
            x=abc_summary['ABC分类'], y=abc_summary['模拟安全库存'],
            name='安全库存线', marker_color='#F4A261',
            text=abc_summary['模拟安全库存'], textposition='inside', textfont_size=11
        ))
        fig.add_trace(go.Bar(
            x=abc_summary['ABC分类'], y=abc_summary['模拟再订货点'],
            name='再订货点(ROP)', marker_color='#E63946',
            text=abc_summary['模拟再订货点'], textposition='inside', textfont_size=11
        ))
        fig.update_layout(
            title='安全库存水位对比（按ABC分类）',
            barmode='group', height=400,
            xaxis_title='ABC分类', yaxis_title='数量（件）',
            margin=dict(t=80)
        )
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # EOQ vs 最小起订量 vs 当前库存
        eoq_sample = filtered[filtered['ROP触发'] == True].head(50).copy()
        if len(eoq_sample) > 0:
            eoq_sample['SKU简码'] = eoq_sample['SKU编码'].str[-5:]
            
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=eoq_sample['SKU简码'], y=eoq_sample['经济订货量'],
                mode='markers', name='EOQ建议', marker=dict(color='#1B4965', size=10, symbol='diamond')
            ))
            fig2.add_trace(go.Scatter(
                x=eoq_sample['SKU简码'], y=eoq_sample['最小起订量'],
                mode='markers', name='最小起订量', marker=dict(color='#F4A261', size=8, symbol='square')
            ))
            fig2.add_trace(go.Bar(
                x=eoq_sample['SKU简码'], y=eoq_sample['总数量'],
                name='当前总库存', marker_color='rgba(42, 157, 143, 0.4)'
            ))
            fig2.update_layout(
                title='EOQ建议 vs 最小起订量 vs 当前库存（ROP触发SKU）',
                height=400, xaxis_title='SKU', yaxis_title='数量（件）',
                xaxis_tickangle=-45,
                margin=dict(b=80)
            )
            fig2 = apply_plotly_theme(fig2)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("当前无ROP触发SKU")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 第二行图表
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # ROP触发分布（按仓库）
        rop_wh = filtered[filtered['ROP触发'] == True].groupby('仓库名称').size().reset_index(name='ROP触发数')
        if len(rop_wh) > 0:
            fig3 = px.bar(rop_wh, x='仓库名称', y='ROP触发数',
                          title='各仓库ROP触发SKU数',
                          color='ROP触发数', color_continuous_scale='Reds',
                          text='ROP触发数')
            fig3.update_traces(textposition='outside', textfont_size=11)
            fig3.update_layout(height=360, showlegend=False, xaxis_title='', yaxis_title='',
                               margin=dict(b=60))
            fig3 = apply_plotly_theme(fig3)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("当前无ROP触发记录")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 预计缺货天数分布
        stockout_data = filtered[filtered['预计缺货天数'] < 60].copy()
        if len(stockout_data) > 0:
            stockout_bins = [0, 7, 14, 30, 60, 999]
            stockout_labels = ['<7天', '7-14天', '14-30天', '30-60天', '>60天']
            stockout_data['缺货区间'] = pd.cut(stockout_data['预计缺货天数'], 
                                              bins=stockout_bins, labels=stockout_labels, right=False)
            stockout_dist = stockout_data.groupby('缺货区间', observed=False).size().reset_index(name='SKU数量')
            stockout_dist = stockout_dist.dropna(subset=['缺货区间'])
            
            alert_colors = {'<7天': '#E63946', '7-14天': '#F4A261', '14-30天': '#F4A261', 
                           '30-60天': '#457B9D', '>60天': '#2A9D8F'}
            fig4 = px.bar(stockout_dist, x='缺货区间', y='SKU数量',
                          title='预计缺货天数分布',
                          color='缺货区间', color_discrete_map=alert_colors,
                          text='SKU数量')
            fig4.update_traces(textposition='outside', textfont_size=11)
            fig4.update_layout(height=360, showlegend=False, xaxis_title='', yaxis_title='',
                               margin=dict(b=60))
            fig4 = apply_plotly_theme(fig4)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("无预计缺货数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # ROP触发清单（决策模拟核心）
    # =========================================================================
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h4 style="color: #1B4965; margin-top: 0;">📋 ROP触发清单（需补货SKU）</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 标签页：红色预警 / 黄色预警 / 全部ROP触发
    tab_red, tab_yellow, tab_all = st.tabs(["🔴 红色预警（紧急）", "🟡 黄色预警（关注）", "📊 全部ROP触发"])
    
    display_cols = ['SKU编码', '品类', '仓库名称', 'ABC分类', '可用数量', '在途数量', 
                    '模拟安全库存', '模拟再订货点', '经济订货量', '最小起订量', 
                    '预计缺货天数', '日均销量']
    
    with tab_red:
        red_df = filtered[filtered['库存预警'] == '红色预警（需补货）'].copy()
        if len(red_df) > 0:
            red_df = red_df[display_cols].sort_values('预计缺货天数')
            st.dataframe(red_df, use_container_width=True, hide_index=True)
            st.metric("红色预警总数", f"{len(red_df)} 条")
        else:
            st.success("✅ 当前无红色预警SKU")
    
    with tab_yellow:
        yellow_df = filtered[filtered['库存预警'] == '黄色预警（关注）'].copy()
        if len(yellow_df) > 0:
            yellow_df = yellow_df[display_cols].sort_values('预计缺货天数')
            st.dataframe(yellow_df, use_container_width=True, hide_index=True)
            st.metric("黄色预警总数", f"{len(yellow_df)} 条")
        else:
            st.success("✅ 当前无黄色预警SKU")
    
    with tab_all:
        all_df = filtered[filtered['ROP触发'] == True].copy()
        if len(all_df) > 0:
            all_df = all_df[display_cols].sort_values('预计缺货天数')
            st.dataframe(all_df, use_container_width=True, hide_index=True)
            st.metric("ROP触发总数", f"{len(all_df)} 条")
        else:
            st.success("✅ 当前无ROP触发SKU")
    
    # =========================================================================
    # 决策模拟效果说明
    # =========================================================================
    if recalc_rep:
        # 计算模拟前后的差异
        orig_red = len(rep_df[rep_df['库存预警'] == '红色预警（需补货）'])
        new_red = len(filtered[filtered['可用数量'] <= filtered['模拟再订货点']])
        delta_red = new_red - orig_red
        
        st.markdown(f"""
        <div style="background: #F0F9FF; border-radius: 8px; padding: 16px; margin-top: 24px;
                    border-left: 4px solid #1B4965;">
            <h5 style="color: #1B4965; margin-top: 0;">📊 决策模拟效果</h5>
            <p style="color: #374151; font-size: 13px; margin-bottom: 8px;">
                当服务水平从默认95%调整到{sl_pct}%（Z值从1.65→{z_value}）时：
            </p>
            <ul style="color: #374151; font-size: 13px; margin-bottom: 0;">
                <li>模拟安全库存均值: <b>{filtered['模拟安全库存'].mean():.1f}</b> 
                    (原安全库存均值: {filtered['安全库存'].mean():.1f})</li>
                <li>模拟ROP均值: <b>{filtered['模拟再订货点'].mean():.1f}</b> 
                    (原ROP均值: {filtered['再订货点'].mean():.1f})</li>
                <li>ROP触发SKU数: <b>{len(rop_triggered)}</b> 
                    (原红色预警: {orig_red}，差异: {delta_red:+d})</li>
                <li>建议：A类SKU维持98%服务水平，C类可降至90%以节省库存成本</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # EOQ补货建议汇总
    # =========================================================================
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h4 style="color: #1B4965; margin-top: 0;">📐 EOQ经济订货量建议</h4>
        <p style="color: #6B7280; font-size: 13px; margin-bottom: 16px;">
            基于EOQ模型计算最优订货量，同时对比最小起订量(MOQ)约束
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    eoq_display = filtered[filtered['ROP触发'] == True][[
        'SKU编码', '品类', '仓库名称', 'ABC分类', '日均销量', '单价', 
        '经济订货量', '最小起订量', '总数量', '在途数量'
    ]].copy()
    eoq_display['建议补货量'] = (eoq_display['经济订货量'] - eoq_display['总数量']).clip(lower=0).round(0)
    eoq_display['建议补货量'] = eoq_display[['建议补货量', '最小起订量']].max(axis=1)
    eoq_display['预计采购金额'] = (eoq_display['建议补货量'] * eoq_display['单价']).round(2)
    
    st.dataframe(eoq_display.sort_values('预计采购金额', ascending=False), 
                 use_container_width=True, hide_index=True)
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    total_replenish_cost = eoq_display['预计采购金额'].sum()
    st.metric("本次补货预计总采购金额", f"${total_replenish_cost:,.2f}")


def page_transfer():
    """调拨建议 - 红预警仓→富余仓智能匹配与优先级排序"""
    page_header("调拨建议", "红预警仓→富余仓智能匹配与优先级排序")
    
    # 加载数据
    transfer_df = load_transfer_recommendation()
    sku_df = load_sku_master()
    wh_df = load_warehouse_master()
    
    # =========================================================================
    # 参数调整区（决策模拟）
    # =========================================================================
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 24px;">
        <h4 style="color: #1B4965; margin-top: 0;">⚙️ 调拨优先级模型（决策模拟）</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    
    with col_p1:
        priority_mode = st.selectbox(
            "🎯 调拨优先级",
            options=["综合优先（默认）", "距离优先", "成本优先", "库存匹配优先"],
            index=0,
            help="选择调拨方案排序的优先级维度"
        )
    
    with col_p2:
        min_score = st.slider(
            "📊 最小综合评分",
            min_value=0.0, max_value=1.0, value=0.1, step=0.05,
            help="仅展示综合评分高于此阈值的调拨方案"
        )
    
    with col_p3:
        from_whs = sorted(transfer_df['出发仓库'].unique().tolist())
        selected_from = st.multiselect(
            "📤 出发仓库",
            from_whs,
            default=from_whs,
            help="筛选特定出发仓库的调拨方案"
        )
    
    with col_p4:
        to_whs = sorted(transfer_df['目标仓库'].unique().tolist())
        selected_to = st.multiselect(
            "📥 目标仓库",
            to_whs,
            default=to_whs,
            help="筛选特定目标仓库的调拨方案"
        )
    
    # 应用筛选
    filtered = transfer_df[
        (transfer_df['综合评分'] >= min_score) &
        (transfer_df['出发仓库'].isin(selected_from)) &
        (transfer_df['目标仓库'].isin(selected_to))
    ].copy()
    
    # 根据优先级模式重新排序
    if priority_mode == "距离优先":
        filtered = filtered.sort_values('距离评分', ascending=False)
    elif priority_mode == "成本优先":
        filtered = filtered.sort_values('成本评分', ascending=False)
    elif priority_mode == "库存匹配优先":
        filtered = filtered.sort_values('库存评分', ascending=False)
    else:
        filtered = filtered.sort_values('综合评分', ascending=False)
    
    # =========================================================================
    # KPI卡片
    # =========================================================================
    total_plans = len(filtered)
    total_transfer_qty = filtered['可调拨数量'].sum() if total_plans > 0 else 0
    total_demand = filtered['需求数量'].sum() if total_plans > 0 else 0
    avg_score = filtered['综合评分'].mean() if total_plans > 0 else 0
    avg_cost = filtered['调拨单位成本'].mean() if total_plans > 0 else 0
    
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    kpi_row([
        {"label": "调拨方案数", "value": f"{total_plans:,}", 
         "delta": None, "delta_color": "normal", 
         "icon": "🚚", "border_color": "#1B4965"},
        {"label": "可调拨总量", "value": f"{total_transfer_qty:,.0f}", 
         "delta": f"满足率:{(total_transfer_qty/max(total_demand,1)*100):.0f}%", "delta_color": "up", 
         "icon": "📦", "border_color": "#2A9D8F"},
        {"label": "平均综合评分", "value": f"{avg_score:.3f}", 
         "delta": None, "delta_color": "normal", 
         "icon": "⭐", "border_color": "#F4A261"},
        {"label": "平均单位成本", "value": f"${avg_cost:.2f}", 
         "delta": None, "delta_color": "normal", 
         "icon": "💰", "border_color": "#457B9D"},
    ])
    
    # =========================================================================
    # 图表区域
    # =========================================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 调拨流向图（出发仓库 → 目标仓库）
        flow_data = filtered.groupby(['出发仓库', '目标仓库']).agg({
            '可调拨数量': 'sum',
            '综合评分': 'mean'
        }).reset_index()
        flow_data['流向'] = flow_data['出发仓库'] + ' → ' + flow_data['目标仓库']
        flow_data = flow_data.sort_values('可调拨数量', ascending=True).tail(15)
        
        if len(flow_data) > 0:
            fig = px.bar(flow_data, x='可调拨数量', y='流向', orientation='h',
                         title='TOP15 调拨流向（按数量）',
                         color='综合评分', color_continuous_scale='Blues',
                         text='可调拨数量')
            fig.update_traces(textposition='outside', textfont_size=10)
            fig.update_layout(height=400, showlegend=False, yaxis_title='')
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("当前无可行调拨方案")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 综合评分分布
        if len(filtered) > 0:
            score_bins = [0, 0.1, 0.2, 0.3, 0.5, 1.0]
            score_labels = ['0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.5', '>0.5']
            filtered['评分区间'] = pd.cut(filtered['综合评分'], bins=score_bins, labels=score_labels, right=False)
            score_dist = filtered.groupby('评分区间', observed=False).size().reset_index(name='方案数')
            score_dist = score_dist.dropna(subset=['评分区间'])
            
            fig2 = px.bar(score_dist, x='评分区间', y='方案数',
                          title='调拨方案综合评分分布',
                          color='方案数', color_continuous_scale='Greens',
                          text='方案数')
            fig2.update_traces(textposition='outside')
            fig2.update_layout(height=400, showlegend=False, xaxis_title='综合评分区间', yaxis_title='')
            fig2 = apply_plotly_theme(fig2)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("无调拨数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 第二行图表
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 距离 vs 成本散点图（气泡大小=可调拨数量）
        if len(filtered) > 0:
            fig3 = px.scatter(filtered, x='距离km', y='调拨单位成本',
                              size='可调拨数量', color='综合评分',
                              color_continuous_scale='RdYlGn',
                              title='距离 vs 成本 vs 数量（气泡大小=数量）',
                              hover_data=['SKU编码', '出发仓库', '目标仓库', '需求数量'])
            fig3.update_layout(height=360, xaxis_title='距离（km）', yaxis_title='单位成本（$）')
            fig3 = apply_plotly_theme(fig3)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("无调拨数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 出发仓库→目标仓库 调拨数量热力图
        heatmap_data = filtered.groupby(['出发仓库', '目标仓库'])['可调拨数量'].sum().reset_index()
        if len(heatmap_data) > 0:
            heatmap_pivot = heatmap_data.pivot(index='出发仓库', columns='目标仓库', values='可调拨数量').fillna(0)
            
            fig4 = go.Figure(data=go.Heatmap(
                z=heatmap_pivot.values,
                x=heatmap_pivot.columns.tolist(),
                y=heatmap_pivot.index.tolist(),
                colorscale=[[0, '#E8F4F8'], [0.5, '#457B9D'], [1, '#1B4965']],
                showscale=True,
                colorbar=dict(title="数量", thickness=15),
                text=heatmap_pivot.values,
                texttemplate="%{text:.0f}",
                textfont_size=10
            ))
            fig4.update_layout(title='调拨数量热力图（出发→目标）', 
                               xaxis_title='目标仓库', yaxis_title='出发仓库',
                               height=360)
            fig4 = apply_plotly_theme(fig4)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("无调拨数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # 调拨建议明细表
    # =========================================================================
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h4 style="color: #1B4965; margin-top: 0;">📋 调拨建议明细（按优先级排序）</h4>
    </div>
    """, unsafe_allow_html=True)
    
    display_cols = ['出发仓库', '目标仓库', 'SKU编码', '距离km', '调拨单位成本',
                    '可调拨数量', '需求数量', '距离评分', '成本评分', '库存评分', '综合评分']
    
    if len(filtered) > 0:
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)
        
        # 统计摘要
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        with sum_col1:
            st.metric("总调拨距离", f"{filtered['距离km'].sum():,.0f} km")
        with sum_col2:
            st.metric("预计总成本", f"${(filtered['调拨单位成本'] * filtered['可调拨数量']).sum():,.2f}")
        with sum_col3:
            st.metric("平均距离", f"{filtered['距离km'].mean():.0f} km")
        with sum_col4:
            st.metric("最大综合评分", f"{filtered['综合评分'].max():.3f}")
    else:
        st.warning("⚠️ 当前筛选条件下无可行调拨方案，请放宽筛选条件")
    
    # =========================================================================
    # 决策模拟效果说明
    # =========================================================================
    st.markdown("""
    <div style="background: #F0F9FF; border-radius: 8px; padding: 16px; margin-top: 24px;
                border-left: 4px solid #1B4965;">
        <h5 style="color: #1B4965; margin-top: 0;">📊 调拨优先级模型说明</h5>
        <p style="color: #374151; font-size: 13px; margin-bottom: 8px;">
            综合评分 = 距离评分(30%) + 成本评分(35%) + 库存匹配评分(35%)
        </p>
        <ul style="color: #374151; font-size: 13px; margin-bottom: 0;">
            <li><b>距离优先</b>：优先选择距离近的仓库对，降低运输时效风险</li>
            <li><b>成本优先</b>：优先选择单位调拨成本低的方案，降低物流成本</li>
            <li><b>库存匹配优先</b>：优先选择可调拨数量与需求数量匹配度高的方案</li>
            <li><b>综合优先</b>：平衡距离、成本、库存三个维度的加权得分</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


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
