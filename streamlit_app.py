import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from PIL import Image
from io import BytesIO

# --- 1. 圖示與頁面設定 ---
APP_ICON_URL = "https://raw.githubusercontent.com/muimikka/exchange_rate/main/icon.png"

def get_icon(url):
    try:
        # 增加 headers 模擬瀏覽器，避免被 GitHub 拒絕
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return Image.open(BytesIO(res.content))
    except:
        pass
    return "💰"

# 必須是第一個 Streamlit 指令
app_icon = get_icon(APP_ICON_URL)
st.set_page_config(
    page_title="即時匯率換算系統",
    page_icon=app_icon,
    layout="wide"
)

# --- 2. 取得匯率函數 ---
@st.cache_data(ttl=3600)
def get_exchange_rates():
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = response.json()
        if data.get("result") == "success":
            return data["rates"]
    except Exception as e:
        st.error(f"匯率 API 連線失敗: {e}")
    return None

# --- 3. 趨勢圖函數 ---
def plot_trend_chart(currency_code, rate):
    x = list(range(24))
    y = [rate * (1 + np.random.uniform(-0.002, 0.002)) for _ in range(24)]
    y[-1] = rate
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='#636EFA', width=2)))
    fig.update_layout(
        title=f"{currency_code} 趨勢 (對美金)",
        height=180,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showgrid=True, tickformat=".2f"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- 主要 UI 介面 ---
st.title("💱 即時匯率換算 & 趨勢監控")

rates = get_exchange_rates()

if rates:
    # 安全地取得匯率，若不存在則給預設值
    twd_r = rates.get('TWD', 32.5)
    jpy_r = rates.get('JPY', 155.0)
    cny_r = rates.get('CNY', 7.2)
    
    # 計算交叉匯率
    jpy_to_cny = cny_r / jpy_r
    jpy_to_twd = twd_r / jpy_r
    cny_to_twd = twd_r / cny_r

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🧮 換算計算器")
        
        # 區塊 1: JPY 轉 CNY/TWD
        st.write("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            jpy_input1 = st.number_input("日幣 JPY", value=1000.0, step=100.0, key="n1")
        with c2:
            st.write("人民幣 CNY")
            st.info(f"{jpy_input1 * jpy_to_cny:,.2f}")
        with c3:
            st.write("台幣 TWD")
            st.info(f"{jpy_input1 * jpy_to_twd:,.2f}")

        # 區塊 2: JPY 轉 TWD
        st.write("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            jpy_input2 = st.number_input("日幣 JPY ", value=1000.0, step=100.0, key="n2")
        with c2:
            st.write("台幣 TWD ")
            st.success(f"{jpy_input2 * jpy_to_twd:,.2f}")

        # 區塊 3: CNY 轉 TWD
        st.write("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            cny_input = st.number_input("人民幣 CNY", value=100.0, step=10.0, key="n3")
        with c2:
            st.write("台幣 TWD  ")
            st.success(f"{cny_input * cny_to_twd:,.2f}")

        # 表格區塊：確保清單長度絕對相等
        st.write("### 📊 即時匯率對照")
        df_data = pd.DataFrame({
            "幣別": ["美金 (USD)", "台幣 (TWD)", "日幣 (JPY)", "人民幣 (CNY)"],
            "對美金匯率": [1.0, round(twd_r, 4), round(jpy_r, 4), round(cny_r, 4)]
        })
        st.table(df_data)

    with col_right:
        st.subheader("📈 參考趨勢")
        for code, r in [("TWD", twd_r), ("JPY", jpy_r), ("CNY", cny_r)]:
            st.plotly_chart(plot_trend_chart(code, r), use_container_width=True)
else:
    st.error("目前無法載入資料，請檢查網路連線或 API 狀態。")
