import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="국내 주식 시각화 대시보드", layout="wide")

st.title("📈 국내 주식 데이터 시각화")
st.markdown(f"현재 날짜: {datetime.now().strftime('%Y-%m-%d')}")

# 사이드바: 설정 및 입력
st.sidebar.header("조회 설정")
stock_code = st.sidebar.text_input("종목 코드 입력 (예: 005930)", value="005930")
market_type = st.sidebar.selectbox("시장 선택", ["KOSPI (.KS)", "KOSDAQ (.KQ)"])

# 티커 심볼 완성
suffix = ".KS" if "KOSPI" in market_type else ".KQ"
ticker_symbol = stock_code + suffix

# 날짜 범위 설정
end_date = datetime.now()
start_date = st.sidebar.date_input("시작 날짜", value=end_date - timedelta(days=365))

# 데이터 불러오기
@st.cache_data
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data

try:
    df = load_data(ticker_symbol, start_date, end_date)

    if df.empty:
        st.error("데이터를 불러오지 못했습니다. 종목 코드나 시장 선택을 확인해주세요.")
    else:
        # 데이터프레임의 인덱스가 MultiIndex인 경우 처리 (yfinance 최신 버전 대응)
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

        # Plotly 캔들스틱 차트
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="주가"
        )])

        fig.update_layout(
            title=f"{ticker_symbol} 주가 추이",
            yaxis_title="가격 (KRW)",
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        # 데이터 표 표시
        with st.expander("Raw 데이터 보기"):
            st.dataframe(df.sort_index(ascending=False))

except Exception as e:
    st.warning(f"오류가 발생했습니다: {e}")
