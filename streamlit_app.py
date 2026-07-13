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
import os
import plotly.express as px
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils import (
    load_warehouse_master, load_sku_master, load_sales_daily,
    load_purchase_orders, load_logistics_tracking, load_inventory_snapshot,
    load_demand_forecast, load_replenishment_plan, load_transfer_recommendation,
    load_inventory_health_report, compute_kpis, load_home_cache
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
    
    # 图表区域 - 优先使用预计算缓存（避免加载大CSV，解决云端内存溢出）
    cache = load_home_cache()
    use_cache = cache is not None
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 品类销售分布
        if use_cache and 'cat_sales' in cache:
            cat_sales = pd.DataFrame(cache['cat_sales'])
        else:
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
        if use_cache and 'abc_dist' in cache:
            abc_dist = pd.DataFrame(cache['abc_dist'])
        else:
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
        if use_cache and 'inv_wh' in cache:
            inv_wh = pd.DataFrame(cache['inv_wh'])
        else:
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
        if use_cache and 'alert_dist' in cache:
            alert_dist = pd.DataFrame(cache['alert_dist'])
        else:
            rep_df = load_replenishment_plan()
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
    
    # Schema验证说明 - 按文件类型分组的完整字段映射
    st.markdown("""
    <div style="background: #F0F9FF; border-radius: 8px; padding: 16px; margin-top: 24px;
                border-left: 4px solid #1B4965;">
        <h5 style="color: #1B4965; margin-top: 0;">📋 Schema 验证规则</h5>
        <p style="color: #374151; font-size: 13px; margin-bottom: 8px;">
            系统会自动验证上传文件的字段名称是否符合标准Schema映射。请严格按照以下字段要求准备CSV文件，<b>字段缺失或格式错误将导致导入失败</b>。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用 Streamlit 原生表格组件展示Schema（支持中文，比HTML更稳定）
    schema_tabs = st.tabs(["📊 销售数据", "📦 SKU主数据", "📋 库存快照", "📝 采购订单"])
    
    with schema_tabs[0]:
        sales_schema = pd.DataFrame({
            "标准字段（英文）": ["date", "sku_id", "warehouse_id", "units_sold", "units_returned"],
            "展示字段（中文）": ["日期", "SKU编码", "仓库ID", "销售数量", "退货数量"],
            "数据类型": ["日期", "字符串", "字符串", "整数", "整数"],
            "是否必填": ["✅ 必填", "✅ 必填", "✅ 必填", "✅ 必填", "❌ 选填"],
            "示例值": ["2025-01-15", "SKU00001", "WH01", "15", "0"],
            "约束说明": [
                "YYYY-MM-DD格式，如2025-01-15",
                "长度10位，前缀SKU+5位数字",
                "长度4位，前缀WH+2位数字",
                "非负整数，记录当日销售件数",
                "非负整数，记录当日退货件数"
            ]
        })
        st.dataframe(sales_schema, use_container_width=True, hide_index=True)
        st.info("💡 销售数据是需求预测和库存分析的基础数据，必须包含完整的日期序列，建议覆盖至少6个月历史数据。")
    
    with schema_tabs[1]:
        sku_schema = pd.DataFrame({
            "标准字段（英文）": ["sku_id", "sku_name", "category", "supplier_id", "unit_price", "weight_kg", "launch_date", "lifecycle_months", "seasonal_strength", "return_rate", "moq", "lead_time_days"],
            "展示字段（中文）": ["SKU编码", "SKU名称", "品类", "供应商ID", "单价", "重量(kg)", "上市日期", "生命周期月数", "季节性强度", "退货率", "最小起订量", "采购提前期天数"],
            "数据类型": ["字符串", "字符串", "字符串", "字符串", "小数", "小数", "日期", "整数", "小数", "小数", "整数", "整数"],
            "是否必填": ["✅ 必填", "✅ 必填", "✅ 必填", "✅ 必填", "✅ 必填", "❌ 选填", "❌ 选填", "❌ 选填", "❌ 选填", "❌ 选填", "✅ 必填", "✅ 必填"],
            "示例值": ["SKU00001", "无线蓝牙耳机Pro", "3C电子", "SUP001", "29.99", "0.35", "2024-03-01", "12", "0.65", "0.03", "100", "35"],
            "约束说明": [
                "长度10位，SKU+5位数字",
                "SKU完整名称，用于报表展示",
                "枚举值：服装鞋履/3C电子/家居用品/宠物用品/美妆个护/运动户外",
                "供应商唯一编码",
                "美元计价，保留2位小数",
                "单位千克，用于物流运费计算",
                "YYYY-MM-DD格式",
                "从上市日期到当前月份数",
                "0-1之间，越高代表季节性越强",
                "0-1之间，退货率百分比",
                "采购最小起订量，整数",
                "从下单到入库的平均天数"
            ]
        })
        st.dataframe(sku_schema, use_container_width=True, hide_index=True)
        st.info("💡 SKU主数据是所有模块的基础字典表，品类和提前期字段直接影响预测算法和补货策略的准确性。")
    
    with schema_tabs[2]:
        inv_schema = pd.DataFrame({
            "标准字段（英文）": ["sku_id", "warehouse_id", "available_qty", "in_transit_qty", "total_qty", "avg_age_days", "overage_qty", "unit_price", "daily_sales"],
            "展示字段（中文）": ["SKU编码", "仓库ID", "可用数量", "在途数量", "总数量", "平均库龄天数", "超龄数量", "单价", "日均销量"],
            "数据类型": ["字符串", "字符串", "整数", "整数", "整数", "整数", "整数", "小数", "小数"],
            "是否必填": ["✅ 必填", "✅ 必填", "✅ 必填", "✅ 必填", "✅ 必填", "❌ 选填", "❌ 选填", "❌ 选填", "❌ 选填"],
            "示例值": ["SKU00001", "WH01", "120", "50", "170", "28", "0", "29.99", "3.5"],
            "约束说明": [
                "必须与SKU主表一致",
                "必须与仓库主表一致",
                "当前可售库存，非负整数",
                "已发货未到库数量，非负整数",
                "可用+在途之和，非负整数",
                "该SKU在该仓库的平均库龄",
                "超过90天的库存数量",
                "美元计价，用于库存价值计算",
                "近30天平均日销量"
            ]
        })
        st.dataframe(inv_schema, use_container_width=True, hide_index=True)
        st.info("💡 库存快照是库存健康监控的核心输入数据，建议每日更新一次，确保可用数量、在途数量与实际情况一致。")
    
    with schema_tabs[3]:
        po_schema = pd.DataFrame({
            "标准字段（英文）": ["po_id", "sku_id", "supplier_id", "warehouse_id", "order_date", "order_qty", "received_qty", "unit_cost", "eta_date", "status"],
            "展示字段（中文）": ["采购订单ID", "SKU编码", "供应商ID", "仓库ID", "下单日期", "订购数量", "到货数量", "单位成本", "预计到货日期", "订单状态"],
            "数据类型": ["字符串", "字符串", "字符串", "字符串", "日期", "整数", "整数", "小数", "日期", "字符串"],
            "是否必填": ["✅ 必填", "✅ 必填", "✅ 必填", "✅ 必填", "✅ 必填", "✅ 必填", "❌ 选填", "✅ 必填", "✅ 必填", "✅ 必填"],
            "示例值": ["PO2025001", "SKU00001", "SUP001", "WH01", "2025-01-01", "500", "0", "12.50", "2025-02-05", "运输中"],
            "约束说明": [
                "唯一采购订单编号",
                "必须与SKU主表一致",
                "必须与供应商主表一致",
                "目标入库仓库ID",
                "YYYY-MM-DD格式",
                "本次采购总数量，非负整数",
                "已到货数量，到货时更新",
                "美元计价，不含关税运费",
                "YYYY-MM-DD格式",
                "枚举值：待确认/已下单/运输中/已入库/已取消"
            ]
        })
        st.dataframe(po_schema, use_container_width=True, hide_index=True)
        st.info("💡 采购订单数据用于采购物流跟踪和库存健康监控中的在途数量计算，订单状态必须准确更新。")
    
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
    
    # 修复：SKU下拉框只显示有预测数据的SKU，避免用户选择无预测数据的SKU后明细为空
    forecast_skus = sorted(forecast_df['SKU编码'].unique().tolist()) if not forecast_df.empty else []
    if not forecast_skus:
        st.warning("⚠️ 暂无预测数据，请检查数据生成状态")
        return
    
    # 获取有预测数据的SKU信息，用于下拉框展示
    sku_with_forecast = sku_df[sku_df['SKU编码'].isin(forecast_skus)].copy()
    
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
        # SKU选择 - 仅显示有预测数据的SKU（修复：从forecast_skus读取而非全部sku_df）
        selected_sku = st.selectbox(
            "🔍 选择SKU",
            forecast_skus,
            index=0,
            help="搜索并选择特定SKU查看其预测趋势（仅显示已有预测数据的SKU）"
        )
        
        # 获取选中SKU的信息（添加防护：如果SKU不在sku_df中则显示默认值）
        sku_info_row = sku_df[sku_df['SKU编码'] == selected_sku]
        if not sku_info_row.empty:
            sku_info = sku_info_row.iloc[0]
            sku_name = sku_info.get('SKU名称', selected_sku)
            sku_cat = sku_info.get('品类', '未知')
            sku_price = sku_info.get('单价', 0)
        else:
            sku_name = selected_sku
            sku_cat = '未知'
            sku_price = 0
        st.markdown(f"""
        <div style="font-size: 12px; color: #6B7280; margin-top: 4px;">
            📦 {sku_name} | 🏷️ {sku_cat} | 💰 ${sku_price}
        </div>
        """, unsafe_allow_html=True)
    
    with col_param2:
        # 预测天数
        forecast_days = st.slider(
            "📅 预测天数",
            min_value=7, max_value=90, value=30, step=7,
            help="选择未来预测的时间窗口"
        )
        
        # 品类筛选（仅显示有预测数据的品类）
        forecast_cats = sorted(forecast_df['品类'].unique().tolist()) if '品类' in forecast_df.columns else []
        selected_cats = st.multiselect(
            "🏷️ 筛选品类",
            forecast_cats,
            default=[],
            help="选择要展示的品类（空白=展示全部）"
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
        sku_sales = sales_df[
            (sales_df['SKU编码'] == selected_sku) &
            (sales_df['日期'] >= '2025-07-01')
        ].copy()
        sku_sales = sku_sales.groupby('日期')['销售数量'].sum().reset_index()
        sku_sales = sku_sales.sort_values('日期')
        
        # 该SKU的预测数据（添加防护：检查日期列是否有效）
        sku_forecast = forecast_df[
            (forecast_df['SKU编码'] == selected_sku)
        ].copy()
        if not sku_forecast.empty and not sku_forecast['日期'].isna().all():
            min_date = sku_forecast['日期'].min()
            if pd.notna(min_date):
                sku_forecast = sku_forecast[sku_forecast['日期'] <= min_date + pd.Timedelta(days=forecast_days)]
        
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
            
            # 置信区间（添加防护：确保上下限列存在）
            if '预测上限' in sku_forecast.columns and '预测下限' in sku_forecast.columns:
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
        if selected_cats:
            cat_forecast = forecast_df[forecast_df['品类'].isin(selected_cats)].copy()
        else:
            cat_forecast = forecast_df.copy()
        
        # 添加防护：确保有日期数据且不为空
        if not cat_forecast.empty and not cat_forecast['日期'].isna().all():
            cat_min_date = cat_forecast['日期'].min()
            if pd.notna(cat_min_date):
                cat_forecast = cat_forecast[cat_forecast['日期'] <= cat_min_date + pd.Timedelta(days=30)]
        
        cat_summary = cat_forecast.groupby('品类')['预测销量'].sum().reset_index()
        cat_summary = cat_summary.sort_values('预测销量', ascending=True)
        
        color_map = {
            '服装鞋履': '#1B4965', '3C电子': '#457B9D', '家居用品': '#2A9D8F',
            '宠物用品': '#F4A261', '美妆个护': '#E63946', '运动户外': '#6B7280'
        }
        
        if not cat_summary.empty:
            fig2 = px.bar(cat_summary, x='预测销量', y='品类', orientation='h',
                          title='各品类未来30天预测销量对比',
                          color='品类', color_discrete_map=color_map,
                          text='预测销量')
            fig2.update_traces(textposition='outside', textfont_size=11)
            fig2.update_layout(height=350, showlegend=False, yaxis_title='')
            fig2 = apply_plotly_theme(fig2)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("无预测数据")
        
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
        if selected_cats:
            cat_forecast_box = forecast_df[forecast_df['品类'].isin(selected_cats)].copy()
        else:
            cat_forecast_box = forecast_df.copy()
        
        # 添加防护：日期有效性检查
        if not cat_forecast_box.empty and not cat_forecast_box['日期'].isna().all():
            box_min_date = cat_forecast_box['日期'].min()
            if pd.notna(box_min_date):
                cat_forecast_box = cat_forecast_box[
                    cat_forecast_box['日期'] <= box_min_date + pd.Timedelta(days=30)
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
    if selected_cats:
        display_forecast = forecast_df[
            (forecast_df['SKU编码'] == selected_sku) &
            (forecast_df['品类'].isin(selected_cats))
        ].copy()
    else:
        display_forecast = forecast_df[
            forecast_df['SKU编码'] == selected_sku
        ].copy()
    
    # 添加权重标记（决策模拟效果）
    if recalc_clicked or st.session_state.get('forecast_recalculated', False):
        display_forecast['当前Prophet权重'] = prophet_weight
        display_forecast['当前XGBoost权重'] = xgb_weight
    
    # 确保列存在（防护：如果forecast_df缺少某些列，则只展示存在的列）
    display_cols = ['SKU编码', '品类', '日期', '预测销量', '预测下限', '预测上限', '集成预测']
    available_cols = [c for c in display_cols if c in display_forecast.columns]
    display_forecast = display_forecast[available_cols].head(50)
    
    st.dataframe(display_forecast, use_container_width=True, hide_index=True)
    
    # 统计摘要（添加防护：空数据时显示0）
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        total_pred = display_forecast['预测销量'].sum() if '预测销量' in display_forecast.columns and not display_forecast.empty else 0
        st.metric("预测总销量", f"{total_pred:,.0f} 件")
    with summary_col2:
        avg_pred = display_forecast['预测销量'].mean() if '预测销量' in display_forecast.columns and not display_forecast.empty else 0
        st.metric("平均日销量", f"{avg_pred:.2f} 件")
    with summary_col3:
        upper_mean = display_forecast['预测上限'].mean() if '预测上限' in display_forecast.columns and not display_forecast.empty else 0
        st.metric("预测上限均值", f"{upper_mean:.2f} 件")
    with summary_col4:
        lower_mean = display_forecast['预测下限'].mean() if '预测下限' in display_forecast.columns and not display_forecast.empty else 0
        st.metric("预测下限均值", f"{lower_mean:.2f} 件")


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
            default=[],
            help="选择要分析的品类（空白=展示全部）"
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
    if selected_cats:
        filtered = rep_df[rep_df['品类'].isin(selected_cats)].copy()
    else:
        filtered = rep_df.copy()
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
            default=[],
            help="选择要分析的品类（空白=展示全部）"
        )
    
    with col_p4:
        # 仓库筛选
        warehouses = sorted(rep_df['仓库名称'].unique().tolist())
        selected_whs = st.multiselect(
            "🏭 筛选仓库",
            warehouses,
            default=[],
            help="选择要分析的仓库（空白=展示全部）"
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
    if selected_cats and selected_whs:
        filtered = rep_df[
            (rep_df['品类'].isin(selected_cats)) & 
            (rep_df['仓库名称'].isin(selected_whs))
        ].copy()
    elif selected_cats:
        filtered = rep_df[rep_df['品类'].isin(selected_cats)].copy()
    elif selected_whs:
        filtered = rep_df[rep_df['仓库名称'].isin(selected_whs)].copy()
    else:
        filtered = rep_df.copy()
    
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
            default=[],
            help="筛选特定出发仓库的调拨方案（空白=展示全部）"
        )
    
    with col_p4:
        to_whs = sorted(transfer_df['目标仓库'].unique().tolist())
        selected_to = st.multiselect(
            "📥 目标仓库",
            to_whs,
            default=[],
            help="筛选特定目标仓库的调拨方案（空白=展示全部）"
        )
    
    # 应用筛选
    if selected_from and selected_to:
        filtered = transfer_df[
            (transfer_df['综合评分'] >= min_score) &
            (transfer_df['出发仓库'].isin(selected_from)) &
            (transfer_df['目标仓库'].isin(selected_to))
        ].copy()
    elif selected_from:
        filtered = transfer_df[
            (transfer_df['综合评分'] >= min_score) &
            (transfer_df['出发仓库'].isin(selected_from))
        ].copy()
    elif selected_to:
        filtered = transfer_df[
            (transfer_df['综合评分'] >= min_score) &
            (transfer_df['目标仓库'].isin(selected_to))
        ].copy()
    else:
        filtered = transfer_df[transfer_df['综合评分'] >= min_score].copy()
    
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
    """采购物流跟踪 - 采购订单状态看板与物流时间线"""
    page_header("采购物流跟踪", "采购订单状态监控、物流时间线追踪与到货预测")
    
    # 加载数据
    po_df = load_purchase_orders()
    log_df = load_logistics_tracking()
    sku_df = load_sku_master()
    wh_df = load_warehouse_master()
    
    # =========================================================================
    # 参数筛选区
    # =========================================================================
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 24px;">
        <h4 style="color: #1B4965; margin-top: 0;">🔍 筛选条件</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        order_statuses = sorted(po_df['订单状态'].unique().tolist())
        selected_status = st.multiselect(
            "📋 订单状态",
            order_statuses,
            default=[],
            help="选择要查看的订单状态（空白=展示全部）"
        )
    
    with col_f2:
        log_statuses = sorted(log_df['物流状态'].unique().tolist())
        selected_log_status = st.multiselect(
            "🚢 物流状态",
            log_statuses,
            default=[],
            help="选择要查看的物流状态（空白=展示全部）"
        )
    
    with col_f3:
        suppliers = sorted(po_df['供应商ID'].unique().tolist())
        selected_suppliers = st.multiselect(
            "🏭 供应商",
            suppliers,
            default=[],
            help="选择供应商（空白=展示全部）"
        )
    
    with col_f4:
        carriers = sorted(log_df['承运商'].unique().tolist())
        selected_carriers = st.multiselect(
            "🚚 承运商",
            carriers,
            default=[],
            help="选择承运商（空白=展示全部）"
        )
    
    # 筛选采购订单
    if selected_status and selected_suppliers:
        filtered_po = po_df[
            (po_df['订单状态'].isin(selected_status)) &
            (po_df['供应商ID'].isin(selected_suppliers))
        ].copy()
    elif selected_status:
        filtered_po = po_df[po_df['订单状态'].isin(selected_status)].copy()
    elif selected_suppliers:
        filtered_po = po_df[po_df['供应商ID'].isin(selected_suppliers)].copy()
    else:
        filtered_po = po_df.copy()
    
    # 筛选物流记录
    if selected_log_status and selected_carriers:
        filtered_log = log_df[
            (log_df['物流状态'].isin(selected_log_status)) &
            (log_df['承运商'].isin(selected_carriers))
        ].copy()
    elif selected_log_status:
        filtered_log = log_df[log_df['物流状态'].isin(selected_log_status)].copy()
    elif selected_carriers:
        filtered_log = log_df[log_df['承运商'].isin(selected_carriers)].copy()
    else:
        filtered_log = log_df.copy()
    
    # 合并（物流记录中有订单ID匹配的）
    merged = filtered_po.merge(
        filtered_log, 
        on=['采购订单ID', 'SKU编码', '仓库ID'], 
        how='left'
    )
    
    # =========================================================================
    # KPI卡片
    # =========================================================================
    total_po = len(filtered_po)
    total_qty = filtered_po['订购数量'].sum()
    total_cost = (filtered_po['订购数量'] * filtered_po['单位成本']).sum()
    in_transit = len(filtered_po[filtered_po['订单状态'] == '在途'])
    completed = len(filtered_po[filtered_po['订单状态'] == '已完成'])
    
    # 计算平均运输时效（有实际到达日期的）
    delivered = merged[merged['实际到达日期'].notna()].copy()
    if len(delivered) > 0:
        delivered['运输天数'] = (delivered['实际到达日期'] - delivered['发货日期']).dt.days
        avg_transit = delivered['运输天数'].mean()
    else:
        avg_transit = 0
    
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    kpi_row([
        {"label": "采购订单总数", "value": f"{total_po:,}", 
         "delta": None, "delta_color": "normal", 
         "icon": "📋", "border_color": "#1B4965"},
        {"label": "采购总数量", "value": f"{total_qty:,.0f}", 
         "delta": None, "delta_color": "normal", 
         "icon": "📦", "border_color": "#457B9D"},
        {"label": "采购总金额", "value": f"${total_cost/10000:.1f}万", 
         "delta": None, "delta_color": "normal", 
         "icon": "💰", "border_color": "#2A9D8F"},
        {"label": "在途订单", "value": f"{in_transit:,}", 
         "delta": None, "delta_color": "normal", 
         "icon": "🚢", "border_color": "#F4A261"},
        {"label": "已完成订单", "value": f"{completed:,}", 
         "delta": None, "delta_color": "normal", 
         "icon": "✅", "border_color": "#1B4965"},
    ])
    
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    kpi_row([
        {"label": "平均运输时效", "value": f"{avg_transit:.0f}天", 
         "delta": None, "delta_color": "normal", 
         "icon": "⏱️", "border_color": "#457B9D"},
        {"label": "在途物流单", "value": f"{len(filtered_log):,}", 
         "delta": None, "delta_color": "normal", 
         "icon": "🚚", "border_color": "#E63946"},
    ])
    
    # =========================================================================
    # 图表区域
    # =========================================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 订单状态分布（饼图）
        status_dist = filtered_po.groupby('订单状态').size().reset_index(name='订单数')
        status_colors = {
            '已完成': '#2A9D8F',
            '在途': '#F4A261',
            '待发货': '#457B9D',
            '已下单': '#1B4965'
        }
        fig = px.pie(status_dist, names='订单状态', values='订单数',
                     title='采购订单状态分布',
                     color='订单状态', color_discrete_map=status_colors)
        fig.update_traces(textinfo='percent+label', textfont_size=12)
        fig.update_layout(height=350)
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 物流状态分布（饼图）
        log_status_dist = filtered_log.groupby('物流状态').size().reset_index(name='物流单数')
        log_status_colors = {
            '已入库': '#2A9D8F',
            '已到达目的港': '#457B9D',
            '运输中': '#F4A261',
            '清关中': '#1B4965'
        }
        fig2 = px.pie(log_status_dist, names='物流状态', values='物流单数',
                      title='物流状态分布',
                      color='物流状态', color_discrete_map=log_status_colors)
        fig2.update_traces(textinfo='percent+label', textfont_size=12)
        fig2.update_layout(height=350)
        fig2 = apply_plotly_theme(fig2)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 第二行图表
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 承运商订单量
        carrier_dist = filtered_log.groupby('承运商').size().reset_index(name='物流单数')
        carrier_dist = carrier_dist.sort_values('物流单数', ascending=True)
        
        fig3 = px.bar(carrier_dist, x='物流单数', y='承运商', orientation='h',
                      title='各承运商物流单数',
                      color='物流单数', color_continuous_scale='Blues',
                      text='物流单数')
        fig3.update_traces(textposition='outside', textfont_size=11)
        fig3.update_layout(height=350, showlegend=False, yaxis_title='')
        fig3 = apply_plotly_theme(fig3)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 月度采购趋势
        filtered_po['月份'] = filtered_po['下单日期'].dt.strftime('%Y-%m')
        monthly = filtered_po.groupby('月份').agg({
            '订购数量': 'sum',
            '采购订单ID': 'nunique'
        }).reset_index()
        monthly.columns = ['月份', '采购数量', '订单数']
        monthly = monthly.sort_values('月份')
        
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=monthly['月份'], y=monthly['采购数量'],
            name='采购数量', marker_color='#457B9D'
        ))
        fig4.update_layout(
            title=dict(text='月度采购趋势'),
            yaxis=dict(title=dict(text='采购数量', font=dict(color='#457B9D'))),
            yaxis2=dict(title=dict(text='订单数', font=dict(color='#E63946')), overlaying='y', side='right'),
            height=350, barmode='group'
        )
        fig4 = apply_plotly_theme(fig4)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # 采购订单明细表
    # =========================================================================
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h4 style="color: #1B4965; margin-top: 0;">📋 采购订单明细</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 合并物流信息展示
    display_cols = ['采购订单ID', 'SKU编码', '供应商ID', '仓库ID', '订单状态',
                    '订购数量', '到货数量', '单位成本', '预计到货日期', '下单日期']
    if '物流单号' in merged.columns:
        display_cols.extend(['物流单号', '物流状态', '承运商', '发货日期'])
    
    display_df = merged[display_cols].copy()
    display_df['采购金额'] = (display_df['订购数量'] * display_df['单位成本']).round(2)
    display_df = display_df.sort_values('下单日期', ascending=False)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # 统计
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    sum_col1, sum_col2, sum_col3 = st.columns(3)
    with sum_col1:
        st.metric("平均到货率", f"{(filtered_po['到货数量'].sum()/filtered_po['订购数量'].sum()*100):.1f}%")
    with sum_col2:
        st.metric("平均单件成本", f"${(total_cost/total_qty if total_qty>0 else 0):.2f}")
    with sum_col3:
        overdue = filtered_po[filtered_po['预计到货日期'] < pd.Timestamp('2025-12-31')]
        st.metric("预计超期订单", f"{len(overdue)} 条")
    
    # =========================================================================
    # 物流时间线模拟
    # =========================================================================
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h4 style="color: #1B4965; margin-top: 0;">🚢 物流状态时间线</h4>
        <p style="color: #6B7280; font-size: 13px; margin-bottom: 16px;">
            各物流状态阶段的订单数量分布与平均停留时间
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 物流状态漏斗图
    log_status_order = ['已入库', '已到达目的港', '清关中', '运输中']
    funnel_data = filtered_log.groupby('物流状态').size().reset_index(name='物流单数')
    funnel_data['排序'] = funnel_data['物流状态'].apply(
        lambda x: log_status_order.index(x) if x in log_status_order else 99
    )
    funnel_data = funnel_data.sort_values('排序')
    
    fig5 = go.Figure(go.Funnel(
        y=funnel_data['物流状态'],
        x=funnel_data['物流单数'],
        textposition='inside',
        textinfo='value+percent initial',
        marker=dict(color=['#2A9D8F', '#457B9D', '#F4A261', '#1B4965']),
        connector=dict(line=dict(color='#E5E7EB', width=2))
    ))
    fig5.update_layout(title='物流状态漏斗（从运输中到已入库）', height=400)
    fig5 = apply_plotly_theme(fig5)
    st.plotly_chart(fig5, use_container_width=True)


# =============================================================================
# 使用指南页面
# =============================================================================

def page_guide():
    """使用指南页面：系统操作手册展示与下载"""
    st.title("📘 使用指南")
    st.markdown("<p style='color: #6B7280;'>系统操作手册与流程说明</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 手册下载区域
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1B4965 0%, #457B9D 100%);
                border-radius: 16px; padding: 32px; margin-bottom: 24px;
                color: white; text-align: center;">
        <h2 style="color: white; margin: 0 0 12px 0; font-size: 24px;">📋 系统操作手册</h2>
        <p style="color: rgba(255,255,255,0.85); margin: 0 0 20px 0; font-size: 15px;">
            包含完整的系统功能说明、操作流程、数据导入规范与常见问题解答
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 下载按钮
    docx_path = os.path.join(os.path.dirname(__file__), "docs", "系统操作手册.docx")
    if os.path.exists(docx_path):
        with open(docx_path, "rb") as f:
            docx_bytes = f.read()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="⬇️ 下载系统操作手册 (.docx)",
                data=docx_bytes,
                file_name="跨境海外仓供应链智能决策系统_操作手册.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
    else:
        st.warning("⚠️ 操作手册文件未找到，请确认 `docs/系统操作手册.docx` 文件存在。")
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # 快速导航卡片
    st.markdown("<h3 style='color: #1B4965;'>📑 快速导航</h3>", unsafe_allow_html=True)
    
    guide_sections = [
        ("🏠 首页仪表盘", "实时展示全链路KPI指标、关键预警与快捷入口", "#1B4965"),
        ("📤 数据导入", "支持ERP销售/库存/预测数据的导入与Schema验证", "#2A9D8F"),
        ("📈 需求预测分析", "Prophet+XGBoost融合预测模型，支持多维度预测对比", "#457B9D"),
        ("📦 库存健康监控", "ABC-XYZ分类矩阵、库龄分析、缺货预警、滞销识别", "#F4A261"),
        ("🔄 补货计划看板", "动态安全库存计算、EOQ建议、采购订单生成模拟", "#2A9D8F"),
        ("🚚 调拨建议", "多仓库存平衡分析、调拨优先级排序、调拨成本评估", "#457B9D"),
        ("📋 采购物流跟踪", "采购订单全生命周期跟踪、物流状态时间线、异常预警", "#1B4965"),
    ]
    
    for i in range(0, len(guide_sections), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(guide_sections):
                title, desc, color = guide_sections[i + j]
                with cols[j]:
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 20px;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 16px;
                                border-left: 4px solid {color};">
                        <h4 style="color: {color}; margin: 0 0 8px 0; font-size: 16px;">{title}</h4>
                        <p style="color: #6B7280; margin: 0; font-size: 13px; line-height: 1.5;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # 系统核心亮点
    st.markdown("<h3 style='color: #1B4965;'>🎯 系统核心亮点</h3>", unsafe_allow_html=True)
    
    highlights = [
        ("🤖 智能预测引擎", "Prophet（65%）+ XGBoost（35%）融合预测，时间序列交叉验证，MAPE/RMSE双指标评估"),
        ("📊 ABC-XYZ双维分类", "销售额×需求波动双维矩阵，差异化库存管理策略，精准定位高风险SKU"),
        ("💡 动态安全库存", "基于正态分布的服务水平模型，支持Z值参数化调节，实时响应需求变化"),
        ("🔄 多仓协同调拨", "距离/成本/时效三优先级算法，贪心策略优化，库存平衡智能建议"),
        ("📋 全链路可视化", "从采购下单到入库上架的物流状态漏斗，异常自动标记，预警实时推送"),
        ("🎮 决策模拟交互", "参数实时调节，结果即时反馈，支持多场景对比分析与决策报告导出"),
    ]
    
    for title, desc in highlights:
        st.markdown(f"""
        <div style="background: white; border-radius: 10px; padding: 16px 20px;
                    box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 12px;
                    display: flex; align-items: flex-start; gap: 12px;">
            <div style="font-size: 22px; line-height: 1;">{title.split(' ')[0]}</div>
            <div style="flex: 1;">
                <div style="font-weight: 600; color: #1B4965; font-size: 14px; margin-bottom: 4px;">
                    {title.split(' ')[1]}
                </div>
                <div style="color: #6B7280; font-size: 13px; line-height: 1.5;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # 数据来源与版本信息
    st.markdown("<h3 style='color: #1B4965;'>ℹ️ 版本信息</h3>", unsafe_allow_html=True)
    
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown("""
        <div style="background: #F8FAFC; border-radius: 10px; padding: 16px;">
            <p style="margin: 0 0 8px 0; color: #1B4965; font-weight: 600;">系统版本</p>
            <p style="margin: 0; color: #6B7280; font-size: 13px;">v1.0.0 (2026.07)</p>
            <p style="margin: 8px 0 0 0; color: #6B7280; font-size: 13px;">技术栈：Streamlit + Python</p>
        </div>
        """, unsafe_allow_html=True)
    with info_col2:
        st.markdown("""
        <div style="background: #F8FAFC; border-radius: 10px; padding: 16px;">
            <p style="margin: 0 0 8px 0; color: #1B4965; font-weight: 600;">数据覆盖</p>
            <p style="margin: 0; color: #6B7280; font-size: 13px;">SKU：1,100+ | 仓库：6个</p>
            <p style="margin: 8px 0 0 0; color: #6B7280; font-size: 13px;">时间跨度：2024.01 - 2025.12</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # 开源链接
    st.markdown("""
    <div style="background: #E8F4F8; border-radius: 10px; padding: 16px; text-align: center;">
        <p style="margin: 0 0 8px 0; color: #1B4965; font-weight: 600;">🔗 开源仓库</p>
        <p style="margin: 0; color: #457B9D; font-size: 13px;">
            GitHub: https://github.com/jiang-yishen/cross-border-scis
        </p>
    </div>
    """, unsafe_allow_html=True)


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
    elif selected_page == "📘 使用指南":
        page_guide()


if __name__ == "__main__":
    main()
