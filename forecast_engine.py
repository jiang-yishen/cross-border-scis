"""
跨境海外仓供应链智能决策系统 - 需求预测算法引擎
==========================================================

功能：基于历史销售数据，使用 Prophet + XGBoost 混合模型预测未来需求
输入：data/sales_daily.csv, data/sku_master.csv
输出：output/demand_forecast.csv（预测结果 + 置信区间）

算法策略：
  - Prophet：长期趋势 + 季节性 + 节假日效应
  - XGBoost：短期波动 + 多特征（Lag/Rolling/促销/品类）
  - 集成：Prophet(60%) + XGBoost(40%) 加权融合
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# 尝试导入 Prophet，如果失败则跳过
PROPHET_AVAILABLE = False
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    print("[WARN] Prophet 未安装，将使用简化版预测（基于移动平均+趋势）")

# 尝试导入 XGBoost，如果失败则跳过
XGB_AVAILABLE = False
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    print("[WARN] XGBoost 未安装，将使用简化版预测")


# =============================================================================
# 配置
# =============================================================================
PROJECT_DIR = r"C:\Users\11363\Desktop\供应链计划面试\供应链优化项目"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 预测未来30天
FORECAST_DAYS = 30

# 节假日定义（跨境电商关键日期）
HOLIDAYS_DF = pd.DataFrame({
    'holiday': ['SpringFestival', 'SpringFestival', 'SpringFestival',
                'LaborDay', 'LaborDay',
                '618', '618', 'PrimeDay', 'PrimeDay',
                'Double11', 'Double11',
                'BlackFriday', 'BlackFriday', 'BlackFriday',
                'Christmas', 'Christmas',
                'Valentine', 'Valentine',
                'MothersDay', 'MothersDay'],
    'ds': pd.to_datetime(['2024-02-10', '2024-02-11', '2024-02-12',
                          '2024-05-01', '2025-05-01',
                          '2024-06-18', '2025-06-18', '2024-07-16', '2025-07-15',
                          '2024-11-11', '2025-11-11',
                          '2024-11-29', '2024-11-30', '2024-12-02',
                          '2024-12-25', '2025-12-25',
                          '2024-02-14', '2025-02-14',
                          '2024-05-12', '2025-05-11']),
    'lower_window': [-2, -2, -2, -1, -1, -1, -1, -1, -1, -3, -3, -3, -3, -3, -5, -5, -1, -1, -1, -1],
    'upper_window': [2, 2, 2, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 5, 5, 1, 1, 1, 1],
})


def load_data():
    """加载销售数据和SKU主数据"""
    _cn_map = {
        '日期': 'date', 'SKU编码': 'sku_id', '仓库ID': 'warehouse_id',
        '销售数量': 'units_sold', '退货数量': 'units_returned',
        'SKU名称': 'sku_name', '品类': 'category', '供应商ID': 'supplier_id',
        '单价': 'unit_price', '重量kg': 'weight_kg', '上市日期': 'launch_date',
        '生命周期月数': 'lifecycle_months', '季节性强度': 'seasonal_strength',
        '退货率': 'return_rate', '最小起订量': 'moq', '采购提前期天数': 'lead_time_days',
    }
    sales = pd.read_csv(os.path.join(DATA_DIR, "sales_daily.csv"))
    sales = sales.rename(columns=_cn_map)
    sales['date'] = pd.to_datetime(sales['date'])
    skus = pd.read_csv(os.path.join(DATA_DIR, "sku_master.csv"))
    skus = skus.rename(columns=_cn_map)
    return sales, skus


def prepare_sku_daily(sales, sku_id, warehouse_id=None):
    """准备单个SKU的日销售时间序列"""
    if warehouse_id:
        df = sales[(sales['sku_id'] == sku_id) & (sales['warehouse_id'] == warehouse_id)].copy()
    else:
        # 按SKU聚合所有仓库的销量
        df = sales[sales['sku_id'] == sku_id].groupby('date').agg({
            'units_sold': 'sum',
            'units_returned': 'sum'
        }).reset_index()
    
    # 确保日期连续（填充缺失日期为0）
    if len(df) == 0:
        return None
    
    date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
    df_full = pd.DataFrame({'date': date_range})
    df_full = df_full.merge(df[['date', 'units_sold']], on='date', how='left')
    df_full['units_sold'] = df_full['units_sold'].fillna(0)
    
    return df_full


def forecast_prophet(df, sku_info=None):
    """使用 Prophet 进行预测（或简化版）"""
    if PROPHET_AVAILABLE and len(df) > 30:
        try:
            m = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                holidays=HOLIDAYS_DF,
                interval_width=0.8,
                changepoint_prior_scale=0.05,
            )
            # 添加品类特定的季节性（如果数据足够）
            if sku_info and sku_info.get('seasonal_strength', 0) > 0.5:
                m.add_seasonality(name='strong_monthly', period=30.5, fourier_order=5)
            
            m.fit(df.rename(columns={'date': 'ds', 'units_sold': 'y'}))
            future = m.make_future_dataframe(periods=FORECAST_DAYS)
            forecast = m.predict(future)
            
            return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(columns={
                'ds': 'date', 'yhat': 'forecast', 'yhat_lower': 'lower', 'yhat_upper': 'upper'
            })
        except Exception as e:
            print(f"  Prophet失败: {e}, 使用简化版")
        
    # 简化版：移动平均 + 趋势
    return forecast_simplified(df)


def forecast_simplified(df):
    """简化版预测：指数平滑 + 趋势"""
    values = df['units_sold'].values
    n = len(values)
    
    # 计算趋势（最近30天 vs 前30天）
    if n >= 60:
        recent_mean = np.mean(values[-30:])
        old_mean = np.mean(values[-60:-30])
        trend = (recent_mean - old_mean) / 30
    else:
        trend = 0
    
    # 7天移动平均作为基准
    baseline = np.mean(values[-7:]) if n >= 7 else np.mean(values)
    
    # 季节性因子（基于历史同期）
    seasonal_factors = {}
    if n >= 365:
        for day in range(FORECAST_DAYS):
            future_date = df['date'].iloc[-1] + timedelta(days=day+1)
            month_day = (future_date.month, future_date.day)
            # 找历史同期的平均值
            hist_values = []
            for i, d in enumerate(df['date']):
                if (d.month, d.day) == month_day:
                    hist_values.append(values[i])
            if hist_values:
                seasonal_factors[day] = np.mean(hist_values) / baseline if baseline > 0 else 1
            else:
                seasonal_factors[day] = 1
    else:
        seasonal_factors = {day: 1 for day in range(FORECAST_DAYS)}
    
    # 生成预测
    forecasts = []
    for day in range(FORECAST_DAYS):
        future_date = df['date'].iloc[-1] + timedelta(days=day+1)
        pred = max(0, baseline + trend * (day + 1)) * seasonal_factors.get(day, 1)
        
        # 检查是否是节假日
        date_str = future_date.strftime('%Y-%m-%d')
        holiday_dates = set(HOLIDAYS_DF['ds'].dt.strftime('%Y-%m-%d'))
        if date_str in holiday_dates:
            pred *= 1.3  # 节假日提升30%
        
        # 置信区间
        std = np.std(values[-30:]) if n >= 30 else np.std(values)
        forecasts.append({
            'date': future_date,
            'forecast': pred,
            'lower': max(0, pred - 1.5 * std),
            'upper': pred + 1.5 * std,
        })
    
    return pd.DataFrame(forecasts)


def forecast_xgboost(df, sku_info=None):
    """使用 XGBoost 进行特征工程 + 预测（或简化版）"""
    if not XGB_AVAILABLE or len(df) < 60:
        # 返回None，后续用Prophet结果替代
        return None
    
    try:
        # 特征工程
        df_feat = df.copy()
        df_feat['dayofweek'] = df_feat['date'].dt.dayofweek
        df_feat['month'] = df_feat['date'].dt.month
        df_feat['dayofmonth'] = df_feat['date'].dt.day
        df_feat['is_weekend'] = (df_feat['dayofweek'] >= 5).astype(int)
        
        # Lag特征
        for lag in [1, 7, 14, 30]:
            df_feat[f'lag_{lag}'] = df_feat['units_sold'].shift(lag)
        
        # Rolling特征
        for window in [7, 14, 30]:
            df_feat[f'rolling_mean_{window}'] = df_feat['units_sold'].shift(1).rolling(window).mean()
            df_feat[f'rolling_std_{window}'] = df_feat['units_sold'].shift(1).rolling(window).std()
        
        # 节假日特征
        df_feat['is_holiday'] = df_feat['date'].dt.strftime('%Y-%m-%d').isin(
            set(HOLIDAYS_DF['ds'].dt.strftime('%Y-%m-%d'))
        ).astype(int)
        
        # 品类季节性强度
        if sku_info:
            df_feat['seasonal_strength'] = sku_info.get('seasonal_strength', 0.5)
        
        # 去掉NaN行
        df_feat = df_feat.dropna()
        
        if len(df_feat) < 30:
            return None
        
        # 训练XGBoost
        feature_cols = [c for c in df_feat.columns if c not in ['date', 'units_sold']]
        X = df_feat[feature_cols]
        y = df_feat['units_sold']
        
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
        )
        model.fit(X, y)
        
        # 生成未来特征并预测
        forecasts = []
        last_values = df['units_sold'].values
        
        for day in range(FORECAST_DAYS):
            future_date = df['date'].iloc[-1] + timedelta(days=day+1)
            
            # 构建特征
            feat = {
                'dayofweek': future_date.weekday(),
                'month': future_date.month,
                'dayofmonth': future_date.day,
                'is_weekend': 1 if future_date.weekday() >= 5 else 0,
                'is_holiday': 1 if future_date.strftime('%Y-%m-%d') in 
                    set(HOLIDAYS_DF['ds'].dt.strftime('%Y-%m-%d')) else 0,
            }
            
            # Lag特征（用最近实际值+已预测值）
            for lag in [1, 7, 14, 30]:
                idx = len(df) + day - lag
                if idx < len(df):
                    feat[f'lag_{lag}'] = last_values[idx]
                else:
                    feat[f'lag_{lag}'] = forecasts[idx - len(df)]['forecast_xgb'] if idx >= len(df) else 0
            
            # Rolling特征
            for window in [7, 14, 30]:
                window_values = []
                for i in range(day, day - window, -1):
                    idx = len(df) + i - 1
                    if idx < len(df):
                        window_values.append(last_values[idx])
                    elif idx >= len(df):
                        window_values.append(forecasts[idx - len(df)]['forecast_xgb'])
                if window_values:
                    feat[f'rolling_mean_{window}'] = np.mean(window_values)
                    feat[f'rolling_std_{window}'] = np.std(window_values) if len(window_values) > 1 else 0
                else:
                    feat[f'rolling_mean_{window}'] = 0
                    feat[f'rolling_std_{window}'] = 0
            
            if sku_info:
                feat['seasonal_strength'] = sku_info.get('seasonal_strength', 0.5)
            
            X_pred = pd.DataFrame([feat])[feature_cols]
            pred = max(0, model.predict(X_pred)[0])
            
            forecasts.append({
                'date': future_date,
                'forecast_xgb': pred,
            })
        
        return pd.DataFrame(forecasts)
    
    except Exception as e:
        print(f"  XGBoost失败: {e}")
        return None


def ensemble_forecast(prophet_df, xgb_df, sku_info=None):
    """Prophet + XGBoost 集成融合"""
    if xgb_df is None:
        # 只有Prophet，权重100%
        prophet_df['ensemble'] = prophet_df['forecast']
        prophet_df['prophet_weight'] = 1.0
        prophet_df['xgb_weight'] = 0.0
        return prophet_df
    
    # 合并
    merged = prophet_df.merge(xgb_df[['date', 'forecast_xgb']], on='date', how='left')
    
    # 根据品类特性调整权重
    # 服装/美妆：季节性强 → Prophet权重更高(70%)
    # 3C/宠物：波动大 → XGBoost权重更高(50%)
    if sku_info:
        cat = sku_info.get('category', '')
        if cat in ['服装鞋履', '美妆个护', '运动户外']:
            pw, xw = 0.65, 0.35
        elif cat in ['宠物用品']:
            pw, xw = 0.55, 0.45
        else:
            pw, xw = 0.6, 0.4
    else:
        pw, xw = 0.6, 0.4
    
    merged['ensemble'] = merged['forecast'] * pw + merged['forecast_xgb'] * xw
    merged['prophet_weight'] = pw
    merged['xgb_weight'] = xw
    
    return merged


def calculate_mape(actual, forecast):
    """计算 MAPE（平均绝对百分比误差）"""
    mask = actual != 0
    if mask.sum() == 0:
        return np.nan
    return np.mean(np.abs((actual[mask] - forecast[mask]) / actual[mask])) * 100


def backtest(sales, sku_id, forecast_df, warehouse_id=None):
    """回测：用历史最后30天验证预测准确性"""
    if warehouse_id:
        actual = sales[(sales['sku_id'] == sku_id) & (sales['warehouse_id'] == warehouse_id)].copy()
    else:
        actual = sales[sales['sku_id'] == sku_id].groupby('date')['units_sold'].sum().reset_index()
    
    actual['date'] = pd.to_datetime(actual['date'])
    
    # 取最后30天作为测试集
    test_dates = forecast_df['date'].values
    actual_test = actual[actual['date'].isin(test_dates)]
    
    if len(actual_test) == 0:
        return None
    
    merged = actual_test.merge(forecast_df[['date', 'ensemble']], on='date', how='left')
    merged = merged.dropna()
    
    if len(merged) == 0:
        return None
    
    mape = calculate_mape(merged['units_sold'].values, merged['ensemble'].values)
    return mape


def run_forecast_engine():
    """主函数：运行需求预测引擎"""
    print("="*60)
    print("[模块2] 需求预测算法引擎")
    print("="*60)
    
    sales, skus = load_data()
    print(f"[数据] 加载: {len(sales)} 条销售记录, {len(skus)} 个SKU")
    
    all_forecasts = []
    backtest_results = []
    
    sku_list = skus['sku_id'].unique()
    total = len(sku_list)
    
    for idx, sku_id in enumerate(sku_list):
        if idx % 10 == 0:
            print(f"   进度: {idx}/{total} SKU...")
        
        sku_info = skus[skus['sku_id'] == sku_id].iloc[0].to_dict()
        
        # 准备数据（按SKU聚合所有仓库）
        df = prepare_sku_daily(sales, sku_id)
        if df is None or len(df) < 14:
            continue
        
        # Prophet预测
        prophet_df = forecast_prophet(df, sku_info)
        
        # XGBoost预测
        xgb_df = forecast_xgboost(df, sku_info)
        
        # 集成融合
        ensemble_df = ensemble_forecast(prophet_df, xgb_df, sku_info)
        
        # 回测
        mape = backtest(sales, sku_id, ensemble_df)
        
        # 添加SKU信息
        ensemble_df['sku_id'] = sku_id
        ensemble_df['category'] = sku_info.get('category', '未知')
        ensemble_df['warehouse_id'] = 'ALL'  # 聚合预测
        
        if mape is not None:
            ensemble_df['mape'] = mape
            backtest_results.append({
                'sku_id': sku_id,
                'category': sku_info.get('category', '未知'),
                'mape': mape,
                'prophet_weight': ensemble_df['prophet_weight'].iloc[0],
                'xgb_weight': ensemble_df['xgb_weight'].iloc[0],
            })
        
        # 只保留未来预测部分
        future = ensemble_df[ensemble_df['date'] > df['date'].max()].copy()
        all_forecasts.append(future)
    
    # 合并所有预测
    if all_forecasts:
        forecast_result = pd.concat(all_forecasts, ignore_index=True)
        # 动态选择列（mape可能不存在）
        cols = [
            'sku_id', 'category', 'warehouse_id', 'date',
            'forecast', 'lower', 'upper', 'ensemble',
            'prophet_weight', 'xgb_weight'
        ]
        if 'mape' in forecast_result.columns:
            cols.append('mape')
        forecast_result = forecast_result[cols]
        
        rename_map = {
            'sku_id': 'SKU编码',
            'category': '品类',
            'warehouse_id': '仓库编码',
            'date': '日期',
            'forecast': '预测销量',
            'lower': '预测下限',
            'upper': '预测上限',
            'ensemble': '集成预测',
            'prophet_weight': 'Prophet权重',
            'xgb_weight': 'XGBoost权重'
        }
        if 'mape' in forecast_result.columns:
            rename_map['mape'] = '平均绝对百分比误差(%)'
        forecast_result = forecast_result.rename(columns=rename_map)
        
        forecast_result.to_csv(os.path.join(OUTPUT_DIR, "demand_forecast.csv"), 
                                index=False, encoding="utf-8-sig")
        print(f"\n[OK] 预测结果已保存: {len(forecast_result)} 条记录")
    
    # 回测统计
    if backtest_results:
        backtest_df = pd.DataFrame(backtest_results)
        backtest_df = backtest_df.rename(columns={
            'sku_id': 'SKU编码',
            'category': '品类',
            'mape': '平均绝对百分比误差(%)',
            'prophet_weight': 'Prophet权重',
            'xgb_weight': 'XGBoost权重'
        })
        backtest_df.to_csv(os.path.join(OUTPUT_DIR, "forecast_backtest.csv"), 
                           index=False, encoding="utf-8-sig")
        
        print("\n" + "="*60)
        print("[结果] 回测统计")
        print("="*60)
        print(f"  总SKU数: {len(backtest_df)}")
        print(f"  平均MAPE: {backtest_df['mape'].mean():.2f}%")
        print(f"  中位数MAPE: {backtest_df['mape'].median():.2f}%")
        print(f"  MAPE < 20%: {(backtest_df['mape'] < 20).sum()} / {len(backtest_df)} ({(backtest_df['mape']<20).mean()*100:.1f}%)")
        print(f"  MAPE < 30%: {(backtest_df['mape'] < 30).sum()} / {len(backtest_df)} ({(backtest_df['mape']<30).mean()*100:.1f}%)")
        
        print("\n  按品类MAPE:")
        cat_mape = backtest_df.groupby('category')['mape'].agg(['mean', 'median', 'count'])
        print(cat_mape)
        
        return {
            'status': 'success',
            'forecast_records': len(forecast_result),
            'backtest_records': len(backtest_df),
            'avg_mape': round(backtest_df['mape'].mean(), 2),
            'median_mape': round(backtest_df['mape'].median(), 2),
            'category_mape': cat_mape.to_dict(),
        }
    
    return {'status': 'success', 'forecast_records': 0}


if __name__ == '__main__':
    run_forecast_engine()

main = run_forecast_engine
