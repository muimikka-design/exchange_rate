import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import os

# --- 1. 頁面設定與本地圖示讀取 ---
# 尋找與此程式碼同資料夾下的 icon.png
icon_path = "icon.png"

if os.path.exists(icon_path):
    try:
        app_icon = Image.open(icon_path)
    except Exception:
        app_icon = "💰"  # 如果圖片損壞，使用 Emoji 備案
else:
    app_icon = "💰"  # 如果沒找到檔案，使用 Emoji 備案

# st.set_page_config 必須是第一個執行的 Streamlit 指令
st.set_page_config(
    page_title="即時匯率換算系統",
    page_icon=app_icon,
    layout="wide"
)


# --- 手機版 Icon 注入 (放在 st.set_page_config 之後) ---

# 這裡必須使用「網址」形式，手機瀏覽器才能在離線或外部抓取到圖示
# 請確保這個 GitHub 連結是有效的
icon_url = "https://raw.githubusercontent.com/muimikka/exchange_rate/main/icon2.png"

st.markdown(f"""
    <head>
        <!-- iOS 設備專用 -->
        <link rel="apple-touch-icon" sizes="180x180" href="{icon_url}">
        <!-- Android 與 Chrome 專用 -->
        <link rel="icon" sizes="1024x1024" href="{icon_url}">
        <!-- 設定 APP 名稱 -->
        <meta name="apple-mobile-web-app-title" content="匯率換算">
        <meta name="apple-mobile-web-app-capable" content="yes">
    </head>
    """, unsafe_allow_html=True)







# --- 2. 取得匯率資料的函數 ---
@st.cache_data(ttl=3600)
def get_exchange_rates():
    try:
        # 使用 Open Exchange Rates 的免費 API 介面
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = response.json()
        if data.get("result") == "success":
            return data["rates"]
    except Exception as e:
        st.error(f"匯率 API 連線失敗: {e}")
    return None

# --- 3. 繪製模擬趨勢圖 ---
def plot_trend_chart(currency_code, rate):
    x = list(range(24))
    # 這裡是用隨機數模擬當日波動，僅供視覺參考
    y = [rate * (1 + np.random.uniform(-0.002, 0.002)) for _ in range(24)]
    y[-1] = rate
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='#636EFA', width=2)))
    fig.update_layout(
        title=f"{currency_code} 近 24h 參考趨勢",
        height=180,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showgrid=True, tickformat=".2f"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- 主要 UI 開始 ---
st.title("💱 即時匯率換算系統")

rates = get_exchange_rates()

if rates:
    # 取得關鍵幣別匯率（對美金）
    twd_r = rates.get('TWD', 32.5)
    jpy_r = rates.get('JPY', 155.0)
    cny_r = rates.get('CNY', 7.2)
    
    # 計算交叉匯率
    jpy_to_cny = cny_r / jpy_r
    jpy_to_twd = twd_r / jpy_r
    cny_to_twd = twd_r / cny_r

    # 畫面佈局：左側計算器，右側趨勢圖
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🧮 快速換算")
        
        # 第一組：日幣轉台幣/人民幣
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            val_jpy1 = st.number_input("輸入日幣 (JPY)", value=1000.0, step=100.0, key="input_jpy1")
        with c2:
            st.write("換算人民幣 (CNY)")
            st.info(f"¥ {val_jpy1 * jpy_to_cny:,.2f}")
        with c3:
            st.write("換算台幣 (TWD)")
            st.info(f"NT$ {val_jpy1 * jpy_to_twd:,.2f}")

        # 第二組：人民幣轉台幣
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            val_cny = st.number_input("輸入人民幣 (CNY)", value=100.0, step=10.0, key="input_cny")
        with c2:
            st.write("換算台幣 (TWD)")
            st.success(f"NT$ {val_cny * cny_to_twd:,.2f}")
        with c3:
            st.empty()

        # 匯率對照表
        st.write("### 📊 目前匯率對照 (對美金)")
        table_df = pd.DataFrame({
            "幣別名稱": ["美金 (USD)", "台幣 (TWD)", "日幣 (JPY)", "人民幣 (CNY)"],
            "匯率數值": [1.0, round(twd_r, 4), round(jpy_r, 4), round(cny_r, 4)]
        })
        st.table(table_df)

    with col_right:
        st.subheader("📈 幣別監控")
        # 顯示各幣別趨勢圖
        st.plotly_chart(plot_trend_chart("TWD", twd_r), use_container_width=True)
        st.plotly_chart(plot_trend_chart("JPY", jpy_r), use_container_width=True)
        st.plotly_chart(plot_trend_chart("CNY", cny_r), use_container_width=True)

else:
    st.error("無法連接到匯率服務，請稍後再試。")

# 注入 CSS 輕微美化
st.markdown("""
    <style>
    .stNumberInput label { font-size: 1.1rem; color: #1f77b4; }
    .stInfo, .stSuccess { font-size: 1.2rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
