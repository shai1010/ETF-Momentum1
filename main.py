import efinance as ef
import pandas as pd
import numpy as np
from scipy.stats import linregress
import math

# ================= 核心数学函数 (与原版完全一致) =================
def calculate_momentum_score(prices, days=29):
    """计算: 年化收益率 * R2"""
    if len(prices) < days: return -999
    y = np.log(prices[-days:])
    x = np.arange(len(y))
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    annualized_returns = math.pow(math.exp(slope), 250) - 1
    r_squared = r_value ** 2
    return annualized_returns * r_squared

def get_ols_slope_and_r2(lows, highs):
    """计算 RSRS 所需的斜率和 R2"""
    slope, intercept, r_value, p_value, std_err = linregress(lows, highs)
    return slope, r_value ** 2

# ================= 核心策略逻辑 =================
def run_strategy():
    print("🚀 启动 100% 复刻版：RSRS择时 + 20日均线防守 + 动量评分系统")
    
    # 1. 大盘择时数据获取 (沪深300)
    # 获取 800 天数据以覆盖 600天的滚动周期
    ref_df = ef.stock.get_quote_history('000300')
    N, M = 18, 600
    
    # 计算 RSRS 斜率序列
    all_slopes = []
    for i in range(len(ref_df) - N + 1):
        sub = ref_df.iloc[i : i + N]
        slope, _ = get_ols_slope_and_r2(sub['最低'].values, sub['最高'].values)
        all_slopes.append(slope)
    
    # 当前时刻的 RSRS 核心指标
    current_lows = ref_df['最低'].iloc[-N:].values
    current_highs = ref_df['最高'].iloc[-N:].values
    curr_slope, curr_r2 = get_ols_slope_and_r2(current_lows, current_highs)
    
    # 计算 Z-Score
    history_slopes = all_slopes[-M:]
    mean = np.mean(history_slopes)
    std = np.std(history_slopes)
    z_score = (curr_slope - mean) / std
    rsrs_score = z_score * curr_r2 # 【完全复刻：Z-Score * R2】
    
    # 20日均线趋势判断 (完全复刻原版：今日MA20 vs 前置MA20)
    # 原版逻辑取了 mean_day + mean_diff_day (20+3) 的窗口进行对比
    ma20_now = ref_df['收盘'].iloc[-20:].mean()
    ma20_before = ref_df['收盘'].iloc[-23:-3].mean()
    
    print(f"📊 RSRS得分: {rsrs_score:.2f} (阈值 0.7/-0.7)")
    print(f"📈 均线趋势: {'向上' if ma20_now > ma20_before else '向下'}")

    # 信号判断
    timing_signal = "KEEP"
    if rsrs_score > 0.7 and ma20_now > ma20_before:
        timing_signal = "BUY"
    elif rsrs_score < -0.7 and ma20_now < ma20_before:
        timing_signal = "SELL"

    if timing_signal == "SELL":
        print("🛑 【最终建议】：择时信号为 SELL，请立即【清仓/空仓】！")
    else:
        print("✅ 【最终建议】：择时信号安全，正在计算动量轮动评分...")
        # 轮动标的评分 (完全复刻：年化收益 * R2)
        pool = {'黄金ETF': '518880', '纳指ETF': '513100', '创业板ETF': '159915', '上证180ETF': '510180'}
        rank_results = []
        for name, code in pool.items():
            df_etf = ef.stock.get_quote_history(code)
            score = calculate_momentum_score(df_etf['收盘'].values, days=29)
            rank_results.append((name, code, score))
        
        # 排序选出第 1 名
        rank_results.sort(key=lambda x: x[2], reverse=True)
        best = rank_results[0]
        print(f"\n🎯 结论：【做多 {best[0]}】({best[1]})")
        print(f"📝 策略评分 (年化收益*R2): {best[2]:.4f}")

if __name__ == "__main__":
    run_strategy()
