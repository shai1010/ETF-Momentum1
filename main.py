import akshare as ak
import pandas as pd

def check_signal():
    print("🚀 正在获取 A 股真实数据...")
    try:
        # 获取沪深300和创业板数据
        df_A = ak.fund_etf_hist_em(symbol="510300", period="daily", start_date="20230101", end_date="20260501")
        df_B = ak.fund_etf_hist_em(symbol="159915", period="daily", start_date="20230101", end_date="20260501")
        
        # 计算 20 日涨幅
        ret_A = (df_A['收盘'].iloc[-1] - df_A['收盘'].iloc[-20]) / df_A['收盘'].iloc[-20]
        ret_B = (df_B['收盘'].iloc[-1] - df_B['收盘'].iloc[-20]) / df_B['收盘'].iloc[-20]
        
        print(f"📊 沪深300 (510300) 近20日涨幅: {ret_A*100:.2f}%")
        print(f"📊 创业板 (159915) 近20日涨幅: {ret_B*100:.2f}%")
        
        if ret_A > ret_B:
            print("🎯 结论：动量轮动系统当前信号 -> 【做多 沪深300】")
        else:
            print("🎯 结论：动量轮动系统当前信号 -> 【做多 创业板】")
            
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")

if __name__ == "__main__":
    check_signal()
