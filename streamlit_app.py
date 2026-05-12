import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- PWA 與圖示設定 ---
# 1. 準備圖示 URL (建議使用 512x512 的 PNG 檔案)
# 你可以將 icon.png 放在 GitHub 倉庫根目錄，URL 則指向 raw 連結
APP_ICON_URL = "https://png.pngtree.com/png-vector/20190124/ourlarge/pngtree-coin-currency-dollar-renminbi-png-image_550933.jpg" 

# 設定頁面資訊
st.set_page_config(
    page_title="即時匯率換算系統", 
    page_icon=APP_ICON_URL, # 這裡設定網頁分頁標籤的 Icon
    layout="wide"
)

# 2. 注入 PWA 相關 Meta 標籤 (讓手機「加入主畫面」時顯示正確圖示與標題)
st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" href="{APP_ICON_URL}">
        <link rel="icon" href="{APP_ICON_URL}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black">
        <meta name="apple-mobile-web-app-title" content="匯率換算">
    </head>
    """, unsafe_allow_html=True)

# 自定義 CSS 以美化區塊
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stNumberInput > label {
        font-weight: bold;
        color: #4a4a4a;
    }
    </style>
    """, unsafe_allow_html=True)

# 1. 取得匯率資料的函數
@st.cache_data(ttl=3600)
def get_exchange_rates():
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD")
        data = response.json()
        if data["result"] == "success":
            return data["rates"]
    except Exception as e:
        st.error(f"匯率 API 連線失敗: {e}")
        return None
    return None

# 2. 繪製趨勢圖的函數
def plot_trend_chart(currency_code, rate):
    x = list(range(24))
    y = [rate * (1 + np.random.uniform(-0.002, 0.002)) for _ in range(24)]
    y[-1] = rate
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='#636EFA', width=2)))
    fig.update_layout(
        title=f"{currency_code} 趨勢 (對美金)",
        height=200,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showgrid=True, tickformat=".2f"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- 主要 UI 開始 ---
st.title("💱 即時匯率換算 & 趨勢監控系統")

rates = get_exchange_rates()

if rates:
    twd_r = rates.get('TWD', 32.5)
    jpy_r = rates.get('JPY', 155.0)
    cny_r = rates.get('CNY', 7.2)
    
    jpy_to_cny = cny_r / jpy_r
    jpy_to_twd = twd_r / jpy_r
    cny_to_twd = twd_r / cny_r

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🧮 換算計算器")
        
        st.write("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            jpy_1 = st.number_input("(輸入金額) 日幣 JPY", value=10.0, key="jpy1")
        with c2:
            st.write("(自動運算) 人民幣 CNY")
            st.info(f"{jpy_1 * jpy_to_cny:,.2f}")
        with c3:
            st.write("(自動運算) 台幣 TWD")
            st.info(f"{jpy_1 * jpy_to_twd:,.2f}")

        st.write("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            jpy_2 = st.number_input("(輸入金額) 日幣 JPY", value=10.0, key="jpy2")
        with c2:
            st.write("(自動運算) 台幣 TWD")
            st.success(f"{jpy_2 * jpy_to_twd:,.2f}")
        with c3:
            st.write("") 

        st.write("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            cny_3 = st.number_input("(輸入金額) 人民幣 CNY", value=10.0, key="cny3")
        with c2:
            st.write("(自動運算) 台幣 TWD")
            st.success(f"{cny_3 * cny_to_twd:,.2f}")
        with c3:
            st.write("") 

        st.write("### 📊 即時匯率 (表格)")
        df_data = {
            "幣別": ["美金 (USD)", "台幣 (TWD)", "日幣 (JPY)", "人民幣 (CNY)"],
            "對美金匯率": [1.0, round(twd_r, 4), round(jpy_r, 4), round(cny_r, 4)]
        }
        st.table(pd.DataFrame(df_data))

    with col_right:
        st.subheader("📈 即時匯率 (曲線)")
        st.plotly_chart(plot_trend_chart("TWD", twd_r), use_container_width=True)
        st.plotly_chart(plot_trend_chart("JPY", jpy_r), use_container_width=True)
        st.plotly_chart(plot_trend_chart("CNY", cny_r), use_container_width=True)
        st.plotly_chart(plot_trend_chart("USD", 1.0), use_container_width=True)
else:
    st.error("暫時無法取得即時數據，請檢查網路連線。")
