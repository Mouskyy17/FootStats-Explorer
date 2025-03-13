import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Charger les données
df = pd.read_csv("df_Big2025.csv")

# Titre de l'application
st.title("Analyse des performances des joueurs - Saison 24/25")

# Sélection des statistiques
stats = df.columns[4:]
stat_x = st.selectbox("Choisissez la statistique pour l'axe X", stats, index=list(stats).index("Buts"))
stat_y = st.selectbox("Choisissez la statistique pour l'axe Y", stats, index=list(stats).index("Passes decisives"))

# Filtres
df = df.dropna(subset=[stat_x, stat_y, "Minutes jouees", "Ligue", "Joueur"])
min_minutes = st.slider("Nombre minimum de minutes jouées", min_value=0, max_value=int(df["Minutes jouees"].max()), value=500)
leagues = st.multiselect("Sélectionnez les ligues", df["Ligue"].unique(), default=df["Ligue"].unique())
num_labels = st.slider("Nombre de joueurs à afficher avec des étiquettes", min_value=0, max_value=20, value=5)
label_size = st.slider("Taille du texte des étiquettes", min_value=6, max_value=20, value=10)

# Filtrer les données
df_filtered = df[(df["Minutes jouees"] >= min_minutes) & (df["Ligue"].isin(leagues))]

# Création du scatter plot
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=df_filtered, x=stat_x, y=stat_y, hue="Ligue", alpha=0.7, palette="tab10", ax=ax)
ax.set_title(f"{stat_y} vs {stat_x}")
ax.set_xlabel(stat_x)
ax.set_ylabel(stat_y)

# Ajouter les étiquettes aux meilleurs joueurs
top_players = df_filtered.nlargest(num_labels, [stat_x, stat_y])
for _, row in top_players.iterrows():
    ax.text(row[stat_x], row[stat_y], row["Joueur"], fontsize=label_size)

st.pyplot(fig)

# Histogrammes
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
df_filtered[stat_x].hist(bins=20, ax=axes[0], color='b', alpha=0.6)
axes[0].set_title(f"Distribution de {stat_x}")
axes[0].set_xlabel(stat_x)
df_filtered[stat_y].hist(bins=20, ax=axes[1], color='r', alpha=0.6)
axes[1].set_title(f"Distribution de {stat_y}")
axes[1].set_xlabel(stat_y)
st.pyplot(fig)

# Top 5 joueurs pour chaque statistique
st.subheader(f"Top 5 joueurs pour {stat_x}")
st.write(df_filtered.nlargest(5, stat_x)[["Joueur", "Equipe", "Ligue", stat_x]])

st.subheader(f"Top 5 joueurs pour {stat_y}")
st.write(df_filtered.nlargest(5, stat_y)[["Joueur", "Equipe", "Ligue", stat_y]])
