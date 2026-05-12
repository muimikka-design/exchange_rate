import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# 確保網址正確且無空格
APP_ICON_URL = "https://raw.githubusercontent.com/muimikka/exchange_rate/main/icon.png"

# 嘗試下載圖片並轉換為 PIL 物件
try:
    response = requests.get(APP_ICON_URL)
    img = Image.open(BytesIO(response.content))
except:
    img = "💰" # 如果下載失敗，用 Emoji 墊後

st.set_page_config(
    page_title="即時匯率換算系統",
    page_icon=img, # 傳入圖片物件
    layout="wide"
)

# 注入 PWA 標籤與 CSS
st.markdown(f"""
    <link rel="apple-touch-icon" href="{APP_ICON_URL}">
    <link rel="icon" href="{APP_ICON_URL}">
    <style>
    .main {{
        background-color: #f8f9fa;
    }}
    .stNumberInput > label {{
        font-weight: bold;
        color: #4a4a4a;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 取得匯率資料 ---
@st.cache_data(ttl=3600)
def get_exchange_rates():
    try:
        # 使用更穩定的 API 備份或原網址
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = response.json()
        if data.get("result") == "success":
            return data["rates"]
    except Exception as e:
        st.error(f"匯率 API 連線失敗: {e}")
    return None

# --- 3. 繪製趨勢圖 ---
def plot_trend_chart(currency_code, rate):
    # 模擬 24 小時數據
    x = list(range(24))
    y = [rate * (1 + np.random.uniform(-0.002, 0.002)) for _ in range(24)]
    y[-1] = rate
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='#636EFA', width=2)))
    fig.update_layout(
        title=f"{currency_code} 趨勢 (對美金)",
        height=180, # 稍微縮小高度增加緊湊感
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showgrid=True, tickformat=".2f"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- 主要 UI ---
st.title("💱 即時匯率換算 & 趨勢監控系統")

rates = get_exchange_rates()

if rates:
    # 取得匯率，若不存在則給予預設值避免報錯
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
        
        # 區塊 1: JPY -> CNY & TWD
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            jpy_1 = st.number_input("輸入日幣 JPY", value=1000.0, step=100.0, key="jpy1")
        with c2:
            st.write("人民幣 CNY")
            st.info(f"¥ {jpy_1 * jpy_to_cny:,.2f}")
        with c3:
            st.write("台幣 TWD")
            st.info(f"NT$ {jpy_1 * jpy_to_twd:,.2f}")

        # 區塊 2: JPY -> TWD (獨立)
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            jpy_2 = st.number_input("輸入日幣 JPY", value=1000.0, step=100.0, key="jpy2")
        with c2:
            st.write("台幣 TWD")
            st.success(f"NT$ {jpy_2 * jpy_to_twd:,.2f}")

        # 區塊 3: CNY -> TWD
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            cny_3 = st.number_input("輸入人民幣 CNY", value=100.0, step=10.0, key="cny3")
        with c2:
            st.write("台幣 TWD")
            st.success(f"NT$ {cny_3 * cny_to_twd:,.2f}")

        st.write("### 📊 即時匯率 (表格)")
        df_data = {
            "幣別": ["美金 (USD)", "台幣 (TWD)", "日幣 (JPY)", "人民幣 (CNY)"],
            "對美金匯率": [1.0, round(twd_r, 4), round(jpy_r, 4), round(cny_r, 4)]
        }
        st.table(pd.DataFrame(df_data))

    with col_right:
        st.subheader("📈 參考趨勢")
        # 繪製圖表
        for code, rate in [("TWD", twd_r), ("JPY", jpy_r), ("CNY", cny_r)]:
            st.plotly_chart(plot_trend_chart(code, rate), use_container_width=True)
else:
    st.error("暫時無法取得即時數據，請檢查網路連線。")
