import gradio as gr
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 設定 API 來源 (使用不需要 Key 的 open.er-api)
def get_all_rates():
    try:
        # 以 USD 為基準獲取所有匯率
        response = requests.get("https://open.er-api.com/v6/latest/USD")
        data = response.json()
        if data["result"] == "success":
            return data["rates"]
    except:
        return None
    return None

# 模擬歷史數據用來畫曲線圖
def generate_chart(currency_code, current_rate):
    # 產生過去 24 小時的隨機微幅波動數據
    x = list(range(24))
    y = [current_rate * (1 + np.random.uniform(-0.002, 0.002)) for _ in range(24)]
    y[-1] = current_rate # 最後一點設為當前匯率
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='#636EFA', width=2)))
    fig.update_layout(
        title=f"{currency_code} 趨勢 (對美金)",
        height=180,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showticklabels=False),
        yaxis=dict(showgrid=True)
    )
    return fig

# 計算邏輯
def update_logic(jpy_in_1, jpy_in_2, cny_in_3):
    rates = get_all_rates()
    if not rates:
        # 若失敗回傳預設值
        empty_df = pd.DataFrame(columns=["幣別", "對美金匯率"])
        return 0, 0, 0, 0, empty_df, None, None, None, None
    
    # 取得基礎匯率
    twd_r = rates.get('TWD', 32.5)
    jpy_r = rates.get('JPY', 155.0)
    cny_r = rates.get('CNY', 7.2)
    
    # 計算匯率對
    jpy_to_cny = cny_r / jpy_r
    jpy_to_twd = twd_r / jpy_r
    cny_to_twd = twd_r / cny_r
    
    # 計算換算結果
    # 1. 日幣 -> 人民幣 & 台幣
    res1_cny = jpy_in_1 * jpy_to_cny
    res1_twd = jpy_in_1 * jpy_to_twd
    
    # 2. 日幣 -> 台幣
    res2_twd = jpy_in_2 * jpy_to_twd
    
    # 3. 人民幣 -> 台幣
    res3_twd = cny_in_3 * cny_to_twd
    
    # 表格數據
    df_data = {
        "幣別": ["美金 (USD)", "台幣 (TWD)", "日幣 (JPY)", "人民幣 (CNY)"],
        "對美金匯率": [1.0, round(twd_r, 4), round(jpy_r, 4), round(cny_r, 4)]
    }
    df = pd.DataFrame(df_data)
    
    # 生成圖表
    fig_twd = generate_chart("TWD", twd_r)
    fig_jpy = generate_chart("JPY", jpy_r)
    fig_cny = generate_chart("CNY", cny_r)
    fig_usd = generate_chart("USD", 1.0)
    
    return (
        round(res1_cny, 2), round(res1_twd, 2), 
        round(res2_twd, 2), 
        round(res3_twd, 2),
        df,
        fig_twd, fig_jpy, fig_cny, fig_usd
    )

# 建立 UI
with gr.Blocks(css=".container { max-width: 1200px; margin: auto; }") as demo:
    gr.Markdown("# 💱 即時匯率換算 & 趨勢監控系統")
    
    with gr.Row():
        # 左側：換算與表格
        with gr.Column(scale=2):
            gr.Markdown("### 🧮 換算計算器")
            
            # 第一組：日幣 -> 人民幣 -> 台幣 (3格)
            with gr.Row():
                jpy_val_1 = gr.Number(label="(輸入金額) 日幣 JPY", value=1, interactive=True)
                cny_res_1 = gr.Number(label="(自動運算) 人民幣 CNY", interactive=False)
                twd_res_1 = gr.Number(label="(自動運算) 台幣 TWD", interactive=False)
            
            gr.Markdown("---")
            
            # 第二組：日幣 -> 台幣 (為了對齊，第三格放空白)
            with gr.Row():
                jpy_val_2 = gr.Number(label="(輸入金額) 日幣 JPY", value=1, interactive=True)
                twd_res_2 = gr.Number(label="(自動運算) 台幣 TWD", interactive=False)
                gr.Markdown("") # 替代 Placeholder 用於對齊
                
            gr.Markdown("---")
            
            # 第三組：人民幣 -> 台幣 (為了對齊，第三格放空白)
            with gr.Row():
                cny_val_3 = gr.Number(label="(輸入金額) 人民幣 CNY", value=1, interactive=True)
                twd_res_3 = gr.Number(label="(自動運算) 台幣 TWD", interactive=False)
                gr.Markdown("") # 替代 Placeholder 用於對齊
            
            gr.Markdown("### 📊 即時匯率(表格)")
            table_output = gr.Dataframe(headers=["幣別", "對美金匯率"])

        # 右側：曲線圖
        with gr.Column(scale=1):
            gr.Markdown("### 📈 即時匯率(曲線)")
            plot_twd = gr.Plot(label="台幣")
            plot_jpy = gr.Plot(label="日幣")
            plot_cny = gr.Plot(label="人民幣")
            plot_usd = gr.Plot(label="美金")

    # 定義觸發動作
    inputs = [jpy_val_1, jpy_val_2, cny_val_3]
    outputs = [cny_res_1, twd_res_1, twd_res_2, twd_res_3, table_output, plot_twd, plot_jpy, plot_cny, plot_usd]
    
    # 綁定事件
    for inp in inputs:
        inp.change(fn=update_logic, inputs=inputs, outputs=outputs)
    
    # 頁面載入時執行一次
    demo.load(fn=update_logic, inputs=inputs, outputs=outputs)

if __name__ == "__main__":
    demo.launch()
