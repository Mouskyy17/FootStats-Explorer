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
excluded_columns = ["Position", "Ligue"]
stats = [col for col in df.columns[4:] if col not in excluded_columns]
stat_x = st.sidebar.selectbox("Choisissez la statistique pour l'axe X", stats, index=list(stats).index("Buts"))
stat_y = st.sidebar.selectbox("Choisissez la statistique pour l'axe Y", stats, index=list(stats).index("Passes decisives"))

# Filtres
df = df.dropna(subset=[stat_x, stat_y, "Minutes jouees", "Ligue", "Joueur", "Position"])
min_minutes = st.sidebar.slider("Nombre minimum de minutes jouées", min_value=0, max_value=int(df["Minutes jouees"].max()), value=500)
leagues = st.sidebar.multiselect("Sélectionnez les ligues", df["Ligue"].unique(), default=df["Ligue"].unique())
positions = st.sidebar.multiselect("Sélectionnez les positions", df["Position"].unique(), default=df["Position"].unique())
num_players = st.sidebar.slider("Nombre de joueurs à considérer sur le graphique", min_value=10, max_value=len(df), value=50)
num_labels = st.sidebar.slider("Nombre de joueurs à afficher avec des étiquettes", min_value=0, max_value=20, value=10)
label_size = st.sidebar.slider("Taille du texte des étiquettes", min_value=6, max_value=20, value=10)

# Filtrer les données
df_filtered = df[(df["Minutes jouees"] >= min_minutes) & (df["Ligue"].isin(leagues)) & (df["Position"].isin(positions))]
df_filtered = df_filtered.nlargest(num_players, stat_x)

# Création du scatter plot avec couleurs foncées et points plus petits
st.subheader(f"{stat_y} vs {stat_x}")
fig = px.scatter(df_filtered, x=stat_x, y=stat_y, color="Ligue", hover_data=["Joueur", "Equipe"],
                 size_max=10, opacity=0.8, color_discrete_sequence=px.colors.qualitative.Dark24)

# Ajouter des étiquettes aux 10-12 meilleurs points avec espacement
top_labels = df_filtered.nlargest(num_labels, [stat_x, stat_y])
for i, row in top_labels.iterrows():
    fig.add_annotation(
        x=row[stat_x], 
        y=row[stat_y] + (row[stat_y] * 0.8),  # Décalage augmenté pour éviter confusion
        text=row["Joueur"],
        showarrow=False,
        font=dict(size=label_size),
        bgcolor="rgba(255, 255, 255, 0.7)",  # Fond semi-transparent pour lisibilité
       # bordercolor="black",  # Bordure pour améliorer la visibilité
    )

st.plotly_chart(fig)

# Histogrammes avec barres plus fines
st.subheader(f"Distribution de {stat_x}")
fig_x = px.histogram(df_filtered, x=stat_x, nbins=30, text_auto=True, hover_data=["Joueur"], opacity=0.8)
st.plotly_chart(fig_x)

st.subheader(f"Distribution de {stat_y}")
fig_y = px.histogram(df_filtered, x=stat_y, nbins=30, text_auto=True, hover_data=["Joueur"], opacity=0.8)
st.plotly_chart(fig_y)

# Top 5 joueurs pour chaque statistique
st.subheader(f"Top 5 joueurs pour {stat_x}")
st.write(df_filtered.nlargest(5, stat_x)[["Joueur", "Equipe", "Ligue", stat_x]])

st.subheader(f"Top 5 joueurs pour {stat_y}")
st.write(df_filtered.nlargest(5, stat_y)[["Joueur", "Equipe", "Ligue", stat_y]])
