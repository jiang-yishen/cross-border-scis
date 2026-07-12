"""
跨境海外仓供应链智能决策系统 - 数据加载层
============================================
统一封装所有数据文件的读取，处理中文表头，提供缓存。
优化：SQLite 数据库替代 CSV（云端内存友好，按需查询）
关键修复：SQLite 读取后强制转换正确的数据类型
"""
import os
import json
import sqlite3
import pandas as pd
import streamlit as st

# 项目根目录（streamlit_app.py 同级）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DB_PATH = os.path.join(BASE_DIR, "data.db")

USE_SQLITE = os.path.exists(DB_PATH)


def _get_conn():
    """获取 SQLite 连接"""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# =============================================================================
# 首页预计算缓存（最快，无需任何数据库查询）
# =============================================================================

@st.cache_data
def load_home_cache():
    """加载首页预计算缓存（~2KB，无需加载任何大文件）"""
    cache_path = os.path.join(BASE_DIR, "home_cache.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


# =============================================================================
# SQLite 查询函数（云端优先）- 强制类型转换修复
# =============================================================================

@st.cache_data
def load_warehouse_master_sql():
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM warehouse_master", conn)
    conn.close()
    return df


@st.cache_data
def load_sku_master_sql():
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM sku_master", conn)
    conn.close()
    df['上市日期'] = pd.to_datetime(df['上市日期'])
    # 类型转换
    df['SKU编码'] = df['SKU编码'].astype(str)
    df['品类'] = df['品类'].astype(str)
    df['单价'] = pd.to_numeric(df['单价'], errors='coerce')
    return df


@st.cache_data
def load_sales_daily_sql(sku_id=None, days=60):
    """日销售数据 - 按需查询，只加载需要的 SKU 和天数"""
    conn = _get_conn()
    if sku_id:
        df = pd.read_sql_query(
            "SELECT * FROM sales_daily WHERE SKU编码 = ? ORDER BY 日期 DESC LIMIT ?",
            conn, params=(sku_id, days * 10)
        )
    else:
        df = pd.read_sql_query("SELECT * FROM sales_daily", conn)
    conn.close()
    df['日期'] = pd.to_datetime(df['日期'])
    # 类型转换
    df['SKU编码'] = df['SKU编码'].astype(str)
    df['仓库ID'] = df['仓库ID'].astype(str)
    df['销售数量'] = pd.to_numeric(df['销售数量'], errors='coerce').fillna(0).astype(int)
    return df


@st.cache_data
def load_purchase_orders_sql():
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM purchase_orders", conn)
    conn.close()
    df['下单日期'] = pd.to_datetime(df['下单日期'])
    df['预计到货日期'] = pd.to_datetime(df['预计到货日期'])
    # 类型转换
    df['SKU编码'] = df['SKU编码'].astype(str)
    df['仓库ID'] = df['仓库ID'].astype(str)
    df['采购数量'] = pd.to_numeric(df['采购数量'], errors='coerce').fillna(0).astype(int)
    df['采购单价'] = pd.to_numeric(df['采购单价'], errors='coerce')
    return df


@st.cache_data
def load_logistics_tracking_sql():
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM logistics_tracking", conn)
    conn.close()
    df['发货日期'] = pd.to_datetime(df['发货日期'])
    df['预计到达日期'] = pd.to_datetime(df['预计到达日期'])
    df['实际到达日期'] = pd.to_datetime(df['实际到达日期'])
    # 类型转换
    df['SKU编码'] = df['SKU编码'].astype(str)
    df['仓库ID'] = df['仓库ID'].astype(str)
    df['发货数量'] = pd.to_numeric(df['发货数量'], errors='coerce').fillna(0).astype(int)
    return df


@st.cache_data
def load_inventory_snapshot_sql():
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM inventory_snapshot", conn)
    conn.close()
    # 类型转换
    df['SKU编码'] = df['SKU编码'].astype(str)
    df['仓库ID'] = df['仓库ID'].astype(str)
    df['总数量'] = pd.to_numeric(df['总数量'], errors='coerce').fillna(0).astype(int)
    df['可用数量'] = pd.to_numeric(df['可用数量'], errors='coerce').fillna(0).astype(int)
    df['在途数量'] = pd.to_numeric(df['在途数量'], errors='coerce').fillna(0).astype(int)
    df['单价'] = pd.to_numeric(df['单价'], errors='coerce')
    return df


@st.cache_data
def load_demand_forecast_sql():
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM demand_forecast", conn)
    conn.close()
    df['日期'] = pd.to_datetime(df['日期'])
    # 类型转换
    df['SKU编码'] = df['SKU编码'].astype(str)
    df['品类'] = df['品类'].astype(str)
    df['预测销量'] = pd.to_numeric(df['预测销量'], errors='coerce').fillna(0)
    df['预测下限'] = pd.to_numeric(df['预测下限'], errors='coerce').fillna(0)
    df['预测上限'] = pd.to_numeric(df['预测上限'], errors='coerce').fillna(0)
    df['集成预测'] = pd.to_numeric(df['集成预测'], errors='coerce').fillna(0)
    return df


@st.cache_data
def load_replenishment_plan_sql():
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM replenishment_plan", conn)
    conn.close()
    # 类型转换
    df['SKU编码'] = df['SKU编码'].astype(str)
    df['品类'] = df['品类'].astype(str)
    df['仓库ID'] = df['仓库ID'].astype(str)
    df['仓库名称'] = df['仓库名称'].astype(str)
    df['ABC分类'] = df['ABC分类'].astype(str)
    df['XYZ分类'] = df['XYZ分类'].astype(str)
    df['总数量'] = pd.to_numeric(df['总数量'], errors='coerce').fillna(0).astype(int)
    df['可用数量'] = pd.to_numeric(df['可用数量'], errors='coerce').fillna(0).astype(int)
    df['安全库存'] = pd.to_numeric(df['安全库存'], errors='coerce').fillna(0).astype(int)
    df['再订货点'] = pd.to_numeric(df['再订货点'], errors='coerce').fillna(0).astype(int)
    df['经济订货量'] = pd.to_numeric(df['经济订货量'], errors='coerce').fillna(0).astype(int)
    df['最小起订量'] = pd.to_numeric(df['最小起订量'], errors='coerce').fillna(0).astype(int)
    df['日均销量'] = pd.to_numeric(df['日均销量'], errors='coerce').fillna(0)
    df['预计缺货天数'] = pd.to_numeric(df['预计缺货天数'], errors='coerce').fillna(0)
    df['单价'] = pd.to_numeric(df['单价'], errors='coerce')
    df['平均库龄天数'] = pd.to_numeric(df['平均库龄天数'], errors='coerce').fillna(0)
    df['超龄数量'] = pd.to_numeric(df['超龄数量'], errors='coerce').fillna(0).astype(int)
    return df


@st.cache_data
def load_transfer_recommendation_sql():
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM transfer_recommendation", conn)
    conn.close()
    # 类型转换
    df['SKU编码'] = df['SKU编码'].astype(str)
    df['品类'] = df['品类'].astype(str)
    df['源仓库'] = df['源仓库'].astype(str)
    df['目标仓库'] = df['目标仓库'].astype(str)
    df['调拨数量'] = pd.to_numeric(df['调拨数量'], errors='coerce').fillna(0).astype(int)
    df['调拨成本'] = pd.to_numeric(df['调拨成本'], errors='coerce').fillna(0)
    df['优先级'] = pd.to_numeric(df['优先级'], errors='coerce').fillna(0).astype(int)
    return df


@st.cache_data
def load_inventory_health_report_sql():
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM inventory_health_report", conn)
    conn.close()
    return df


# =============================================================================
# CSV 回退函数（本地开发用，当 SQLite 不存在时）
# =============================================================================

@st.cache_data
def load_warehouse_master():
    if USE_SQLITE:
        return load_warehouse_master_sql()
    df = pd.read_csv(os.path.join(DATA_DIR, "warehouse_master.csv"), encoding="utf-8-sig")
    return df


@st.cache_data
def load_sku_master():
    if USE_SQLITE:
        return load_sku_master_sql()
    df = pd.read_csv(os.path.join(DATA_DIR, "sku_master.csv"), encoding="utf-8-sig")
    df['上市日期'] = pd.to_datetime(df['上市日期'])
    return df


@st.cache_data
def load_sales_daily():
    if USE_SQLITE:
        return load_sales_daily_sql()
    df = pd.read_csv(os.path.join(DATA_DIR, "sales_daily.csv"), encoding="utf-8-sig")
    df['日期'] = pd.to_datetime(df['日期'])
    return df


@st.cache_data
def load_purchase_orders():
    if USE_SQLITE:
        return load_purchase_orders_sql()
    df = pd.read_csv(os.path.join(DATA_DIR, "purchase_orders.csv"), encoding="utf-8-sig")
    df['下单日期'] = pd.to_datetime(df['下单日期'])
    df['预计到货日期'] = pd.to_datetime(df['预计到货日期'])
    return df


@st.cache_data
def load_logistics_tracking():
    if USE_SQLITE:
        return load_logistics_tracking_sql()
    df = pd.read_csv(os.path.join(DATA_DIR, "logistics_tracking.csv"), encoding="utf-8-sig")
    df['发货日期'] = pd.to_datetime(df['发货日期'])
    df['预计到达日期'] = pd.to_datetime(df['预计到达日期'])
    df['实际到达日期'] = pd.to_datetime(df['实际到达日期'])
    return df


@st.cache_data
def load_inventory_snapshot():
    if USE_SQLITE:
        return load_inventory_snapshot_sql()
    df = pd.read_csv(os.path.join(DATA_DIR, "inventory_snapshot.csv"), encoding="utf-8-sig")
    return df


@st.cache_data
def load_demand_forecast():
    if USE_SQLITE:
        return load_demand_forecast_sql()
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "demand_forecast.csv"), encoding="utf-8-sig")
    df['日期'] = pd.to_datetime(df['日期'])
    return df


@st.cache_data
def load_replenishment_plan():
    if USE_SQLITE:
        return load_replenishment_plan_sql()
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "replenishment_plan.csv"), encoding="utf-8-sig")
    return df


@st.cache_data
def load_transfer_recommendation():
    if USE_SQLITE:
        return load_transfer_recommendation_sql()
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "transfer_recommendation.csv"), encoding="utf-8-sig")
    return df


@st.cache_data
def load_inventory_health_report():
    if USE_SQLITE:
        return load_inventory_health_report_sql()
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "inventory_health_report.csv"), encoding="utf-8-sig")
    return df


# =============================================================================
# 计算全局KPI（用于首页仪表盘）
# =============================================================================

def compute_kpis():
    """计算全局关键指标 - 优先使用预计算缓存（避免云端内存溢出）"""
    cache = load_home_cache()
    if cache and 'kpis' in cache:
        return cache['kpis']
    
    # Fallback: 动态计算（仅本地开发时使用）
    sku_df = load_sku_master()
    sales_df = load_sales_daily()
    inv_df = load_inventory_snapshot()
    rep_df = load_replenishment_plan()
    po_df = load_purchase_orders()
    wh_df = load_warehouse_master()
    
    total_sku = len(sku_df)
    total_category = sku_df['品类'].nunique()
    merged = sales_df.merge(sku_df[['SKU编码', '单价']], on='SKU编码', how='left')
    total_revenue = (merged['销售数量'] * merged['单价']).sum()
    total_inventory_value = (inv_df['总数量'] * inv_df['单价']).sum()
    red_alert = len(rep_df[rep_df['库存预警'] == '红色预警（需补货）'])
    yellow_alert = len(rep_df[rep_df['库存预警'] == '黄色预警（关注）'])
    overage_alert = len(rep_df[rep_df['库龄预警'] != '正常'])
    in_transit_po = len(po_df[po_df['订单状态'] == '运输中'])
    total_warehouse = len(wh_df)
    avg_daily_sales = sales_df['销售数量'].sum() / sales_df['日期'].nunique()
    total_qty = inv_df['总数量'].sum()
    turnover_days = total_qty / avg_daily_sales if avg_daily_sales > 0 else 0
    stockout_risk = len(rep_df[rep_df['预计缺货天数'] < 7])
    
    return {
        'total_sku': total_sku,
        'total_category': total_category,
        'total_revenue': total_revenue,
        'total_inventory_value': total_inventory_value,
        'red_alert': red_alert,
        'yellow_alert': yellow_alert,
        'overage_alert': overage_alert,
        'in_transit_po': in_transit_po,
        'total_warehouse': total_warehouse,
        'turnover_days': round(turnover_days, 1),
        'stockout_risk': stockout_risk,
    }
