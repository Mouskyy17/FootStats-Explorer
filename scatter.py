import streamlit as st
import pandas as pd
import plotly.express as px

# Charger les données
df = pd.read_csv("df_Big2025.csv")

# Titre de l'application
st.title("FootStats Explorer - Saison 24/25")

# Sidebar pour les options
st.sidebar.header("Options de personnalisation")

# Sélection des statistiques
stats = df.columns[4:]
stat_x = st.sidebar.selectbox("Choisissez la statistique pour l'axe X", stats, index=list(stats).index("Buts"))
stat_y = st.sidebar.selectbox("Choisissez la statistique pour l'axe Y", stats, index=list(stats).index("Passes decisives"))

# Filtres
df = df.dropna(subset=[stat_x, stat_y, "Minutes jouees", "Ligue", "Joueur", "Position"])
min_minutes = st.sidebar.slider("Nombre minimum de minutes jouées", 0, int(df["Minutes jouees"].max()), 500)
leagues = st.sidebar.multiselect("Sélectionnez les ligues", df["Ligue"].unique(), default=df["Ligue"].unique())
positions = st.sidebar.multiselect("Sélectionnez les positions", df["Position"].unique(), default=df["Position"].unique())
num_players = st.sidebar.slider("Nombre de joueurs à considérer sur le graphique", 10, len(df), 50)
num_labels = st.sidebar.slider("Nombre de joueurs à afficher avec des étiquettes", 0, 20, 5)
label_size = st.sidebar.slider("Taille du texte des étiquettes", 6, 20, 10)

# Filtrer les données
df_filtered = df[(df["Minutes jouees"] >= min_minutes) & (df["Ligue"].isin(leagues)) & (df["Position"].isin(positions))]
df_filtered = df_filtered.nlargest(num_players, stat_x)

# Création du scatter plot amélioré
st.subheader(f"{stat_y} vs {stat_x}")
fig = px.scatter(
    df_filtered, x=stat_x, y=stat_y, size="Minutes jouees", color="Ligue",
    hover_data=["Joueur", "Equipe"], opacity=0.7,
    color_discrete_sequence=px.colors.qualitative.Set1
)

# Ajout d'annotations pour les meilleurs joueurs
for i, row in df_filtered.nlargest(num_labels, stat_x).iterrows():
    fig.add_annotation(
        x=row[stat_x], y=row[stat_y], text=row["Joueur"],
        showarrow=True, arrowhead=2, font=dict(size=label_size)
    )

st.plotly_chart(fig)

# Histogrammes améliorés
st.subheader(f"Distribution de {stat_x}")
fig_x = px.histogram(df_filtered, x=stat_x, nbins=20, text_auto=True, hover_data=["Joueur"], orientation='h')
fig_x.add_vline(x=df_filtered[stat_x].median(), line_dash="dash", line_color="red", annotation_text="Médiane")
st.plotly_chart(fig_x)

st.subheader(f"Distribution de {stat_y}")
fig_y = px.histogram(df_filtered, x=stat_y, nbins=20, text_auto=True, hover_data=["Joueur"], orientation='h')
fig_y.add_vline(x=df_filtered[stat_y].median(), line_dash="dash", line_color="red", annotation_text="Médiane")
st.plotly_chart(fig_y)

# Top 5 joueurs
st.subheader(f"Top 5 joueurs pour {stat_x}")
st.write(df_filtered.nlargest(5, stat_x)[["Joueur", "Equipe", "Ligue", stat_x]])

st.subheader(f"Top 5 joueurs pour {stat_y}")
st.write(df_filtered.nlargest(5, stat_y)[["Joueur", "Equipe", "Ligue", stat_y]])