import efinance as ef
import pandas as pd

def check_signal():
    print("🚀 正在通过 efinance 获取 A 股真实数据...")
    try:
        # 获取沪深300(510300)和创业板(159915)的最新行情
        # efinance 的接口非常稳，直接取近 60 天数据
        codes = ['510300', '159915']
        
        results = {}
        for code in codes:
            df = ef.stock.get_quote_history(code)
            # 计算 20 日涨幅 (今天收盘价 vs 20天前收盘价)
            close_now = df['收盘'].iloc[-1]
            close_before = df['收盘'].iloc[-20]
            ret = (close_now - close_before) / close_before
            results[code] = ret
            print(f"📊 资产 {code} 近20日涨幅: {ret*100:.2f}%")
        
        if results['510300'] > results['159915']:
            print("\n🎯 结论：动量轮动系统当前信号 -> 【做多 沪深300】")
        else:
            print("\n🎯 结论：动量轮动系统当前信号 -> 【做多 创业板】")
            
    except Exception as e:
        print(f"❌ 数据获取失败，报错详情: {e}")

if __name__ == "__main__":
    check_signal()
