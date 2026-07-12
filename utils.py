"""
跨境海外仓供应链智能决策系统 - 数据加载层
============================================
统一封装所有数据文件的读取，处理中文表头，提供缓存。
优化：使用 dtype 优化 + Parquet 优先（云端内存友好）
"""
import os
import pandas as pd
import streamlit as st

# 项目根目录（streamlit_app.py 同级）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def _read_sales():
    """优先读取 Parquet（体积小、加载快），否则回退到 CSV"""
    parquet_path = os.path.join(DATA_DIR, "sales_daily.parquet")
    csv_path = os.path.join(DATA_DIR, "sales_daily.csv")
    if os.path.exists(parquet_path):
        return pd.read_parquet(parquet_path)
    # 读取 CSV 时指定 dtype 减少内存
    return pd.read_csv(
        csv_path, encoding="utf-8-sig",
        dtype={"SKU编码": "string", "仓库ID": "string", "销售数量": "int32"}
    )


@st.cache_data
def load_warehouse_master():
    """仓库主数据"""
    df = pd.read_csv(os.path.join(DATA_DIR, "warehouse_master.csv"), encoding="utf-8-sig")
    return df


@st.cache_data
def load_sku_master():
    """SKU主数据"""
    df = pd.read_csv(os.path.join(DATA_DIR, "sku_master.csv"), encoding="utf-8-sig",
                     dtype={"SKU编码": "string", "品类": "category"})
    df['上市日期'] = pd.to_datetime(df['上市日期'])
    return df


@st.cache_data
def load_sales_daily():
    """日销售数据 - dtype 优化减少内存"""
    df = _read_sales()
    df['日期'] = pd.to_datetime(df['日期'])
    return df


@st.cache_data
def load_purchase_orders():
    """采购订单"""
    df = pd.read_csv(os.path.join(DATA_DIR, "purchase_orders.csv"), encoding="utf-8-sig",
                     dtype={"SKU编码": "string", "仓库ID": "string"})
    df['下单日期'] = pd.to_datetime(df['下单日期'])
    df['预计到货日期'] = pd.to_datetime(df['预计到货日期'])
    return df


@st.cache_data
def load_logistics_tracking():
    """物流跟踪"""
    df = pd.read_csv(os.path.join(DATA_DIR, "logistics_tracking.csv"), encoding="utf-8-sig",
                     dtype={"SKU编码": "string", "仓库ID": "string"})
    df['发货日期'] = pd.to_datetime(df['发货日期'])
    df['预计到达日期'] = pd.to_datetime(df['预计到达日期'])
    df['实际到达日期'] = pd.to_datetime(df['实际到达日期'])
    return df


@st.cache_data
def load_inventory_snapshot():
    """库存快照"""
    df = pd.read_csv(os.path.join(DATA_DIR, "inventory_snapshot.csv"), encoding="utf-8-sig",
                     dtype={"SKU编码": "string", "仓库ID": "string"})
    return df


@st.cache_data
def load_demand_forecast():
    """需求预测结果"""
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "demand_forecast.csv"), encoding="utf-8-sig",
                     dtype={"SKU编码": "string", "品类": "category"})
    df['日期'] = pd.to_datetime(df['日期'])
    return df


@st.cache_data
def load_replenishment_plan():
    """补货计划"""
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "replenishment_plan.csv"), encoding="utf-8-sig",
                     dtype={"SKU编码": "string", "品类": "category", "仓库ID": "string"})
    return df


@st.cache_data
def load_transfer_recommendation():
    """调拨建议"""
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "transfer_recommendation.csv"), encoding="utf-8-sig",
                     dtype={"SKU编码": "string", "品类": "category"})
    return df


@st.cache_data
def load_inventory_health_report():
    """库存健康报告"""
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "inventory_health_report.csv"), encoding="utf-8-sig")
    return df


# =============================================================================
# 计算全局KPI（用于首页仪表盘）
# =============================================================================

def compute_kpis():
    """计算全局关键指标"""
    sku_df = load_sku_master()
    sales_df = load_sales_daily()
    inv_df = load_inventory_snapshot()
    rep_df = load_replenishment_plan()
    po_df = load_purchase_orders()
    wh_df = load_warehouse_master()
    
    # 1. 总SKU数 & 品类数
    total_sku = len(sku_df)
    total_category = sku_df['品类'].nunique()
    
    # 2. 总销售额（估算）
    merged = sales_df.merge(sku_df[['SKU编码', '单价']], on='SKU编码', how='left')
    total_revenue = (merged['销售数量'] * merged['单价']).sum()
    
    # 3. 总库存价值
    total_inventory_value = (inv_df['总数量'] * inv_df['单价']).sum()
    
    # 4. 预警统计
    red_alert = len(rep_df[rep_df['库存预警'] == '红色预警（需补货）'])
    yellow_alert = len(rep_df[rep_df['库存预警'] == '黄色预警（关注）'])
    overage_alert = len(rep_df[rep_df['库龄预警'] != '正常'])
    
    # 5. 在途采购订单
    in_transit_po = len(po_df[po_df['订单状态'] == '运输中'])
    
    # 6. 仓库数
    total_warehouse = len(wh_df)
    
    # 7. 平均库存周转天数（简化：总库存 / 日均销量）
    avg_daily_sales = sales_df['销售数量'].sum() / sales_df['日期'].nunique()
    total_qty = inv_df['总数量'].sum()
    turnover_days = total_qty / avg_daily_sales if avg_daily_sales > 0 else 0
    
    # 8. 缺货风险SKU数（预计缺货天数 < 7天）
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
