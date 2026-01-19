import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="국내 주식 분석 대시보드", layout="wide")

# --- 종목 리스트 정의 ---
STOCK_DICT = {
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "LG에너지솔루션": "373220.KS",
    "현대차": "005380.KS", "NAVER": "035420.KS", "카카오": "035720.KS",
    "에코프로": "086520.KQ", "에코프로비엠": "247540.KQ"
}

st.title("📈 국내 주식 날짜별 데이터 분석")

# --- 사이드바 설정 ---
st.sidebar.header("조회 설정")
selected_stock_name = st.sidebar.selectbox("종목 선택", options=list(STOCK_DICT.keys()) + ["직접 입력"])

if selected_stock_name == "직접 입력":
    ticker_input = st.sidebar.text_input("종목 코드 입력 (예: 005930)")
    market_type = st.sidebar.selectbox("시장 선택", [".KS (코스피)", ".KQ (코스닥)"])
    ticker_symbol = ticker_input + market_type.split(" ")[0]
else:
    ticker_symbol = STOCK_DICT[selected_stock_name]

# 데이터 불러오기 범위 (지표 계산을 위해 시작 날짜를 넉넉히 잡음)
end_date = datetime.now()
start_date = st.sidebar.date_input("데이터 조회 시작일", value=end_date - timedelta(days=365))

@st.cache_data
def load_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        return data
    except:
        return None

df = load_data(ticker_symbol, start_date, end_date)

if df is not None and not df.empty:
    # yfinance MultiIndex 대응
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # 1. 날짜 선택 슬라이더 (데이터가 있는 날짜만 선택 가능하도록)
    # 인덱스를 문자열 포맷으로 변환
    available_dates = df.index.strftime('%Y-%m-%d').tolist()
    
    st.info("💡 하단 슬라이더를 조절하여 특정 날짜의 지표를 확인하세요.")
    selected_date_str = st.select_slider(
        "기준 날짜 선택",
        options=available_dates,
        value=available_dates[-1] # 기본값은 가장 최근 날짜
    )

    # 2. 선택된 날짜의 데이터 추출
    selected_idx = available_dates.index(selected_date_str)
    current_data = df.iloc[selected_idx]
    
    # 전일 데이터 추출 (첫 번째 날짜 선택 시 예외 처리)
    if selected_idx > 0:
        prev_data = df.iloc[selected_idx - 1]
        change = current_data['Close'] - prev_data['Close']
        pct_change = (change / prev_data['Close']) * 100
    else:
        change = 0
        pct_change = 0

    # 3. 상단 지표 (선택된 날짜 기준)
    col1, col2, col3 = st.columns(3)
    col1.metric(f"{selected_date_str} 종가", f"{int(current_data['Close']):,} 원")
    col2.metric("전일 대비", f"{int(change):,} 원", f"{pct_change:.2f}%")
    col3.metric("거래량", f"{int(current_data['Volume']):,}")

    # 4. Plotly 차트 (선택된 날짜를 강조하기 위해 수직선 추가 가능)
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="주가"
    )])

    # 선택한 날짜에 수직선 표시 (V-Line)
    fig.add_vline(x=selected_date_str, line_width=2, line_dash="dash", line_color="red")

    fig.update_layout(
        title=f"{selected_stock_name} 주가 추이 (현재 선택: {selected_date_str})",
        yaxis_title="가격 (KRW)",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # 5. 재무제표 확인 탭 (이전 요청 기능 유지)
    with st.expander("재무제표 데이터 보기"):
        ticker_obj = yf.Ticker(ticker_symbol)
        st.dataframe(ticker_obj.financials)
else:
    st.error("데이터를 불러오지 못했습니다.")
