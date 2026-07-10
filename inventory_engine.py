# ============================================================
# 模块3：智能补货与多仓调拨引擎
# 功能：ABC-XYZ分类、安全库存、ROP、EOQ、库存预警、调拨建议
# ============================================================

import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_inventory_snapshot(sku_df, wh_df, sales_df):
    """生成各仓库存快照（模拟真实库存分布）"""
    warehouses = wh_df['warehouse_id'].tolist()
    wh_names = dict(zip(wh_df['warehouse_id'], wh_df['warehouse_name']))

    recent_sales = sales_df[sales_df['date'] >= '2025-10-01'].copy()
    daily_demand = recent_sales.groupby(['sku_id', 'warehouse_id'])['units_sold'].mean().reset_index()
    daily_demand.rename(columns={'units_sold': 'avg_units_sold'}, inplace=True)

    np.random.seed(42)
    inventory_records = []

    for _, sku in sku_df.iterrows():
        sku_id = sku['sku_id']
        category = sku['category']
        lead_time = sku['lead_time_days']
        unit_price = sku['unit_price']

        for wh in warehouses:
            dd = daily_demand[(daily_demand['sku_id'] == sku_id) & (daily_demand['warehouse_id'] == wh)]
            avg_sales = dd['avg_units_sold'].values[0] if len(dd) > 0 else 0.5

            coverage_days = np.random.choice([15, 30, 45, 60, 90], p=[0.1, 0.25, 0.35, 0.2, 0.1])
            available_qty = max(0, int(avg_sales * coverage_days * np.random.uniform(0.5, 1.5)))
            in_transit_qty = max(0, int(avg_sales * lead_time * np.random.uniform(0.3, 1.2))) if np.random.random() > 0.3 else 0

            if category in ['服装鞋履', '美妆个护']:
                avg_age = np.random.exponential(25)
            elif category in ['3C电子', '运动户外']:
                avg_age = np.random.exponential(45)
            else:
                avg_age = np.random.exponential(55)
            avg_age = min(int(avg_age), 200)

            threshold_map = {'服装鞋履': 45, '3C电子': 60, '家居用品': 60, '宠物用品': 60, '美妆个护': 45, '运动户外': 60}
            threshold = threshold_map.get(category, 60)
            overage_ratio = np.random.uniform(0.1, 0.4) if avg_age > threshold else 0.0
            overage_qty = int(available_qty * overage_ratio)

            inventory_records.append({
                'sku_id': sku_id, 'warehouse_id': wh,
                'available_qty': available_qty, 'in_transit_qty': in_transit_qty,
                'total_qty': available_qty + in_transit_qty,
                'avg_age_days': avg_age, 'overage_qty': overage_qty,
                'unit_price': unit_price, 'avg_units_sold': round(avg_sales, 2)
            })

    return pd.DataFrame(inventory_records)


def generate_transfer_cost_matrix(wh_df):
    """生成仓间调拨成本矩阵"""
    distance_matrix = {
        ('WH01', 'WH02'): 4000, ('WH01', 'WH03'): 6000, ('WH01', 'WH04'): 5500,
        ('WH01', 'WH05'): 11000, ('WH01', 'WH06'): 15000,
        ('WH02', 'WH03'): 9000, ('WH02', 'WH04'): 8500, ('WH02', 'WH05'): 8000,
        ('WH02', 'WH06'): 13000, ('WH03', 'WH04'): 500, ('WH03', 'WH05'): 9000,
        ('WH03', 'WH06'): 10000, ('WH04', 'WH05'): 9500, ('WH04', 'WH06'): 11000,
        ('WH05', 'WH06'): 4500
    }
    for (a, b), d in list(distance_matrix.items()):
        distance_matrix[(b, a)] = d

    transfer_cost = {}
    for (a, b), d in distance_matrix.items():
        if a == b:
            continue
        transfer_cost[(a, b)] = round(0.5 + d * 0.0008, 2)

    records = []
    for (fw, tw), c in transfer_cost.items():
        records.append({
            'from_warehouse': fw, 'to_warehouse': tw,
            'distance_km': distance_matrix[(fw, tw)], 'transfer_cost_per_unit': c
        })
    return pd.DataFrame(records), distance_matrix, transfer_cost


def classify_abc_xyz(sales_df, sku_df):
    """ABC-XYZ 库存分类"""
    # ABC：基于年销售额累计占比（帕累托原则）
    annual_sales = sales_df.groupby('sku_id')['units_sold'].sum().reset_index()
    annual_sales.rename(columns={'units_sold': 'annual_sales_qty'}, inplace=True)
    annual_sales = annual_sales.merge(sku_df[['sku_id', 'unit_price']], on='sku_id')
    annual_sales['annual_revenue'] = annual_sales['annual_sales_qty'] * annual_sales['unit_price']
    annual_sales = annual_sales.sort_values('annual_revenue', ascending=False).reset_index(drop=True)
    annual_sales['cum_revenue_pct'] = annual_sales['annual_revenue'].cumsum() / annual_sales['annual_revenue'].sum() * 100
    annual_sales['abc_class'] = annual_sales['cum_revenue_pct'].apply(
        lambda x: 'A' if x <= 80 else ('B' if x <= 95 else 'C')
    )

    # XYZ：基于需求变异系数 CV = std/mean
    daily_total = sales_df.groupby(['sku_id', 'date'])['units_sold'].sum().reset_index()
    xyz_stats = daily_total.groupby('sku_id')['units_sold'].agg(['mean', 'std']).reset_index()
    xyz_stats['cv'] = (xyz_stats['std'] / xyz_stats['mean']).fillna(0)
    xyz_stats['xyz_class'] = xyz_stats['cv'].apply(
        lambda x: 'X' if x < 0.5 else ('Y' if x < 1.0 else 'Z')
    )

    abc_xyz = annual_sales[['sku_id', 'abc_class', 'annual_revenue']].merge(
        xyz_stats[['sku_id', 'xyz_class', 'cv']], on='sku_id'
    )
    abc_xyz['abc_xyz'] = abc_xyz['abc_class'] + abc_xyz['xyz_class']
    return abc_xyz


def calculate_replenishment(inventory_df, abc_xyz, sku_df, wh_df, sales_df):
    """计算安全库存、ROP、EOQ、库存预警"""
    wh_names = dict(zip(wh_df['warehouse_id'], wh_df['warehouse_name']))
    recent_sales = sales_df[sales_df['date'] >= '2025-10-01'].copy()

    inventory_class = inventory_df.merge(abc_xyz[['sku_id', 'abc_class', 'xyz_class', 'abc_xyz']], on='sku_id')
    inventory_class = inventory_class.merge(
        sku_df[['sku_id', 'lead_time_days', 'moq', 'category']], on='sku_id'
    )

    z_values = {'A': 2.05, 'B': 1.65, 'C': 1.28}
    holding_cost_rate = 0.28
    ordering_cost = 800
    age_threshold = {'A': 45, 'B': 60, 'C': 90}

    records = []
    for _, row in inventory_class.iterrows():
        sku_id, wh = row['sku_id'], row['warehouse_id']
        avg_sales = row['avg_units_sold']
        lead_time = row['lead_time_days']
        unit_price = row['unit_price']
        moq = row['moq']
        abc = row['abc_class']
        available = row['available_qty']
        avg_age = row['avg_age_days']
        overage = row['overage_qty']

        # 需求标准差
        sku_wh_sales = recent_sales[
            (recent_sales['sku_id'] == sku_id) & (recent_sales['warehouse_id'] == wh)
        ]['units_sold']
        sigma = sku_wh_sales.std() if len(sku_wh_sales) > 5 else avg_sales * 0.3
        sigma = max(sigma, avg_sales * 0.1)

        # 安全库存 = Z × σ × √LT
        z = z_values[abc]
        safety_stock = int(np.ceil(z * sigma * np.sqrt(lead_time)))

        # 再订货点 ROP
        rop = int(np.ceil(avg_sales * lead_time + safety_stock))

        # EOQ
        annual_demand = avg_sales * 365
        h = unit_price * holding_cost_rate
        eoq = int(np.ceil(np.sqrt(2 * annual_demand * ordering_cost / h))) if h > 0 and annual_demand > 0 else moq
        eoq = max(eoq, moq)

        # 库存预警
        stock_ratio = available / rop if rop > 0 else 999
        if available <= rop:
            alert_level = '红色预警（需补货）'
        elif stock_ratio <= 1.5:
            alert_level = '黄色预警（关注）'
        else:
            alert_level = '正常'
        days_to_stockout = available / avg_sales if avg_sales > 0 else 999

        # 超龄预警
        age_thresh = age_threshold[abc]
        if avg_age > age_thresh:
            age_alert = f'超龄（{avg_age}天 > {age_thresh}天阈值）'
        elif avg_age > age_thresh * 0.7:
            age_alert = f'接近超龄（{avg_age}天）'
        else:
            age_alert = f'正常（{avg_age}天）'

        records.append({
            'sku_id': sku_id, 'warehouse_id': wh, 'warehouse_name': wh_names[wh],
            'category': row['category'], 'abc_class': abc, 'xyz_class': row['xyz_class'],
            'abc_xyz': row['abc_xyz'], 'unit_price': unit_price,
            'avg_units_sold': avg_sales, 'lead_time_days': lead_time,
            'safety_stock': safety_stock, 'rop': rop, 'eoq': eoq, 'moq': moq,
            'available_qty': available, 'in_transit_qty': row['in_transit_qty'],
            'total_qty': row['total_qty'], 'avg_age_days': avg_age,
            'overage_qty': overage, 'stock_alert': alert_level,
            'age_alert': age_alert, 'days_to_stockout': round(days_to_stockout, 1),
            'z_value': z
        })

    return pd.DataFrame(records)


def generate_transfer_recommendations(replenishment_df, distance_matrix, transfer_cost):
    """生成调拨建议（红预警仓 → 超龄富余仓）"""
    red_alert = replenishment_df[replenishment_df['stock_alert'] == '红色预警（需补货）'].copy()
    excess_df = replenishment_df[replenishment_df['available_qty'] > replenishment_df['rop'] * 2].copy()
    excess_df = excess_df[excess_df['overage_qty'] > 0]

    recommendations = []
    for _, need in red_alert.iterrows():
        sku_id, to_wh = need['sku_id'], need['warehouse_id']
        need_qty = need['eoq']

        candidates = excess_df[
            (excess_df['sku_id'] == sku_id) &
            (excess_df['warehouse_id'] != to_wh) &
            (excess_df['overage_qty'] >= need_qty * 0.5)
        ].copy()
        if len(candidates) == 0:
            continue

        scores = []
        for _, cand in candidates.iterrows():
            from_wh = cand['warehouse_id']
            dist = distance_matrix.get((from_wh, to_wh), 10000)
            distance_score = 1 / (1 + dist / 1000)
            cost = transfer_cost.get((from_wh, to_wh), 5.0)
            cost_score = 1 / (1 + cost / 2)
            transferable = min(cand['overage_qty'], cand['available_qty'] - cand['rop'])
            inventory_score = min(transferable / need_qty, 3) / 3
            total_score = 0.6 * distance_score + 0.3 * cost_score + 0.1 * inventory_score

            scores.append({
                'from_warehouse': from_wh, 'to_warehouse': to_wh, 'sku_id': sku_id,
                'distance_km': dist, 'transfer_cost_per_unit': cost,
                'transferable_qty': int(transferable), 'need_qty': need_qty,
                'distance_score': round(distance_score, 3),
                'cost_score': round(cost_score, 3),
                'inventory_score': round(inventory_score, 3),
                'total_score': round(total_score, 3)
            })

        if scores:
            recommendations.append(max(scores, key=lambda x: x['total_score']))

    df = pd.DataFrame(recommendations)
    if len(df) > 0:
        df = df.sort_values('total_score', ascending=False)
    return df


def main():
    print("=" * 60)
    print("模块3：智能补货与多仓调拨引擎")
    print("=" * 60)

    # 读取数据
    print("\n[0/6] 读取基础数据...")
    sku_df = pd.read_csv(os.path.join(DATA_DIR, "sku_master.csv"))
    wh_df = pd.read_csv(os.path.join(DATA_DIR, "warehouse_master.csv"))
    sales_df = pd.read_csv(os.path.join(DATA_DIR, "sales_daily.csv"))
    
    # 中文表头 → 英文列名映射
    _cn_map = {
        '日期': 'date', 'SKU编码': 'sku_id', '仓库ID': 'warehouse_id',
        '销售数量': 'units_sold', '退货数量': 'units_returned',
        'SKU名称': 'sku_name', '品类': 'category', '供应商ID': 'supplier_id',
        '单价': 'unit_price', '重量kg': 'weight_kg', '上市日期': 'launch_date',
        '生命周期月数': 'lifecycle_months', '季节性强度': 'seasonal_strength',
        '退货率': 'return_rate', '仓库名称': 'warehouse_name', '国家': 'country',
        '区域': 'region', '覆盖范围': 'coverage',
        '最小起订量': 'moq', '采购提前期天数': 'lead_time_days',
        '海运天数': 'headway_days', '尾程天数': 'last_mile_days'
    }
    sales_df = sales_df.rename(columns=_cn_map)
    sku_df = sku_df.rename(columns=_cn_map)
    wh_df = wh_df.rename(columns=_cn_map)
    
    sales_df['date'] = pd.to_datetime(sales_df['date'])

    # 1. 库存快照
    print("\n[1/6] 生成库存快照...")
    inventory_df = generate_inventory_snapshot(sku_df, wh_df, sales_df)
    # 先保存英文版用于内部计算，最后再转中文
    inventory_df_raw = inventory_df.copy()
    inventory_df_display = inventory_df.rename(columns={
        'sku_id': 'SKU编码',
        'warehouse_id': '仓库ID',
        'available_qty': '可用数量',
        'in_transit_qty': '在途数量',
        'total_qty': '总数量',
        'avg_age_days': '平均库龄天数',
        'overage_qty': '超龄数量',
        'unit_price': '单价',
        'avg_units_sold': '日均销量'
    })
    inventory_df_display.to_csv(os.path.join(DATA_DIR, "inventory_snapshot.csv"), index=False)
    print(f"   OK 库存快照：{len(inventory_df)} 条")

    # 2. 调拨成本矩阵
    print("\n[2/6] 生成调拨成本矩阵...")
    transfer_cost_df, distance_matrix, transfer_cost = generate_transfer_cost_matrix(wh_df)
    transfer_cost_df_display = transfer_cost_df.rename(columns={
        'from_warehouse': '出发仓库',
        'to_warehouse': '目标仓库',
        'distance_km': '距离km',
        'transfer_cost_per_unit': '调拨单位成本'
    })
    transfer_cost_df_display.to_csv(os.path.join(DATA_DIR, "transfer_cost_matrix.csv"), index=False)
    print(f"   OK 调拨成本矩阵：{len(transfer_cost_df)} 条")

    # 3. ABC-XYZ 分类
    print("\n[3/6] 执行 ABC-XYZ 库存分类...")
    abc_xyz = classify_abc_xyz(sales_df, sku_df)
    print("   ABC-XYZ 分类统计：")
    for cls in sorted(abc_xyz['abc_xyz'].unique()):
        print(f"      {cls}: {(abc_xyz['abc_xyz'] == cls).sum()} 个SKU")

    # 4. 安全库存 / ROP / EOQ
    print("\n[4/6] 计算安全库存、ROP、EOQ...")
    replenishment_df = calculate_replenishment(inventory_df_raw, abc_xyz, sku_df, wh_df, sales_df)

    # 5. 调拨建议
    print("\n[5/6] 生成调拨建议...")
    transfer_rec_df = generate_transfer_recommendations(replenishment_df, distance_matrix, transfer_cost)

    # 6. 输出（计算完成后再转中文表头）
    print("\n[6/6] 保存输出文件...")
    replenishment_df = replenishment_df.rename(columns={
        'sku_id': 'SKU编码',
        'warehouse_id': '仓库ID',
        'warehouse_name': '仓库名称',
        'category': '品类',
        'abc_class': 'ABC分类',
        'xyz_class': 'XYZ分类',
        'abc_xyz': 'ABC-XYZ组合',
        'unit_price': '单价',
        'avg_units_sold': '日均销量',
        'lead_time_days': '采购提前期天数',
        'safety_stock': '安全库存',
        'rop': '再订货点',
        'eoq': '经济订货量',
        'moq': '最小起订量',
        'available_qty': '可用数量',
        'in_transit_qty': '在途数量',
        'total_qty': '总数量',
        'avg_age_days': '平均库龄天数',
        'overage_qty': '超龄数量',
        'stock_alert': '库存预警',
        'age_alert': '库龄预警',
        'days_to_stockout': '预计缺货天数',
        'z_value': 'Z值'
    })
    replenishment_df.to_csv(os.path.join(OUTPUT_DIR, "replenishment_plan.csv"), index=False)
    print(f"   OK 补货计划：{len(replenishment_df)} 条 -> output/replenishment_plan.csv")

    if len(transfer_rec_df) > 0:
        transfer_rec_df = transfer_rec_df.rename(columns={
            'from_warehouse': '出发仓库',
            'to_warehouse': '目标仓库',
            'sku_id': 'SKU编码',
            'distance_km': '距离km',
            'transfer_cost_per_unit': '调拨单位成本',
            'transferable_qty': '可调拨数量',
            'need_qty': '需求数量',
            'distance_score': '距离评分',
            'cost_score': '成本评分',
            'inventory_score': '库存评分',
            'total_score': '综合评分'
        })
        transfer_rec_df.to_csv(os.path.join(OUTPUT_DIR, "transfer_recommendation.csv"), index=False)
        print(f"   OK 调拨建议：{len(transfer_rec_df)} 条 -> output/transfer_recommendation.csv")
    else:
        print(f"   ! 调拨建议：无可行调拨方案（红预警SKU在富余仓无超龄库存可转出）")

    # 库存健康报告
    health = replenishment_df.groupby('仓库ID').agg({
        'SKU编码': 'count', '可用数量': 'sum', '总数量': 'sum', '超龄数量': 'sum'
    }).reset_index()
    health.columns = ['仓库ID', 'SKU数量', '可用库存总量', '库存总量', '超龄库存总量']
    alert_summary = replenishment_df.groupby(['仓库ID', '库存预警']).size().unstack(fill_value=0).reset_index()
    health = health.merge(alert_summary, on='仓库ID', how='left')
    health.to_csv(os.path.join(OUTPUT_DIR, "inventory_health_report.csv"), index=False)
    print(f"   OK 库存健康报告：{len(health)} 个仓库 -> output/inventory_health_report.csv")

    # 业务验证
    print("\n" + "=" * 60)
    print("业务逻辑验证")
    print("=" * 60)

    abc_dist = replenishment_df.groupby('ABC分类')['SKU编码'].nunique()
    print(f"\n[验证1] ABC分类分布：")
    for cls in ['A', 'B', 'C']:
        cnt = abc_dist.get(cls, 0)
        print(f"   {cls}类: {cnt} 个SKU ({cnt / 100 * 100:.0f}%)")

    ss_by_abc = replenishment_df.groupby('ABC分类')['安全库存'].mean()
    print(f"\n[验证2] 平均安全库存（A>B>C 预期）：")
    for cls in ['A', 'B', 'C']:
        print(f"   {cls}类: {ss_by_abc.get(cls, 0):.1f} 件")

    alert_dist = replenishment_df['库存预警'].value_counts()
    print(f"\n[验证3] 库存预警分布：")
    for alert, cnt in alert_dist.items():
        print(f"   {alert}: {cnt} 条 ({cnt / len(replenishment_df) * 100:.1f}%)")

    if len(transfer_rec_df) > 0:
        print(f"\n[验证4] 调拨建议：{len(transfer_rec_df)} 条")
        print(f"   平均距离: {transfer_rec_df['距离km'].mean():.0f} km")
        print(f"   平均成本: ${transfer_rec_df['调拨单位成本'].mean():.2f}/件")
        print(f"   平均评分: {transfer_rec_df['综合评分'].mean():.3f}")
    else:
        print(f"\n[验证4] 调拨建议：无可行方案（符合业务逻辑）")

    age_alert_dist = replenishment_df['库龄预警'].apply(lambda x: x.split('（')[0]).value_counts()
    print(f"\n[验证5] 库龄预警分布：")
    for alert, cnt in age_alert_dist.items():
        print(f"   {alert}: {cnt} 条 ({cnt / len(replenishment_df) * 100:.1f}%)")

    total_value = (replenishment_df['可用数量'] * replenishment_df['单价']).sum()
    print(f"\n[验证6] 总库存价值: ${total_value:,.0f}")

    print("\n" + "=" * 60)
    print("模块3执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
