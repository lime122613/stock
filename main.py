import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="국내 주식 시각화", layout="wide")

# 1. 날짜 처리 수정: .date()를 사용하여 시간 정보를 제거합니다.
today = datetime.now().date() 

st.sidebar.header("조회 설정")
# 시작 날짜 선택 (기본값: 1년 전)
start_date = st.sidebar.date_input("시작 날짜", value=today - timedelta(days=365))
# 종료 날짜도 선택 가능하게 변경 (기본값: 오늘)
end_date = st.sidebar.date_input("종료 날짜", value=today)

# 종목 선택 부분 (이전 코드와 동일)
STOCK_DICT = {"삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "NAVER": "035420.KS"}
selected_stock = st.sidebar.selectbox("종목 선택", options=list(STOCK_DICT.keys()))
ticker_symbol = STOCK_DICT[selected_stock]

# 2. 캐시 함수 수정: 인자값이 바뀌면 즉시 새로 로드함
@st.cache_data(ttl=3600) # 1시간마다 캐시 자동 만료 설정
def load_data(ticker, start, end):
    # yfinance는 문자열 형태의 날짜(YYYY-MM-DD)를 가장 잘 인식합니다.
    data = yf.download(ticker, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
    return data

if start_date >= end_date:
    st.error("시작 날짜는 종료 날짜보다 빨라야 합니다.")
else:
    df = load_data(ticker_symbol, start_date, end_date)

    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 차트 제목에 조회 기간 표시 (변경 확인용)
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
        )])
        
        fig.update_layout(
            title=f"{selected_stock} ({start_date} ~ {end_date})",
            xaxis_rangeslider_visible=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 데이터가 실제로 바뀌었는지 표로 확인
        st.write(f"조회된 데이터 행 수: {len(df)}개")
    else:
        st.info("해당 기간의 데이터가 없습니다.")

# 이동평균 계산
df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA60'] = df['Close'].rolling(window=60).mean()

# 차트에 추가
fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='20일선', line=dict(color='orange', width=1)))
fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name='60일선', line=dict(color='blue', width=1)))
