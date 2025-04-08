import streamlit as st
import pandas as pd
import altair as alt
import json

st.set_page_config(
    page_title="Distalyzer",
    page_icon="📊",
    layout="centered"
)

st.title("Distalyzer - Aplikasi Analisis Distribusi Data")

st.markdown("""
Aplikasi ini membantu kamu menganalisis distribusi data frekuensi, PDF, CDF, dan persentase dari file **CSV** atau **JSON**.

**Syarat format data:**
- Terdiri dari **2 kolom**: kolom pertama bertipe **string**, kolom kedua bertipe **numerik**.
- **Baris pertama** digunakan untuk nama kolom.

Berikut contoh data untuk jumlah servant pada setiap kelas di Fate Series.


**Contoh format CSV yang benar:**
| Kelas | Jumlah Servant Terkait |
|-------|-------------------------|
| Saber | 45                      |
| Archer| 39                      |
| Lancer| 34                      |

**Contoh format JSON yang benar:**
```
[
  {"Kelas": "Saber", "Jumlah Servant Terkait": 45},
  {"Kelas": "Archer", "Jumlah Servant Terkait": 39},
  {"Kelas": "Lancer", "Jumlah Servant Terkait": 34}
]
```
""")

uploaded_file = st.file_uploader("Unggah file CSV atau JSON", type=["csv", "json"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_json(uploaded_file)

        if df.shape[1] != 2:
            st.error("File harus memiliki tepat 2 kolom.")
        else:
            col1, col2 = df.columns

            if not pd.api.types.is_numeric_dtype(df[col2]):
                st.error("Kolom kedua harus bertipe numerik.")
            else:
                total = df[col2].sum()

                df["PDF_numeric"] = df[col2] / total
                df["PDF"] = df.apply(lambda r: f"{r[col2]}/{total} = {r['PDF_numeric']:.4f}", axis=1)

                df["CDF_numeric"] = df["PDF_numeric"].cumsum()

                cdf_strings = []
                running = 0
                for p in df["PDF_numeric"]:
                    prev = running
                    running += p
                    if prev == 0:
                        cdf_strings.append(f"{p:.4f} = {running:.4f}")
                    else:
                        cdf_strings.append(f"{prev:.4f} + {p:.4f} = {running:.4f}")
                df["CDF"] = cdf_strings

                df["Persentase"] = df["PDF_numeric"] * 100

                st.subheader("Tabel Data")
                st.dataframe(df.rename(columns={col1: col1, col2: "Frekuensi"}).set_index(col1)[["Frekuensi", "PDF", "CDF", "Persentase"]])

                st.subheader("Grafik Frekuensi")
                bar_chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X(f"{col1}:N", title=col1, sort=None),
                    y=alt.Y(f"{col2}:Q", title="Frekuensi"),
                    tooltip=[col1, col2]
                ).properties(height=400)
                st.altair_chart(bar_chart, use_container_width=True)

                st.subheader("Grafik PDF")
                pdf_chart = alt.Chart(df).mark_line(point=True, color="orange").encode(
                    x=alt.X(f"{col1}:N", title=col1, sort=None),
                    y=alt.Y("PDF_numeric:Q", title="PDF"),
                    tooltip=[col1, "PDF"]
                ).properties(height=300)
                st.altair_chart(pdf_chart, use_container_width=True)

                st.subheader("Grafik CDF")
                cdf_chart = alt.Chart(df).mark_line(point=True, color="blue").encode(
                    x=alt.X(f"{col1}:N", title=col1, sort=None),
                    y=alt.Y("CDF_numeric:Q", title="CDF"),
                    tooltip=[col1, "CDF"]
                ).properties(height=300)
                st.altair_chart(cdf_chart, use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")

st.markdown("""---""")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with 愛 in Streamlit"
    "</div>",
    unsafe_allow_html=True
)