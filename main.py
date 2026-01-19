import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="국내 주식 시각화 대시보드", layout="wide")

# --- 종목 리스트 정의 ---
# 종목명과 티커 심볼(yfinance 기준) 매핑
STOCK_DICT = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대차": "005380.KS",
    "기아": "000270.KS",
    "셀트리온": "068270.KS",
    "POSCO홀딩스": "005490.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "에코프로": "086520.KQ",
    "에코프로비엠": "247540.KQ"
}

st.title("📈 국내 주요 주식 데이터 시각화")

# --- 사이드바 설정 ---
st.sidebar.header("조회 설정")

# 1. 종목 선택 (Selectbox)
selected_stock_name = st.sidebar.selectbox(
    "종목을 선택하세요", 
    options=list(STOCK_DICT.keys()) + ["직접 입력"]
)

# 2. 종목 코드 결정
if selected_stock_name == "직접 입력":
    ticker_input = st.sidebar.text_input("종목 코드 입력 (예: 005930)")
    market_type = st.sidebar.selectbox("시장 선택", [".KS (코스피)", ".KQ (코스닥)"])
    ticker_symbol = ticker_input + market_type.split(" ")[0]
else:
    ticker_symbol = STOCK_DICT[selected_stock_name]
    st.sidebar.info(f"선택된 코드: {ticker_symbol}")

# 3. 날짜 범위 설정
end_date = datetime.now()
start_date = st.sidebar.date_input("시작 날짜", value=end_date - timedelta(days=365))

# --- 데이터 로드 및 시각화 ---
@st.cache_data
def load_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        return data
    except Exception:
        return None

if ticker_symbol:
    df = load_data(ticker_symbol, start_date, end_date)

    if df is not None and not df.empty:
        # yfinance 최신 버전의 MultiIndex 대응
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 상단 지표 (Metric)
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change = last_close - prev_close
        pct_change = (change / prev_close) * 100

        col1, col2, col3 = st.columns(3)
        col1.metric("현재가 (종가)", f"{int(last_close):,} 원")
        col2.metric("전일 대비", f"{int(change):,} 원", f"{pct_change:.2f}%")
        col3.metric("거래량", f"{int(df['Volume'].iloc[-1]):,}")

        # Plotly 차트
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="주가"
        )])

        fig.update_layout(
            title=f"{selected_stock_name if selected_stock_name != '직접 입력' else ticker_symbol} 주가 추이",
            yaxis_title="가격 (KRW)",
            xaxis_rangeslider_visible=True,
            template="plotly_white",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("데이터를 불러올 수 없습니다. 코드나 날짜를 확인해 주세요.")
