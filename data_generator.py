"""
跨境海外仓供应链智能决策系统 - 高保真业务模拟数据引擎
============================================================

功能：基于真实跨境电商业务规则，生成高保真模拟数据
数据表：
  1. warehouse_master.csv    - 仓库主数据
  2. sku_master.csv          - SKU主数据
  3. sales_daily.csv         - 日销售数据
  4. purchase_orders.csv     - 采购订单
  5. logistics_tracking.csv  - 物流跟踪
  6. inventory_snapshot.csv  - 库存快照

业务规则：
  - 6个海外仓（美国东/西岸、欧洲、英国、日本、东南亚）
  - 6大品类（服装鞋履、3C电子、家居、宠物用品、美妆个护、运动户外）
  - 24个月销售历史（2024.01-2025.12）
  - 品类差异化需求模式（季节性/生命周期/促销/复购）
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# =============================================================================
# 配置参数
# =============================================================================
CONFIG = {
    "start_date": "2024-01-01",
    "end_date": "2025-12-31",
    "random_seed": 42,
    "output_dir": "data",
}

# 品类配置（基于市场调研的真实分布）
CATEGORY_CONFIG = {
    "服装鞋履": {"sku_count": 280, "avg_price": 45, "avg_weight": 0.5, "lifecycle_months": 18, "seasonal_strength": 0.8, "return_rate": 0.15},
    "3C电子":   {"sku_count": 270, "avg_price": 120, "avg_weight": 0.8, "lifecycle_months": 12, "seasonal_strength": 0.3, "return_rate": 0.08},
    "家居用品":  {"sku_count": 180, "avg_price": 65, "avg_weight": 3.5, "lifecycle_months": 24, "seasonal_strength": 0.2, "return_rate": 0.05},
    "宠物用品":  {"sku_count": 110, "avg_price": 35, "avg_weight": 1.2, "lifecycle_months": 30, "seasonal_strength": 0.1, "return_rate": 0.02},
    "美妆个护":  {"sku_count": 100, "avg_price": 55, "avg_weight": 0.3, "lifecycle_months": 20, "seasonal_strength": 0.4, "return_rate": 0.10},
    "运动户外":  {"sku_count": 60,  "avg_price": 80, "avg_weight": 2.0, "lifecycle_months": 15, "seasonal_strength": 0.6, "return_rate": 0.12},
}

# 仓库配置
WAREHOUSES = [
    {"warehouse_id": "WH01", "warehouse_name": "美国东岸仓", "country": "美国", "region": "北美东部", "coverage": "美国东部/加拿大", "headway_days": 35, "last_mile_days": 4},
    {"warehouse_id": "WH02", "warehouse_name": "美国西岸仓", "country": "美国", "region": "北美西部", "coverage": "美国西部", "headway_days": 25, "last_mile_days": 4},
    {"warehouse_id": "WH03", "warehouse_name": "欧洲仓(荷兰)", "country": "荷兰", "region": "欧盟", "coverage": "欧盟国家", "headway_days": 40, "last_mile_days": 3},
    {"warehouse_id": "WH04", "warehouse_name": "英国仓", "country": "英国", "region": "欧洲", "coverage": "英国", "headway_days": 40, "last_mile_days": 2},
    {"warehouse_id": "WH05", "warehouse_name": "日本仓", "country": "日本", "region": "东亚", "coverage": "日本", "headway_days": 20, "last_mile_days": 2},
    {"warehouse_id": "WH06", "warehouse_name": "东南亚仓(新加坡)", "country": "新加坡", "region": "东南亚", "coverage": "东南亚国家", "headway_days": 12, "last_mile_days": 3},
]

# 节假日配置（影响销量的关键日期）
HOLIDAYS = {
    # 春节（销量下降）
    "2024-02-10": 0.3, "2024-02-11": 0.3, "2024-02-12": 0.3,
    "2025-01-29": 0.3, "2025-01-30": 0.3, "2025-01-31": 0.3,
    # 五一
    "2024-05-01": 0.5, "2025-05-01": 0.5,
    #  Prime Day / 618
    "2024-06-18": 1.5, "2024-07-16": 1.6, "2024-07-17": 1.6,
    "2025-06-18": 1.5, "2025-07-15": 1.6, "2025-07-16": 1.6,
    # 双11
    "2024-11-11": 1.8, "2025-11-11": 1.8,
    # 黑五 / 网一
    "2024-11-29": 2.0, "2024-11-30": 1.8, "2024-12-02": 1.7,
    "2025-11-28": 2.0, "2025-11-29": 1.8, "2025-12-01": 1.7,
    # 圣诞
    "2024-12-25": 1.3, "2025-12-25": 1.3,
    # 情人节
    "2024-02-14": 1.3, "2025-02-14": 1.3,
    # 母亲节
    "2024-05-12": 1.2, "2025-05-11": 1.2,
}


# =============================================================================
# 数据生成函数
# =============================================================================

def generate_warehouses(output_dir):
    """生成仓库主数据"""
    df = pd.DataFrame(WAREHOUSES)
    df.rename(columns={
        "warehouse_id": "仓库ID",
        "warehouse_name": "仓库名称",
        "country": "国家",
        "region": "区域",
        "coverage": "覆盖范围",
        "headway_days": "海运天数",
        "last_mile_days": "尾程天数",
    })    .to_csv(os.path.join(output_dir, "warehouse_master.csv"), index=False, encoding="utf-8-sig")
    print(f"✅ warehouse_master.csv: {len(df)} 个仓库")
    return df


def generate_skus(output_dir, total_skus=1000):
    """生成SKU主数据"""
    suppliers = [f"SUP{str(i).zfill(3)}" for i in range(1, 51)]
    sku_list = []
    sku_id = 1
    
    for cat_name, cfg in CATEGORY_CONFIG.items():
        count = int(total_skus * cfg["sku_count"] / 1000)
        for i in range(count):
            # 上市日期在24个月内均匀分布
            launch_offset = random.randint(0, 720)
            launch_date = datetime(2024, 1, 1) + timedelta(days=launch_offset)
            
            # 价格：对数正态分布（更真实的电商价格分布）
            price = max(5, np.random.lognormal(np.log(cfg["avg_price"]), 0.35))
            
            sku_list.append({
                "sku_id": f"SKU{str(sku_id).zfill(5)}",
                "sku_name": f"{cat_name}-商品{sku_id:04d}",
                "category": cat_name,
                "supplier_id": random.choice(suppliers),
                "unit_price": round(price, 2),
                "weight_kg": round(max(0.05, np.random.normal(cfg["avg_weight"], cfg["avg_weight"]*0.25)), 2),
                "launch_date": launch_date.strftime("%Y-%m-%d"),
                "lifecycle_months": cfg["lifecycle_months"],
                "seasonal_strength": cfg["seasonal_strength"],
                "return_rate": cfg["return_rate"],
                "moq": random.choice([50, 100, 200, 500]),
                "lead_time_days": random.randint(15, 55),
            })
            sku_id += 1
    
    df = pd.DataFrame(sku_list)
    df.rename(columns={
        "sku_id": "SKU编码",
        "sku_name": "SKU名称",
        "category": "品类",
        "supplier_id": "供应商ID",
        "unit_price": "单价",
        "weight_kg": "重量kg",
        "launch_date": "上市日期",
        "lifecycle_months": "生命周期月数",
        "seasonal_strength": "季节性强度",
        "return_rate": "退货率",
        "moq": "最小起订量",
        "lead_time_days": "采购提前期天数",
    })    .to_csv(os.path.join(output_dir, "sku_master.csv"), index=False, encoding="utf-8-sig")
    print(f"✅ sku_master.csv: {len(df)} 个SKU")
    print("   品类分布:", dict(df["category"].value_counts()))
    return df


def get_seasonal_factor(cat, month, seasonal_str):
    """根据品类和月份计算季节性因子"""
    if cat == "服装鞋履":
        # 夏季(6-8)和冬季(11-1)双峰
        return 1 + seasonal_str * (0.6 * np.sin(2 * np.pi * (month - 2) / 12))
    elif cat == "3C电子":
        return 1 + seasonal_str * (0.5 if month in [8, 9, 11, 12] else -0.1)
    elif cat == "宠物用品":
        return 1 + seasonal_str * (0.3 if month == 12 else 0.05)
    elif cat == "美妆个护":
        return 1 + seasonal_str * (0.6 if month in [2, 5, 11] else -0.05)
    elif cat == "运动户外":
        return 1 + seasonal_str * (0.5 if month in [3, 4, 5, 9, 10] else -0.2)
    else:
        return 1.0  # 家居用品季节性弱


def generate_sales(output_dir, df_skus, df_warehouses, chunk_size=200):
    """生成日销售数据（分批处理以避免内存溢出）"""
    date_range = pd.date_range(start=CONFIG["start_date"], end=CONFIG["end_date"], freq="D")
    wh_ids = df_warehouses["warehouse_id"].tolist()
    
    print(f"📅 生成销售数据: {len(date_range)} 天 ({date_range[0].date()} ~ {date_range[-1].date()})")
    
    all_sales = []
    total_skus = len(df_skus)
    
    for idx, (_, sku) in enumerate(df_skus.iterrows()):
        if idx % 100 == 0:
            print(f"   进度: {idx}/{total_skus} SKU...")
        
        cat = sku["category"]
        launch = datetime.strptime(sku["launch_date"], "%Y-%m-%d")
        lifecycle = sku["lifecycle_months"]
        seasonal_str = sku["seasonal_strength"]
        return_rate = sku["return_rate"]
        
        # 基础日销量：大部分SKU日销低，少数爆款高（对数正态分布）
        base_demand = max(0.5, np.random.lognormal(2.0, 1.3))
        
        # 每个SKU分配到2-4个仓库
        num_wh = random.randint(2, min(4, len(wh_ids)))
        assigned_warehouses = random.sample(wh_ids, k=num_wh)
        
        # 生成仓库销量份额（美国仓库销量更高）
        wh_shares = []
        for wh in assigned_warehouses:
            if wh in ["WH01", "WH02"]:
                wh_shares.append(random.uniform(0.25, 0.45))
            elif wh in ["WH03", "WH04"]:
                wh_shares.append(random.uniform(0.15, 0.25))
            else:
                wh_shares.append(random.uniform(0.08, 0.18))
        # 归一化
        total_share = sum(wh_shares)
        wh_shares = [s / total_share for s in wh_shares]
        
        # 为该SKU生成所有日期的销售
        sku_sales = []
        for date in date_range:
            if date < launch:
                continue
            
            # 生命周期因子
            months_since = (date - launch).days / 30
            if months_since < 2:
                lifecycle_f = 0.2 + 0.8 * (months_since / 2)  # 新品爬坡
            elif months_since < lifecycle * 0.5:
                lifecycle_f = 1.0  # 稳定期
            elif months_since < lifecycle * 0.75:
                lifecycle_f = 0.85  # 成熟期微降
            else:
                lifecycle_f = max(0.15, 0.85 - 0.03 * (months_since - lifecycle * 0.75))  # 衰退
            
            # 季节性 + 节假日 + 周末
            month = date.month
            seasonal_f = get_seasonal_factor(cat, month, seasonal_str)
            holiday_f = HOLIDAYS.get(date.strftime("%Y-%m-%d"), 1.0)
            weekend_f = 1.15 if date.weekday() >= 5 and cat in ["服装鞋履", "美妆个护"] else 1.0
            noise = np.random.lognormal(0, 0.25)
            
            demand = base_demand * lifecycle_f * seasonal_f * holiday_f * weekend_f * noise
            demand = max(0, int(round(demand)))
            
            if demand > 0:
                for wh, share in zip(assigned_warehouses, wh_shares):
                    wh_demand = max(0, int(demand * share * random.uniform(0.85, 1.15)))
                    if wh_demand > 0:
                        sku_sales.append({
                            "date": date.strftime("%Y-%m-%d"),
                            "sku_id": sku["sku_id"],
                            "warehouse_id": wh,
                            "units_sold": wh_demand,
                            "units_returned": max(0, int(wh_demand * return_rate * random.uniform(0.3, 1.5))),
                        })
        
        all_sales.extend(sku_sales)
    
    df = pd.DataFrame(all_sales)
    df.rename(columns={
        "date": "日期",
        "sku_id": "SKU编码",
        "warehouse_id": "仓库ID",
        "units_sold": "销售数量",
        "units_returned": "退货数量",
    })    .to_csv(os.path.join(output_dir, "sales_daily.csv"), index=False, encoding="utf-8-sig")
    print(f"✅ sales_daily.csv: {len(df):,} 条记录")
    return df


def generate_purchase_orders(output_dir, df_skus, df_warehouses):
    """生成采购订单数据"""
    wh_ids = df_warehouses["warehouse_id"].tolist()
    po_records = []
    po_id = 1
    
    for _, sku in df_skus.iterrows():
        launch = datetime.strptime(sku["launch_date"], "%Y-%m-%d")
        po_start = max(datetime(2024, 1, 1), launch - timedelta(days=random.randint(20, 45)))
        
        current_date = po_start
        while current_date <= datetime(2025, 12, 31):
            qty = sku["moq"] * random.randint(2, 10)
            lead_time = sku["lead_time_days"] + random.randint(12, 45)
            eta = current_date + timedelta(days=lead_time)
            
            # 根据ETA判断状态
            if eta < datetime(2025, 5, 1):
                status = "已完成"
            elif eta < datetime(2025, 9, 1):
                status = random.choice(["已完成", "已完成", "部分到货", "在途"])
            elif eta < datetime(2025, 11, 1):
                status = random.choice(["在途", "部分到货", "已完成"])
            else:
                status = random.choice(["在途", "待发货", "已下单"])
            
            po_records.append({
                "po_id": f"PO{str(po_id).zfill(6)}",
                "sku_id": sku["sku_id"],
                "supplier_id": sku["supplier_id"],
                "warehouse_id": random.choice(wh_ids),
                "order_date": current_date.strftime("%Y-%m-%d"),
                "qty_ordered": qty,
                "qty_received": qty if status == "已完成" else int(qty * random.uniform(0, 0.95)),
                "unit_cost": round(sku["unit_price"] * random.uniform(0.35, 0.65), 2),
                "eta_date": eta.strftime("%Y-%m-%d"),
                "status": status,
            })
            po_id += 1
            current_date += timedelta(days=random.randint(25, 55))
    
    df = pd.DataFrame(po_records)
    df.rename(columns={
        "po_id": "采购订单ID",
        "sku_id": "SKU编码",
        "supplier_id": "供应商ID",
        "warehouse_id": "仓库ID",
        "order_date": "下单日期",
        "qty_ordered": "订购数量",
        "qty_received": "到货数量",
        "unit_cost": "单位成本",
        "eta_date": "预计到货日期",
        "status": "订单状态",
    })    .to_csv(os.path.join(output_dir, "purchase_orders.csv"), index=False, encoding="utf-8-sig")
    print(f"✅ purchase_orders.csv: {len(df):,} 条记录")
    return df


def generate_logistics(output_dir, df_pos):
    """生成物流跟踪数据"""
    route_map = {
        "WH01": "中国港口→洛杉矶/长滩港→美国清关→卡车运输→海外仓",
        "WH02": "中国港口→洛杉矶/长滩港→美国清关→卡车运输→海外仓",
        "WH03": "中国港口→鹿特丹港→欧盟清关→卡车运输→海外仓",
        "WH04": "中国港口→费利克斯托港→英国清关→卡车运输→海外仓",
        "WH05": "中国港口→横滨港→日本清关→卡车运输→海外仓",
        "WH06": "中国港口→新加坡港→东盟清关→卡车运输→海外仓",
    }
    
    logistics = []
    for _, po in df_pos.iterrows():
        if po["status"] == "已下单":
            continue
        
        wh = po["warehouse_id"]
        eta_dt = datetime.strptime(po["eta_date"], "%Y-%m-%d")
        
        if po["status"] in ["已完成", "部分到货"]:
            actual = (eta_dt + timedelta(days=random.randint(-5, 12))).strftime("%Y-%m-%d")
            status = "已入库"
        else:
            actual = None
            status = random.choice(["运输中", "清关中", "已到达目的港"])
        
        logistics.append({
            "tracking_id": f"TRK{po['po_id']}",
            "po_id": po["po_id"],
            "sku_id": po["sku_id"],
            "warehouse_id": wh,
            "route": route_map.get(wh, "中国港口→目的港→清关→海外仓"),
            "ship_date": po["order_date"],
            "eta_date": po["eta_date"],
            "actual_arrival": actual,
            "status": status,
            "carrier": random.choice(["COSCO", "MSC", "Maersk", " Evergreen", "ONE"]),
        })
    
    df = pd.DataFrame(logistics)
    df.rename(columns={
        "tracking_id": "物流单号",
        "po_id": "采购订单ID",
        "sku_id": "SKU编码",
        "warehouse_id": "仓库ID",
        "route": "运输路线",
        "ship_date": "发货日期",
        "eta_date": "预计到达日期",
        "actual_arrival": "实际到达日期",
        "status": "物流状态",
        "carrier": "承运商",
    })    .to_csv(os.path.join(output_dir, "logistics_tracking.csv"), index=False, encoding="utf-8-sig")
    print(f"✅ logistics_tracking.csv: {len(df):,} 条记录")
    return df


def generate_inventory_snapshot(output_dir, df_skus, df_warehouses, df_sales, df_pos):
    """生成库存快照（截至2025-12-31）"""
    wh_ids = df_warehouses["warehouse_id"].tolist()
    inventory = []
    
    # 预计算各SKU-仓库的销量和收货量
    sales_agg = df_sales.groupby(["sku_id", "warehouse_id"])["units_sold"].sum().to_dict()
    received_agg = df_pos[df_pos["status"].isin(["已完成", "部分到货"])].groupby(["sku_id", "warehouse_id"])["qty_received"].sum().to_dict()
    transit_agg = df_pos[df_pos["status"] == "在途"].groupby(["sku_id", "warehouse_id"])["qty_ordered"].sum().to_dict()
    
    # 近30天销量（用于计算安全库存）
    recent_sales = df_sales[df_sales["date"] >= "2025-12-01"].groupby(["sku_id", "warehouse_id"])["units_sold"].sum().to_dict()
    
    for _, sku in df_skus.iterrows():
        for wh in wh_ids:
            key = (sku["sku_id"], wh)
            total_sold = sales_agg.get(key, 0)
            total_received = received_agg.get(key, 0)
            in_transit = transit_agg.get(key, 0)
            
            # 当前库存 = 总收货 - 总销售 + 随机调整（模拟盘点差异、损耗等）
            on_hand = max(0, total_received - total_sold + random.randint(-15, 30))
            
            # 安全库存：基于近30天日均销量 × 15天
            recent = recent_sales.get(key, 0)
            safety = max(5, int((recent / 30) * 15))
            
            inventory.append({
                "sku_id": sku["sku_id"],
                "warehouse_id": wh,
                "on_hand": on_hand,
                "in_transit": in_transit,
                "reserved": int(on_hand * random.uniform(0.05, 0.15)),
                "available": max(0, on_hand - int(on_hand * 0.1)),
                "safety_stock": safety,
                "reorder_point": int(safety * 1.5),
                "max_stock": int(safety * 4),
                "snapshot_date": "2025-12-31",
            })
    
    df = pd.DataFrame(inventory)
    df.rename(columns={
        "sku_id": "SKU编码",
        "warehouse_id": "仓库ID",
        "on_hand": "在库数量",
        "in_transit": "在途数量",
        "reserved": "预留数量",
        "available": "可用数量",
        "safety_stock": "安全库存",
        "reorder_point": "再订货点",
        "max_stock": "最大库存",
        "snapshot_date": "快照日期",
    })    .to_csv(os.path.join(output_dir, "inventory_snapshot.csv"), index=False, encoding="utf-8-sig")
    print(f"✅ inventory_snapshot.csv: {len(df):,} 条记录")
    return df


# =============================================================================
# 主函数
# =============================================================================

def main(ctx):
    np.random.seed(CONFIG["random_seed"])
    random.seed(CONFIG["random_seed"])
    
    run_dir = ctx["runDir"]
    output_dir = os.path.join(run_dir, CONFIG["output_dir"])
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*60)
    print("🚀 跨境海外仓供应链智能决策系统 - 数据生成引擎")
    print("="*60)
    
    # Step 1: 仓库主数据
    df_wh = generate_warehouses(output_dir)
    
    # Step 2: SKU主数据
    df_skus = generate_skus(output_dir, total_skus=1000)
    
    # Step 3: 日销售数据
    df_sales = generate_sales(output_dir, df_skus, df_wh)
    
    # Step 4: 采购订单
    df_pos = generate_purchase_orders(output_dir, df_skus, df_wh)
    
    # Step 5: 物流跟踪
    df_logistics = generate_logistics(output_dir, df_pos)
    
    # Step 6: 库存快照
    df_inventory = generate_inventory_snapshot(output_dir, df_skus, df_wh, df_sales, df_pos)
    
    # 验证统计
    print("\n" + "="*60)
    print("📊 数据生成完成！统计概览")
    print("="*60)
    
    # 销售额估算
    df_sales_price = df_sales.merge(df_skus[["sku_id", "unit_price"]], on="sku_id")
    total_revenue = (df_sales_price["units_sold"] * df_sales_price["unit_price"]).sum()
    
    stats = {
        "warehouse_count": len(df_wh),
        "sku_count": len(df_skus),
        "sales_records": len(df_sales),
        "sales_date_range": f"{df_sales['date'].min()} ~ {df_sales['date'].max()}",
        "po_records": len(df_pos),
        "logistics_records": len(df_logistics),
        "inventory_records": len(df_inventory),
        "estimated_revenue_usd": round(total_revenue, 2),
    }
    
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    print("\n📁 输出文件:")
    for f in os.listdir(output_dir):
        fp = os.path.join(output_dir, f)
        size = os.path.getsize(fp)
        print(f"  {f} ({size/1024:.1f} KB)")
    
    return {
        "status": "success",
        "output_dir": output_dir,
        "stats": stats,
    }
