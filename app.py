import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IT & DS Jobs Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("vacancies.csv")
    return df

df = load_data()

st.title("Dashboard: 5000 вакансий в IT и Data Science")
st.markdown("Данные собраны с помощью API jsearch")

st.sidebar.header("Фильтры")
selected_roles = st.sidebar.multiselect(
    "Выберите должность:", 
    options=df["name"].unique(),
    default=df["name"].value_counts().head(5).index.tolist()
)

filtered_df = df[df["name"].isin(selected_roles)]

col1, col2, col3 = st.columns(3)
col1.metric("Всего вакансий (после фильтра)", len(filtered_df))
col2.metric("Уникальных компаний", filtered_df["employer"].nunique())
col3.metric("Вакансий с указанной ЗП", filtered_df["salary_from"].notna().sum())

st.markdown("---")

st.subheader("Топ-20 компаний по количеству вакансий")
top_employers = filtered_df["employer"].value_counts().head(20).reset_index()
top_employers.columns = ["Компания", "Количество"]
fig1 = px.bar(top_employers, x="Количество", y="Компания", orientation="h", color="Количество")
st.plotly_chart(fig1, use_container_width=True)

col4, col5 = st.columns(2)

with col4:
    st.subheader("Топ-10 локаций")
    top_areas = filtered_df["area"].value_counts().head(10).reset_index()
    top_areas.columns = ["Город", "Количество"]
    fig2 = px.pie(top_areas, values="Количество", names="Город", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

with col5:
    st.subheader("Распределение зарплат")
    salary_df = filtered_df.dropna(subset=["salary_from"])
    salary_df = salary_df[(salary_df["salary_from"] > 0) & (salary_df["salary_from"] < 500000)] 
    
    if not salary_df.empty:
        fig3 = px.histogram(salary_df, x="salary_from", nbins=30, color_discrete_sequence=["#00b4d8"])
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("В собранных данных не оказалось указанных зарплат для построения графика.")

st.subheader("Последние добавленные вакансии")
st.dataframe(filtered_df[["name", "employer", "area", "salary_from", "published_at"]].sort_values(by="published_at", ascending=False).head(50), use_container_width=True)