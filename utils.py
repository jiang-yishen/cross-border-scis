"""
跨境海外仓供应链智能决策系统 - 数据加载层
============================================
纯 JSON 缓存版本：所有页面数据预先计算并序列化为 JSON
云端部署时不再加载任何数据库/CSV，彻底解决内存溢出
"""
import os
import json
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DB_PATH = os.path.join(BASE_DIR, "data.db")

USE_SQLITE = os.path.exists(DB_PATH)


def _load_json_cache(filename):
    """加载 JSON 缓存文件"""
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


# =============================================================================
# 首页预计算缓存（~2KB）
# =============================================================================

@st.cache_data
def load_home_cache():
    cache = _load_json_cache("home_cache.json")
    return cache


# =============================================================================
# 辅助函数：从 JSON 构建 DataFrame
# =============================================================================

def _dict_to_df(data, dtype_map=None):
    """将字典列表转换为 DataFrame，可选类型映射"""
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    if dtype_map:
        for col, dtype in dtype_map.items():
            if col in df.columns:
                if dtype == 'datetime':
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                elif dtype == 'int':
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                elif dtype == 'float':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif dtype == 'str':
                    df[col] = df[col].astype(str)
    return df


# =============================================================================
# SKU / 仓库 元数据（小文件，直接加载）
# =============================================================================

@st.cache_data
def load_sku_master():
    # 尝试从缓存获取
    fc = _load_json_cache("forecast_cache.json")
    if fc and 'sku_list' in fc:
        return _dict_to_df([
            {"SKU编码": s} for s in fc['sku_list']
        ])
    # Fallback: 读 CSV
    df = pd.read_csv(os.path.join(DATA_DIR, "sku_master.csv"), encoding="utf-8-sig")
    df['上市日期'] = pd.to_datetime(df['上市日期'])
    return df


@st.cache_data
def load_warehouse_master():
    fc = _load_json_cache("replenishment_cache.json")
    if fc and 'warehouses' in fc:
        return _dict_to_df(fc['warehouses'])
    df = pd.read_csv(os.path.join(DATA_DIR, "warehouse_master.csv"), encoding="utf-8-sig")
    return df


# =============================================================================
# 需求预测页面数据（从 forecast_cache.json）
# =============================================================================

@st.cache_data
def load_demand_forecast():
    fc = _load_json_cache("forecast_cache.json")
    if fc and 'forecast' in fc:
        return _dict_to_df(fc['forecast'], {
            '日期': 'datetime', 'SKU编码': 'str', '品类': 'str',
            '预测销量': 'float', '预测下限': 'float', '预测上限': 'float', '集成预测': 'float'
        })
    # Fallback
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "demand_forecast.csv"), encoding="utf-8-sig")
    df['日期'] = pd.to_datetime(df['日期'])
    return df


@st.cache_data
def load_sales_daily():
    fc = _load_json_cache("forecast_cache.json")
    if fc and 'sales_recent' in fc:
        return _dict_to_df(fc['sales_recent'], {
            '日期': 'datetime', 'SKU编码': 'str', '仓库ID': 'str', '销售数量': 'int'
        })
    df = pd.read_csv(os.path.join(DATA_DIR, "sales_daily.csv"), encoding="utf-8-sig")
    df['日期'] = pd.to_datetime(df['日期'])
    return df


# =============================================================================
# 库存监控页面数据（从 inventory_cache.json）
# =============================================================================

@st.cache_data
def load_replenishment_plan():
    ic = _load_json_cache("inventory_cache.json")
    if ic:
        # 合并所有预警数据作为完整 replenishment_plan
        dfs = []
        for key in ['red_df', 'yellow_df', 'overage_df']:
            if key in ic and ic[key]:
                dfs.append(_dict_to_df(ic[key]))
        if dfs:
            return pd.concat(dfs, ignore_index=True).drop_duplicates(subset=['SKU编码', '仓库ID'])
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "replenishment_plan.csv"), encoding="utf-8-sig")
    return df


@st.cache_data
def load_inventory_snapshot():
    ic = _load_json_cache("inventory_cache.json")
    if ic and 'inv_wh' in ic:
        # 用仓库聚合数据反推（简化）
        return _dict_to_df(ic['inv_wh'], {'仓库ID': 'str', '总数量': 'int'})
    df = pd.read_csv(os.path.join(DATA_DIR, "inventory_snapshot.csv"), encoding="utf-8-sig")
    return df


# =============================================================================
# 补货计划页面数据（从 replenishment_cache.json）
# =============================================================================

@st.cache_data
def load_purchase_orders():
    rc = _load_json_cache("replenishment_cache.json")
    if rc:
        return _dict_to_df([], {'SKU编码': 'str'})  # 简化，物流页面用 logistics_cache
    df = pd.read_csv(os.path.join(DATA_DIR, "purchase_orders.csv"), encoding="utf-8-sig")
    df['下单日期'] = pd.to_datetime(df['下单日期'])
    df['预计到货日期'] = pd.to_datetime(df['预计到货日期'])
    return df


# =============================================================================
# 调拨建议页面数据（从 transfer_cache.json）
# =============================================================================

@st.cache_data
def load_transfer_recommendation():
    tc = _load_json_cache("transfer_cache.json")
    if tc and 'transfer' in tc:
        return _dict_to_df(tc['transfer'], {
            'SKU编码': 'str', '品类': 'str', '源仓库': 'str', '目标仓库': 'str',
            '调拨数量': 'int', '调拨成本': 'float', '优先级': 'int'
        })
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "transfer_recommendation.csv"), encoding="utf-8-sig")
    return df


# =============================================================================
# 物流跟踪页面数据（从 logistics_cache.json）
# =============================================================================

@st.cache_data
def load_logistics_tracking():
    lc = _load_json_cache("logistics_cache.json")
    if lc and 'logistics' in lc:
        return _dict_to_df(lc['logistics'], {
            'SKU编码': 'str', '仓库ID': 'str', '发货日期': 'datetime',
            '预计到达日期': 'datetime', '实际到达日期': 'datetime', '发货数量': 'int'
        })
    df = pd.read_csv(os.path.join(DATA_DIR, "logistics_tracking.csv"), encoding="utf-8-sig")
    df['发货日期'] = pd.to_datetime(df['发货日期'])
    df['预计到达日期'] = pd.to_datetime(df['预计到达日期'])
    df['实际到达日期'] = pd.to_datetime(df['实际到达日期'])
    return df


@st.cache_data
def load_inventory_health_report():
    df = pd.read_csv(os.path.join(OUTPUT_DIR, "inventory_health_report.csv"), encoding="utf-8-sig")
    return df


# =============================================================================
# 计算全局KPI（首页）
# =============================================================================

def compute_kpis():
    cache = load_home_cache()
    if cache and 'kpis' in cache:
        return cache['kpis']
    
    # Fallback: 动态计算
    sku_df = load_sku_master()
    sales_df = load_sales_daily()
    inv_df = load_inventory_snapshot()
    rep_df = load_replenishment_plan()
    po_df = load_purchase_orders()
    wh_df = load_warehouse_master()
    
    total_sku = len(sku_df)
    total_category = sku_df['品类'].nunique() if '品类' in sku_df.columns else 0
    
    total_revenue = 0
    if '销售数量' in sales_df.columns and '单价' in sku_df.columns:
        merged = sales_df.merge(sku_df[['SKU编码', '单价']], on='SKU编码', how='left')
        total_revenue = (merged['销售数量'] * merged['单价']).sum()
    
    total_inventory_value = 0
    if '总数量' in inv_df.columns and '单价' in inv_df.columns:
        total_inventory_value = (inv_df['总数量'] * inv_df['单价']).sum()
    
    red_alert = len(rep_df[rep_df['库存预警'] == '红色预警（需补货）']) if '库存预警' in rep_df.columns else 0
    yellow_alert = len(rep_df[rep_df['库存预警'] == '黄色预警（关注）']) if '库存预警' in rep_df.columns else 0
    overage_alert = len(rep_df[rep_df['库龄预警'] != '正常']) if '库龄预警' in rep_df.columns else 0
    in_transit_po = 0
    total_warehouse = len(wh_df)
    
    avg_daily_sales = sales_df['销售数量'].sum() / sales_df['日期'].nunique() if '销售数量' in sales_df.columns else 0
    total_qty = inv_df['总数量'].sum() if '总数量' in inv_df.columns else 0
    turnover_days = total_qty / avg_daily_sales if avg_daily_sales > 0 else 0
    stockout_risk = len(rep_df[rep_df['预计缺货天数'] < 7]) if '预计缺货天数' in rep_df.columns else 0
    
    return {
        'total_sku': int(total_sku),
        'total_category': int(total_category),
        'total_revenue': float(total_revenue),
        'total_inventory_value': float(total_inventory_value),
        'red_alert': int(red_alert),
        'yellow_alert': int(yellow_alert),
        'overage_alert': int(overage_alert),
        'in_transit_po': int(in_transit_po),
        'total_warehouse': int(total_warehouse),
        'turnover_days': round(turnover_days, 1),
        'stockout_risk': int(stockout_risk),
    }
