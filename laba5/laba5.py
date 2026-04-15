import os
import glob
import urllib.request
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


NOAA_TO_NAME = {
    1: "Черкаська", 2: "Чернігівська", 3: "Чернівецька",
    4: "Крим", 5: "Дніпропетровська", 6: "Донецька",
    7: "Івано-Франківська", 8: "Харківська", 9: "Херсонська",
    10: "Хмельницька", 11: "Київська", 12: "м. Київ",
    13: "Кіровоградська", 14: "Луганська", 15: "Львівська",
    16: "Миколаївська", 17: "Одеська", 18: "Полтавська",
    19: "Рівненська", 20: "Сумська", 21: "Тернопільська",
    22: "Вінницька", 23: "Волинська", 24: "Закарпатська",
    25: "Запорізька", 26: "Житомирська", 27: "м. Севастополь",
}

NAME_TO_ID = {v: k for k, v in NOAA_TO_NAME.items()}
ALL_REGIONS = sorted(NOAA_TO_NAME.values())

DATA_DIR = "vhi_data"

def download_vhi_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    progress = st.progress(0, text="Завантаження даних VHI…")
    for i in range(1, 28):
        existing = glob.glob(os.path.join(DATA_DIR, f"vhi_id_{i}_*.csv"))
        if existing:
            progress.progress(i / 27, text=f"Область {i}/27 — вже є")
            continue
        url = (
            f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/"
            f"get_TS_admin.php?country=UKR&provinceID={i}"
            f"&year1=1981&year2=2024&type=Mean"
        )
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                content = resp.read().decode("utf-8")
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = os.path.join(DATA_DIR, f"vhi_id_{i}_{ts}.csv")
            with open(fname, "w") as f:
                f.write(content)
            progress.progress(i / 27, text=f"Область {i}/27 — завантажено ✓")
        except Exception as e:
            progress.progress(i / 27, text=f"Область {i}/27 — помилка: {e}")
    progress.empty()


@st.cache_data(show_spinner="Зчитування даних…")
def load_vhi_data():
    frames = []
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".csv"):
            continue
        parts = filename.replace(".csv", "").split("_")
        province_id = next(
            (int(p) for p in parts if p.isdigit() and 1 <= int(p) <= 27), None
        )
        if province_id is None:
            continue
        rows = []
        with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.replace("<br>", "").replace("<tt><pre>", "").replace("</tt></pre>", "").strip()
                if not line or line.startswith(("Mean", "year", "<")):
                    continue
                row_parts = [x.strip() for x in line.rstrip(",").split(",")]
                if len(row_parts) == 7:
                    rows.append(row_parts)
        if not rows:
            continue
        tmp = pd.DataFrame(rows, columns=["year", "week", "SMN", "SMT", "VCI", "TCI", "VHI"])
        for col in tmp.columns:
            tmp[col] = pd.to_numeric(tmp[col], errors="coerce")
        tmp = tmp.dropna(subset=["year", "week", "VHI"])
        tmp = tmp[tmp["VHI"] != -1]
        if tmp.empty:
            continue
        tmp["year"] = tmp["year"].astype(int)
        tmp["week"] = tmp["week"].astype(int)
        tmp["province_id"] = province_id
        tmp["region"] = NOAA_TO_NAME.get(province_id, f"ID {province_id}")
        frames.append(tmp)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(subset=["province_id", "year", "week"])
    return df


st.set_page_config(
    page_title="VHI Аналіз України",
    page_icon=" ",
    layout="wide",
)

st.title("Аналіз індексів VHI / TCI / VCI по областях України")

if not os.path.exists(DATA_DIR) or len(glob.glob(os.path.join(DATA_DIR, "*.csv"))) < 27:
    st.info("Дані відсутні. Починаємо завантаження з NOAA (може зайняти ~1-2 хвилини)…")
    download_vhi_data()
    st.cache_data.clear()

df_all = load_vhi_data()

if df_all.empty:
    st.error("Не вдалося завантажити дані. Перевірте підключення до інтернету.")
    st.stop()

MIN_YEAR = int(df_all["year"].min())
MAX_YEAR = int(df_all["year"].max())
MIN_WEEK = int(df_all["week"].min())
MAX_WEEK = int(df_all["week"].max())


DEFAULTS = dict(
    index_type="VHI",
    region=ALL_REGIONS[0],
    week_range=(MIN_WEEK, MAX_WEEK),
    year_range=(MIN_YEAR, MAX_YEAR),
    sort_asc=False,
    sort_desc=False,
)

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_filters():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


col_filters, col_content = st.columns([1, 3], gap="large")

with col_filters:
    st.subheader(" Фільтри")

    index_type = st.selectbox(
        "Часовий ряд",
        ["VCI", "TCI", "VHI"],
        index=["VCI", "TCI", "VHI"].index(st.session_state.index_type),
        key="index_type",
    )

    region = st.selectbox(
        "Область",
        ALL_REGIONS,
        index=ALL_REGIONS.index(st.session_state.region),
        key="region",
    )

    week_range = st.slider(
        "Тижні",
        MIN_WEEK, MAX_WEEK,
        value=st.session_state.week_range,
        key="week_range",
    )

    year_range = st.slider(
        "Роки",
        MIN_YEAR, MAX_YEAR,
        value=st.session_state.year_range,
        key="year_range",
    )

    st.markdown("**Сортування**")
    sort_asc = st.checkbox("За зростанням", key="sort_asc")
    sort_desc = st.checkbox("За спаданням", key="sort_desc")

    if sort_asc and sort_desc:
        st.warning("Увімкнено обидва сортування — застосовується зростання.")

    st.button("Скинути фільтри", on_click=reset_filters, use_container_width=True)


mask = (
    (df_all["region"] == region)
    & (df_all["week"] >= week_range[0])
    & (df_all["week"] <= week_range[1])
    & (df_all["year"] >= year_range[0])
    & (df_all["year"] <= year_range[1])
)
df_filtered = df_all[mask].copy()

if sort_asc and not sort_desc:
    df_filtered = df_filtered.sort_values(index_type, ascending=True)
elif sort_desc:
    df_filtered = df_filtered.sort_values(index_type, ascending=False)
else:
    df_filtered = df_filtered.sort_values(["year", "week"])

display_cols = ["year", "week", "VCI", "TCI", "VHI", "region"]
df_display = df_filtered[display_cols].rename(columns={
    "year": "Рік", "week": "Тиждень", "region": "Область"
})


with col_content:
    tab_table, tab_chart, tab_compare = st.tabs([" Таблиця", " Графік", "Порівняння областей"])

  
    with tab_table:
        st.caption(f"Знайдено записів: **{len(df_display)}**")
        st.dataframe(df_display, use_container_width=True, height=500)

  
    with tab_chart:
        if df_filtered.empty:
            st.info("Немає даних для вибраних фільтрів.")
        else:
            df_plot = df_filtered.copy()
            
            df_plot["period"] = df_plot["year"].astype(str) + "-W" + df_plot["week"].astype(str).str.zfill(2)
            df_plot = df_plot.sort_values(["year", "week"])

            fig1 = px.line(
                df_plot,
                x="period",
                y=index_type,
                title=f"{index_type} — {region} ({year_range[0]}–{year_range[1]}, тижні {week_range[0]}–{week_range[1]})",
                labels={"period": "Рік-Тиждень", index_type: index_type},
                color_discrete_sequence=["#cc2e2e"],
            )
            fig1.update_layout(
                xaxis=dict(tickangle=-45, nticks=20),
                hovermode="x unified",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            fig1.add_hrect(y0=0, y1=10, fillcolor="red", opacity=0.08, line_width=0, annotation_text="Надзвичайна посуха")
            fig1.add_hrect(y0=10, y1=20, fillcolor="orange", opacity=0.08, line_width=0, annotation_text="Помірна посуха")
            fig1.add_hrect(y0=40, y1=100, fillcolor="green", opacity=0.05, line_width=0, annotation_text="Норма")
            st.plotly_chart(fig1, use_container_width=True)


    with tab_compare:
     
        mask_all = (
            (df_all["week"] >= week_range[0])
            & (df_all["week"] <= week_range[1])
            & (df_all["year"] >= year_range[0])
            & (df_all["year"] <= year_range[1])
        )
        df_compare_all = df_all[mask_all].copy()

        if df_compare_all.empty:
            st.info("Немає даних для вибраних фільтрів.")
        else:
       
            df_med = (
                df_compare_all.groupby("region")[index_type]
                .median()
                .reset_index()
                .rename(columns={index_type: f"Медіана {index_type}"})
                .sort_values(f"Медіана {index_type}", ascending=False)
            )

            colors = ["#3cd3e7" if r == region else "#db34c5" for r in df_med["region"]]

            fig2 = go.Figure(go.Bar(
                x=df_med["region"],
                y=df_med[f"Медіана {index_type}"],
                marker_color=colors,
                hovertemplate="%{x}: %{y:.1f}<extra></extra>",
            ))
            fig2.update_layout(
                title=f"Медіана {index_type} по всіх областях (виділено: {region})",
                xaxis=dict(tickangle=-45),
                yaxis_title=f"Медіана {index_type}",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("#### Розподіл значень по областях (box plot)")
            fig3 = px.box(
                df_compare_all,
                x="region",
                y=index_type,
                color="region",
                title=f"Розподіл {index_type} по областях",
                labels={"region": "Область"},
            )
            fig3.update_layout(
                xaxis=dict(tickangle=-45),
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                height=500,
            )
            st.plotly_chart(fig3, use_container_width=True)