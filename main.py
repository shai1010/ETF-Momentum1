import efinance as ef
import pandas as pd
import numpy as np
from scipy.stats import linregress
import math
import time

# ================= 稳健数据抓取函数 (防止断网) =================
def get_data_safe(code, retry=5):
    """如果连接断开，自动重试 5 次"""
    for i in range(retry):
        try:
            df = ef.stock.get_quote_history(code)
            if df is not None and not df.empty:
                return df
        except Exception:
            print(f"🔄 正在尝试重新连接 {code} (第 {i+1} 次)...")
            time.sleep(3) # 等 3 秒再试
    return pd.DataFrame()

# ================= 核心数学函数 (100% 复刻原版) =================
def calculate_momentum_score(prices, days=29):
    if len(prices) < days: return -999
    y = np.log(prices[-days:])
    x = np.arange(len(y))
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    annualized_returns = math.pow(math.exp(slope), 250) - 1
    r_squared = r_value ** 2
    return annualized_returns * r_squared

def get_ols_slope_and_r2(lows, highs):
    slope, intercept, r_value, p_value, std_err = linregress(lows, highs)
    return slope, r_value ** 2

# ================= 核心策略逻辑 =================
def run_strategy():
    print("🚀 启动 100% 复刻版：RSRS择时 + 20日均线防守 + 动量评分系统 (带重试保护)")
    
    # 1. 大盘择时数据获取 (沪深300)
    ref_df = get_data_safe('000300')
    if ref_df.empty:
        print("❌ 无法连接到服务器，请稍后手动重新运行一次。")
        return

    N, M = 18, 600
    all_slopes = []
    for i in range(len(ref_df) - N + 1):
        sub = ref_df.iloc[i : i + N]
        slope, _ = get_ols_slope_and_r2(sub['最低'].values, sub['最高'].values)
        all_slopes.append(slope)
    
    curr_lows = ref_df['最低'].iloc[-N:].values
    curr_highs = ref_df['最高'].iloc[-N:].values
    curr_slope, curr_r2 = get_ols_slope_and_r2(current_lows, current_highs)
    
    history_slopes = all_slopes[-M:]
    z_score = (curr_slope - np.mean(history_slopes)) / np.std(history_slopes)
    rsrs_score = z_score * curr_r2
    
    ma20_now = ref_df['收盘'].iloc[-20:].mean()
    ma20_before = ref_df['收盘'].iloc[-23:-3].mean()
    
    print(f"📊 RSRS得分: {rsrs_score:.2f} | 均线: {'向上' if ma20_now > ma20_before else '向下'}")

    timing_signal = "KEEP"
    if rsrs_score > 0.7 and ma20_now > ma20_before:
        timing_signal = "BUY"
    elif rsrs_score < -0.7 and ma20_now < ma20_before:
        timing_signal = "SELL"

    if timing_signal == "SELL":
        print("🛑 【最终建议】：择时信号为 SELL，建议【空仓】。")
    else:
        print("✅ 【最终建议】：环境安全，计算轮动评分...")
        pool = {'黄金ETF': '518880', '纳指ETF': '513100', '创业板ETF': '159915', '上证180ETF': '510180'}
        rank_results = []
        for name, code in pool.items():
            df_etf = get_data_safe(code)
            if not df_etf.empty:
                score = calculate_momentum_score(df_etf['收盘'].values, days=29)
                rank_results.append((name, code, score))
        
        rank_results.sort(key=lambda x: x[2], reverse=True)
        best = rank_results[0]
        print(f"\n🎯 结论：【做多 {best[0]}】({best[1]}) | 评分: {best[2]:.4f}")

if __name__ == "__main__":
    run_strategy()
