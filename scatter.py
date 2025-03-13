import streamlit as st
import pandas as pd

# Charger les données
df = pd.read_csv("df_Big2025.csv")

# Titre de l'application
st.title("Analyse des performances des joueurs - Saison 24/25")

# Sidebar pour les options
st.sidebar.header("Options de personnalisation")

# Sélection des statistiques
stats = df.columns[4:]
stat_x = st.sidebar.selectbox("Choisissez la statistique pour l'axe X", stats, index=list(stats).index("Buts"))
stat_y = st.sidebar.selectbox("Choisissez la statistique pour l'axe Y", stats, index=list(stats).index("Passes decisives"))

# Filtres
df = df.dropna(subset=[stat_x, stat_y, "Minutes jouees", "Ligue", "Joueur"])
min_minutes = st.sidebar.slider("Nombre minimum de minutes jouées", min_value=0, max_value=int(df["Minutes jouees"].max()), value=500)
leagues = st.sidebar.multiselect("Sélectionnez les ligues", df["Ligue"].unique(), default=df["Ligue"].unique())
num_labels = st.sidebar.slider("Nombre de joueurs à afficher avec des étiquettes", min_value=0, max_value=20, value=5)
label_size = st.sidebar.slider("Taille du texte des étiquettes", min_value=6, max_value=20, value=10)

# Filtrer les données
df_filtered = df[(df["Minutes jouees"] >= min_minutes) & (df["Ligue"].isin(leagues))]

# Création du scatter plot
st.subheader(f"{stat_y} vs {stat_x}")
st.scatter_chart(df_filtered, x=stat_x, y=stat_y, size="Minutes jouees", color="Ligue")

# Histogrammes
st.subheader(f"Distribution de {stat_x}")
st.hist_chart(df_filtered[stat_x])
st.subheader(f"Distribution de {stat_y}")
st.hist_chart(df_filtered[stat_y])

# Top 5 joueurs pour chaque statistique
st.subheader(f"Top 5 joueurs pour {stat_x}")
st.write(df_filtered.nlargest(5, stat_x)[["Joueur", "Equipe", "Ligue", stat_x]])

st.subheader(f"Top 5 joueurs pour {stat_y}")
st.write(df_filtered.nlargest(5, stat_y)[["Joueur", "Equipe", "Ligue", stat_y]])
