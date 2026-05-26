from datetime import datetime

import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium


st.set_page_config(
    page_title="Nocturnal PGIS",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
* {
  font-family: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
}
.stApp {
  background:
    linear-gradient(135deg, rgba(14, 23, 42, 0.98), rgba(29, 38, 57, 0.96) 48%, rgba(12, 31, 37, 0.98));
  color: #f8fafc;
}
.block-container {
  max-width: 1380px;
  padding-top: 1.25rem;
  padding-bottom: 2.25rem;
}
[data-testid="stSidebar"] {
  background: rgba(9, 17, 30, 0.95);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}
.hero {
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: linear-gradient(135deg, rgba(20, 184, 166, 0.18), rgba(244, 114, 91, 0.13));
  border-radius: 8px;
  padding: 26px 28px;
  margin-bottom: 18px;
  box-shadow: 0 18px 52px rgba(0, 0, 0, 0.28);
}
.hero h1 {
  font-size: 2.75rem;
  line-height: 1.08;
  margin: 0;
  letter-spacing: 0;
}
.hero p {
  color: #d9e4ec;
  font-size: 1.02rem;
  margin: 12px 0 0;
  max-width: 880px;
}
.place-card {
  background: rgba(255, 255, 255, 0.075);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 18px;
  margin: 10px 0;
  box-shadow: 0 14px 38px rgba(0, 0, 0, 0.18);
}
.place-title {
  font-size: 1.22rem;
  font-weight: 800;
  margin-bottom: 8px;
}
.badge {
  display: inline-block;
  padding: 4px 9px;
  margin: 3px 4px 3px 0;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.18);
  border: 1px solid rgba(203, 213, 225, 0.22);
  color: #f8fafc;
  font-size: 0.8rem;
}
.status-open {
  background: rgba(20, 184, 166, 0.22);
  color: #a7fff4;
  border-color: rgba(45, 212, 191, 0.42);
}
.status-soon {
  background: rgba(245, 158, 11, 0.18);
  color: #fde68a;
  border-color: rgba(245, 158, 11, 0.38);
}
.status-closed {
  background: rgba(248, 113, 113, 0.16);
  color: #fecaca;
  border-color: rgba(248, 113, 113, 0.36);
}
.small-muted {
  color: #cbd5e1;
  font-size: 0.92rem;
}
.section-title {
  font-size: 1.35rem;
  font-weight: 800;
  margin: 18px 0 10px;
}
div[data-testid="stMetric"] {
  background: rgba(255, 255, 255, 0.075);
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.11);
}
</style>
""",
    unsafe_allow_html=True,
)


PLACES = [
    {
        "name": "문라이트 루프탑",
        "category": "카페/바",
        "lat": 37.5559,
        "lon": 126.9237,
        "area": "홍대",
        "open": 18,
        "close": 2,
        "is24": False,
        "rating": 4.7,
        "reviews": 328,
        "price": "3-5만원",
        "crowd": "보통",
        "noise": "활기참",
        "tags": ["루프탑", "야경", "DJ 세트", "칵테일"],
        "activities": ["라이브 DJ", "시그니처 칵테일", "야경 사진"],
        "group": ["2명", "3-5명"],
        "mood": ["활기찬", "실외", "대화"],
        "weather": ["맑음", "더운 날"],
        "scores": [4.8, 4.5, 4.1, 4.3, 4.6],
        "trend": [4.4, 4.5, 4.6, 4.7, 4.7, 4.8],
    },
    {
        "name": "온앤온 보드게임 카페",
        "category": "카페",
        "lat": 37.5572,
        "lon": 126.9254,
        "area": "홍대",
        "open": 13,
        "close": 5,
        "is24": False,
        "rating": 4.5,
        "reviews": 211,
        "price": "1-3만원",
        "crowd": "여유",
        "noise": "보통",
        "tags": ["보드게임", "단체", "프라이빗 룸"],
        "activities": ["보드게임 대여", "단체 이벤트", "음료 무제한"],
        "group": ["3-5명", "6명 이상"],
        "mood": ["조용한", "실내", "대화"],
        "weather": ["흐림", "비", "추운 날"],
        "scores": [4.2, 4.6, 4.7, 4.4, 4.3],
        "trend": [4.1, 4.2, 4.3, 4.4, 4.5, 4.5],
    },
    {
        "name": "심야 스터디 라운지",
        "category": "스터디카페",
        "lat": 37.4983,
        "lon": 127.0276,
        "area": "강남",
        "open": 0,
        "close": 24,
        "is24": True,
        "rating": 4.6,
        "reviews": 189,
        "price": "1만원 이하",
        "crowd": "여유",
        "noise": "조용한",
        "tags": ["24시간", "콘센트", "수면실"],
        "activities": ["집중 작업", "회의룸", "프린트"],
        "group": ["혼자", "2명"],
        "mood": ["조용한", "실내", "작업"],
        "weather": ["흐림", "비", "추운 날", "더운 날"],
        "scores": [4.7, 4.4, 4.8, 4.6, 4.4],
        "trend": [4.3, 4.4, 4.5, 4.5, 4.6, 4.6],
    },
    {
        "name": "VR 아케이드 배틀존",
        "category": "오락시설",
        "lat": 37.5008,
        "lon": 127.0261,
        "area": "강남",
        "open": 16,
        "close": 3,
        "is24": False,
        "rating": 4.3,
        "reviews": 154,
        "price": "1-3만원",
        "crowd": "혼잡",
        "noise": "시끌벅적",
        "tags": ["VR존", "PC방", "게임 대전"],
        "activities": ["VR 슈팅", "e스포츠 좌석", "콘솔 게임"],
        "group": ["2명", "3-5명", "6명 이상"],
        "mood": ["활기찬", "실내", "대화"],
        "weather": ["흐림", "비", "더운 날"],
        "scores": [4.4, 4.1, 4.2, 4.0, 4.5],
        "trend": [4.0, 4.1, 4.2, 4.2, 4.3, 4.3],
    },
    {
        "name": "한강 선셋 피크닉",
        "category": "야외공간",
        "lat": 37.5285,
        "lon": 126.9328,
        "area": "여의도",
        "open": 18,
        "close": 1,
        "is24": False,
        "rating": 4.8,
        "reviews": 402,
        "price": "1만원 이하",
        "crowd": "보통",
        "noise": "보통",
        "tags": ["한강", "야경", "배달 가능"],
        "activities": ["돗자리 대여", "야경 산책", "푸드트럭"],
        "group": ["혼자", "2명", "3-5명"],
        "mood": ["조용한", "실외", "산책"],
        "weather": ["맑음", "더운 날"],
        "scores": [4.9, 4.2, 4.8, 4.3, 4.7],
        "trend": [4.5, 4.6, 4.7, 4.7, 4.8, 4.8],
    },
    {
        "name": "블루 사우나 스파",
        "category": "찜질방/스파",
        "lat": 37.5610,
        "lon": 127.0370,
        "area": "왕십리",
        "open": 0,
        "close": 24,
        "is24": True,
        "rating": 4.2,
        "reviews": 97,
        "price": "1-3만원",
        "crowd": "여유",
        "noise": "조용한",
        "tags": ["24시간", "사우나", "수면실"],
        "activities": ["찜질방", "안마의자", "심야 식당"],
        "group": ["혼자", "2명", "3-5명"],
        "mood": ["조용한", "실내", "휴식"],
        "weather": ["비", "추운 날"],
        "scores": [4.0, 4.2, 4.5, 4.1, 4.0],
        "trend": [4.0, 4.0, 4.1, 4.2, 4.2, 4.2],
    },
]

WEATHER_RULES = {
    "맑음": "야외 경관이 좋은 루프탑, 한강, 산책형 장소를 우선 추천합니다.",
    "흐림": "날씨 영향을 덜 받는 실내 복합문화공간과 보드게임 카페를 우선 추천합니다.",
    "비": "이동 부담이 적고 오래 머물 수 있는 실내 장소를 우선 추천합니다.",
    "추운 날": "스터디카페, 스파, 사우나처럼 실내 체류감이 좋은 장소를 우선 추천합니다.",
    "더운 날": "냉방이 잘 되는 실내 공간과 밤바람을 활용할 수 있는 야외 장소를 함께 추천합니다.",
}

STATUS_ORDER = {"영업 중": 0, "마감 임박": 1, "영업 종료": 2}
STATUS_CLASS = {
    "영업 중": "status-open",
    "마감 임박": "status-soon",
    "영업 종료": "status-closed",
}


def badge(text, klass=""):
    return f'<span class="badge {klass}">{text}</span>'


def get_status(place, hour):
    if place["is24"]:
        return "영업 중"

    open_hour = place["open"]
    close_hour = place["close"]
    is_open = (
        open_hour <= hour < close_hour
        if close_hour > open_hour
        else hour >= open_hour or hour < close_hour
    )

    if not is_open:
        return "영업 종료"

    normalized_close = close_hour if close_hour > open_hour else close_hour + 24
    normalized_hour = hour if hour >= open_hour else hour + 24
    if normalized_close - normalized_hour <= 1:
        return "마감 임박"
    return "영업 중"


def score_place(place, group, budget, mood, space, weather, radius):
    score = place["rating"] * 12
    if group in place["group"]:
        score += 15
    if budget == place["price"]:
        score += 12
    if mood in place["mood"]:
        score += 10
    if space in place["mood"]:
        score += 10
    if weather in place["weather"]:
        score += 18
    if radius in ["2km", "5km"] or place["area"] in ["홍대", "강남"]:
        score += 4
    if place["crowd"] == "여유":
        score += 3
    return round(min(score, 100), 1)


def format_hours(place):
    if place["is24"]:
        return "24시간"
    open_text = f"{place['open']:02d}:00"
    close_text = "24:00" if place["close"] == 24 else f"{place['close']:02d}:00"
    return f"{open_text} - {close_text}"


st.markdown(
    """
<div class="hero">
  <h1>야간 활동 장소 추천 PGIS</h1>
  <p>
    시간, 날씨, 인원, 예산, 공간 선호를 바탕으로 심야에 갈 만한 장소를 추천합니다.
    지도 기반 위치 확인, 실시간 영업 상태, 리뷰 신뢰도와 평점 추이를 한 화면에서 볼 수 있습니다.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("조건 설정")
    now_hour = st.slider("현재 시간", 0, 23, datetime.now().hour)
    weather = st.selectbox("날씨", list(WEATHER_RULES.keys()))
    group = st.selectbox("인원 구성", ["혼자", "2명", "3-5명", "6명 이상"])
    age = st.selectbox("연령대", ["20대 초반", "20대 후반", "30대"])
    gender = st.selectbox("성별 구성", ["혼성", "여성", "남성"])
    mood = st.radio("선호 분위기", ["조용한", "활기찬"], horizontal=True)
    space = st.radio("공간 선호", ["실내", "실외"], horizontal=True)
    budget = st.select_slider(
        "예산",
        options=["1만원 이하", "1-3만원", "3-5만원", "5만원 이상"],
        value="1-3만원",
    )
    radius = st.selectbox("검색 반경", ["500m", "1km", "2km", "5km"], index=2)
    categories = sorted({place["category"] for place in PLACES})
    category_filter = st.multiselect("카테고리", categories, default=categories)

places = []
for place in PLACES:
    if place["category"] not in category_filter:
        continue
    item = place.copy()
    item["status"] = get_status(item, now_hour)
    item["status_class"] = STATUS_CLASS[item["status"]]
    item["recommend_score"] = score_place(
        item, group, budget, mood, space, weather, radius
    )
    places.append(item)

places = sorted(
    places,
    key=lambda item: (STATUS_ORDER[item["status"]], -item["recommend_score"], -item["rating"]),
)
df = pd.DataFrame(places)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("추천 장소", f"{len(df)}곳")
metric_2.metric(
    "현재 영업 중",
    f"{df['status'].eq('영업 중').sum()}곳" if not df.empty else "0곳",
)
metric_3.metric("평균 평점", f"{df['rating'].mean():.1f}" if not df.empty else "-")
metric_4.metric("현재 날씨", weather)
st.info(WEATHER_RULES[weather])

tab_map, tab_recommend, tab_detail, tab_review = st.tabs(
    ["지도", "추천 리스트", "장소 상세", "리뷰/평판"]
)

with tab_map:
    map_col, rank_col = st.columns([1.35, 0.65])
    with map_col:
        fmap = folium.Map(
            location=[37.535, 126.99],
            zoom_start=12,
            tiles="CartoDB dark_matter",
        )
        for place in places:
            marker_color = {
                "영업 중": "green",
                "마감 임박": "orange",
                "영업 종료": "red",
            }[place["status"]]
            popup = (
                f"<b>{place['name']}</b><br>"
                f"{place['category']} · 평점 {place['rating']}<br>"
                f"{place['status']}<br>"
                f"추천 점수 {place['recommend_score']}"
            )
            folium.CircleMarker(
                [place["lat"], place["lon"]],
                radius=10,
                color=marker_color,
                fill=True,
                fill_opacity=0.82,
                popup=popup,
            ).add_to(fmap)
        st_folium(fmap, height=560, width=900)

    with rank_col:
        st.markdown('<div class="section-title">실시간 추천 Top 5</div>', unsafe_allow_html=True)
        if not places:
            st.warning("선택한 카테고리에 해당하는 장소가 없습니다.")
        for index, place in enumerate(places[:5], start=1):
            st.markdown(
                f"""
                <div class="place-card">
                  <div class="place-title">{index}. {place['name']}</div>
                  {badge(place['status'], place['status_class'])}
                  {badge(place['category'])}
                  {badge(place['price'])}
                  <div class="small-muted">
                    평점 {place['rating']} · 리뷰 {place['reviews']}개 · 추천 점수 {place['recommend_score']}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with tab_recommend:
    if not places:
        st.warning("필터 조건을 완화하면 더 많은 장소를 볼 수 있습니다.")
    for place in places:
        st.markdown(
            f"""
            <div class="place-card">
              <div class="place-title">{place['name']} <span class="small-muted">· {place['area']}</span></div>
              {badge(place['status'], place['status_class'])}
              {badge(place['category'])}
              {badge(place['crowd'])}
              {badge(place['noise'])}
              {badge(place['price'])}
              <p class="small-muted">
                추천 점수 <b>{place['recommend_score']}</b> · 평점 {place['rating']} · 리뷰 {place['reviews']}개 · 운영 {format_hours(place)}
              </p>
              <p>{' '.join(badge(tag) for tag in place['tags'])}</p>
              <p><b>주요 활동</b> · {', '.join(place['activities'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab_detail:
    if not places:
        st.warning("표시할 장소가 없습니다.")
    else:
        selected = st.selectbox("상세 확인 장소", [place["name"] for place in places])
        place = next(item for item in places if item["name"] == selected)
        detail_col, chart_col = st.columns([0.9, 1.1])

        with detail_col:
            st.markdown(f"### {place['name']}")
            st.write(f"{place['category']} · {place['area']} · {format_hours(place)}")
            st.markdown(" ".join(badge(tag) for tag in place["tags"]), unsafe_allow_html=True)
            st.write("**시설/활동**", ", ".join(place["activities"]))
            st.write("**추천 대상**", f"{group} · {age} · {gender} · {mood}/{space}")
            st.progress(
                min(place["recommend_score"] / 100, 1.0),
                text=f"추천 적합도 {place['recommend_score']}점",
            )

        with chart_col:
            radar = go.Figure()
            radar.add_trace(
                go.Scatterpolar(
                    r=place["scores"],
                    theta=["분위기", "서비스", "가성비", "청결", "접근성"],
                    fill="toself",
                    name=place["name"],
                )
            )
            radar.update_layout(
                height=330,
                margin=dict(l=30, r=30, t=30, b=30),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                polar=dict(radialaxis=dict(range=[0, 5], color="white")),
                showlegend=False,
            )
            st.plotly_chart(radar, use_container_width=True)

        trend_df = pd.DataFrame(
            {"월": ["1월", "2월", "3월", "4월", "5월", "6월"], "평점": place["trend"]}
        )
        trend_chart = px.line(
            trend_df,
            x="월",
            y="평점",
            markers=True,
            range_y=[3.8, 5.0],
            title="최근 평점 추이",
        )
        trend_chart.update_layout(
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.04)",
            font_color="white",
        )
        st.plotly_chart(trend_chart, use_container_width=True)

with tab_review:
    review_df = pd.DataFrame(
        [
            ["방문 인증", "야경이 좋고 직원 응대가 빨라서 데이트 코스로 추천합니다.", 4.8, 42, "문라이트 루프탑"],
            ["방문 인증", "게임 종류가 많아서 단체 모임에 좋았습니다. 주말은 예약을 추천합니다.", 4.5, 31, "온앤온 보드게임 카페"],
            ["일반", "조용하고 콘센트가 많아 심야 작업하기 좋습니다.", 4.6, 22, "심야 스터디 라운지"],
            ["방문 인증", "비 오는 날 실내에서 머물기 좋고 VR 장비 상태가 괜찮았습니다.", 4.2, 17, "VR 아케이드 배틀존"],
        ],
        columns=["인증", "리뷰", "평점", "공감", "장소"],
    )
    only_verified = st.checkbox("방문 인증 리뷰만 보기", value=True)
    sort_key = st.selectbox("정렬", ["공감", "평점"])
    review_view = (
        review_df[review_df["인증"].eq("방문 인증")] if only_verified else review_df
    )
    review_view = review_view.sort_values(sort_key, ascending=False)

    for _, review in review_view.iterrows():
        st.markdown(
            f"""
            <div class="place-card">
              {badge(review['인증'])}
              {badge(review['장소'])}
              <div class="place-title">평점 {review['평점']} <span class="small-muted">공감 {review['공감']}개</span></div>
              <p>{review['리뷰']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    keyword_df = pd.DataFrame(
        {
            "키워드": ["야경", "조용한", "가성비", "단체", "청결", "혼잡"],
            "빈도": [36, 28, 24, 21, 18, 14],
        }
    )
    keyword_chart = px.bar(keyword_df, x="키워드", y="빈도", title="자주 언급되는 키워드")
    keyword_chart.update_layout(
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.04)",
        font_color="white",
    )
    st.plotly_chart(keyword_chart, use_container_width=True)

st.caption("Demo MVP · Streamlit 배포용 샘플 데이터 기반 PGIS 대시보드")
