import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="국내 주식 & 재무 분석", layout="wide")

# --- 종목 리스트 ---
STOCK_DICT = {
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "LG에너지솔루션": "373220.KS",
    "현대차": "005380.KS", "NAVER": "035420.KS", "카카오": "035720.KS",
    "에코프로비엠": "247540.KQ", "셀트리온": "068270.KS"
}

st.title("📊 국내 주식 통합 분석 대시보드")

# --- 사이드바 ---
st.sidebar.header("설정")
selected_name = st.sidebar.selectbox("종목 선택", options=list(STOCK_DICT.keys()))
ticker_symbol = STOCK_DICT[selected_name]

today = datetime.now().date()
start_date = st.sidebar.date_input("차트 시작 날짜", value=today - timedelta(days=365))

# --- 데이터 로드 함수 ---
@st.cache_data
def get_stock_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    return df

@st.cache_data
def get_financial_data(ticker):
    stock = yf.Ticker(ticker)
    # yfinance에서 제공하는 재무제표 데이터들
    income = stock.financials        # 손익계산서
    balance = stock.balance_sheet    # 재무상태표
    cashflow = stock.cashflow        # 현금흐름표
    return income, balance, cashflow

# --- 메인 화면 레이아웃 (탭 활용) ---
tab1, tab2 = st.tabs(["📈 주가 차트", "📑 재무제표"])

# 데이터 가져오기
df = get_stock_data(ticker_symbol, start_date, today)
income, balance, cashflow = get_financial_data(ticker_symbol)

# [탭 1: 주가 차트]
with tab1:
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"
        )])
        fig.update_layout(title=f"{selected_name} 주가 추이", xaxis_rangeslider_visible=True, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("주가 데이터를 불러올 수 없습니다.")

# [탭 2: 재무제표]
with tab2:
    st.subheader(f"🔍 {selected_name} 기업 재무 정보")
    
    # 세부 탭으로 재무제표 구분
    f_tab1, f_tab2, f_tab3 = st.tabs(["손익계산서", "재무상태표", "현금흐름표"])
    
    with f_tab1:
        st.write("#### 연간 손익계산서 (Income Statement)")
        if not income.empty:
            st.dataframe(income, use_container_width=True)
        else:
            st.warning("제공되는 손익계산서 데이터가 없습니다.")

    with f_tab2:
        st.write("#### 연간 재무상태표 (Balance Sheet)")
        if not balance.empty:
            st.dataframe(balance, use_container_width=True)
        else:
            st.warning("제공되는 재무상태표 데이터가 없습니다.")

    with f_tab3:
        st.write("#### 연간 현금흐름표 (Cash Flow)")
        if not cashflow.empty:
            st.dataframe(cashflow, use_container_width=True)
        else:
            st.warning("제공되는 현금흐름표 데이터가 없습니다.")

    st.info("※ 데이터는 Yahoo Finance 기준이며, 국내 기업의 경우 최근 분기 데이터 반영이 늦을 수 있습니다.")
