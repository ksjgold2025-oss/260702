import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="쌍둥이 지역 찾기", layout="wide")

st.title("👥 우리 동네와 인구 구조가 가장 비슷한 '쌍둥이 지역' 찾기")

# 데이터 로드
@st.cache_data
def load_data():
    # 행정안전부 CSV 인코딩은 보통 cp949입니다.
    df = pd.read_csv('202606_202606_연령별인구현황_월간.csv', encoding='cp949')
    
    # 컬럼 정리: 행정구역명을 인덱스로 설정
    # 보통 0번째 컬럼은 행정구역, 1번째는 총인구수입니다.
    df = df.set_index(df.columns[0])
    
    # 인구 수 컬럼만 추출 (숫자가 아닌 컬럼 제외, 예: '총인구수' 등)
    # 0세부터 100세 이상까지의 데이터만 추출
    data = df.iloc[:, 2:] 
    
    # 데이터를 비율로 변환 (인구 규모와 상관없이 구조만 비교하기 위함)
    data_ratio = data.div(data.sum(axis=1), axis=0)
    
    return data, data_ratio

try:
    df, df_ratio = load_data()
    
    # 사이드바: 기준 지역 선택
    target_region = st.sidebar.selectbox("나의 거주 지역을 선택하세요:", df.index)
    
    if target_region:
        # 쌍둥이 지역 찾기 (유클리드 거리 기반)
        target_vec = df_ratio.loc[target_region]
        
        # 다른 모든 지역과의 차이 계산
        dist = np.sqrt(((df_ratio - target_vec) ** 2).sum(axis=1))
        
        # 자기 자신 제외 후 최소 거리 지역 찾기
        dist = dist.drop(target_region)
        twin_region = dist.idxmin()
        min_dist = dist.min()
        
        st.success(f"당신이 선택한 '{target_region}'과 인구 구조가 가장 비슷한 쌍둥이 지역은 **'{twin_region}'** 입니다.")
        st.info(f"유사도 지표(거리): {min_dist:.4f} (0에 가까울수록 매우 유사)")
        
        # 시각화
        fig = go.Figure()
        
        # 타겟 지역 데이터 추가
        fig.add_trace(go.Scatter(
            x=df_ratio.columns, y=df_ratio.loc[target_region],
            mode='lines', name=target_region, line=dict(color='blue', width=3)
        ))
        
        # 쌍둥이 지역 데이터 추가
        fig.add_trace(go.Scatter(
            x=df_ratio.columns, y=df_ratio.loc[twin_region],
            mode='lines', name=twin_region, line=dict(color='red', width=3, dash='dash')
        ))
        
        fig.update_layout(
            title="인구 구조 비교 (연령별 비율)",
            xaxis_title="연령",
            yaxis_title="비율",
            hovermode="x unified",
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 상세 데이터 비교
        st.write("### 인구 구성 상세")
        comp_df = pd.DataFrame({
            target_region: df_ratio.loc[target_region],
            twin_region: df_ratio.loc[twin_region]
        })
        st.dataframe(comp_df.style.format("{:.2%}"))

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.write("CSV 파일의 구조나 인코딩을 확인해주세요.")
