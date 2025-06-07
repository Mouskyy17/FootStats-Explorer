import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="FootStats Explorer - Saison 24/25",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #1e3c72;
    }
    
    .filter-section {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stSelectbox > div > div {
        background-color: #ffffff;
    }
    
    .subtitle {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e3c72;
        margin: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Chargement des données avec mise en cache"""
    try:
        df = pd.read_csv("df_Big2025.csv")
        return df
    except FileNotFoundError:
        st.error("Fichier 'df_Big2025.csv' non trouvé. Veuillez vérifier le chemin du fichier.")
        return None

# Charger les données
df = load_data()

if df is not None:
    # Titre principal avec style
    st.markdown('<h1 class="main-header">⚽ FootStats Explorer - Saison 24/25</h1>', unsafe_allow_html=True)
    
    # Métriques générales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Joueurs", len(df))
    with col2:
        st.metric("Ligues", df["Ligue"].nunique())
    with col3:
        st.metric("Équipes", df["Equipe"].nunique() if "Equipe" in df.columns else "N/A")
    with col4:
        st.metric("Positions", df["Position"].nunique())

    # Sidebar améliorée
    with st.sidebar:
        st.markdown("## 🎛️ Paramètres de Visualisation")
        
        # Section statistiques
        st.markdown("### 📊 Statistiques à comparer")
        excluded_columns = ["Position", "Ligue", "Equipe", "Joueur"]
        stats = [col for col in df.columns[4:] if col not in excluded_columns]
        
        col1_sb, col2_sb = st.columns(2)
        with col1_sb:
            stat_x = st.selectbox("Axe X", stats, 
                                index=list(stats).index("Buts") if "Buts" in stats else 0,
                                help="Choisissez la statistique pour l'axe horizontal")
        with col2_sb:
            stat_y = st.selectbox("Axe Y", stats, 
                                index=list(stats).index("Passes decisives") if "Passes decisives" in stats else 1,
                                help="Choisissez la statistique pour l'axe vertical")
        
        st.markdown("---")
        
        # Section filtres
        st.markdown("### 🔍 Filtres")
        
        # Nettoyage des données pour les filtres
        df_clean = df.dropna(subset=[stat_x, stat_y, "Minutes jouees", "Ligue", "Joueur", "Position"])
        
        min_minutes = st.slider("Minutes minimum", 
                               min_value=0, 
                               max_value=int(df_clean["Minutes jouees"].max()), 
                               value=500,
                               help="Filtrer les joueurs par temps de jeu minimum")
        
        leagues = st.multiselect("Ligues", 
                               df_clean["Ligue"].unique(), 
                               default=df_clean["Ligue"].unique()[:3],  # Limite par défaut
                               help="Sélectionnez les ligues à afficher")
        
        positions = st.multiselect("Positions", 
                                 df_clean["Position"].unique(), 
                                 default=df_clean["Position"].unique(),
                                 help="Filtrez par position de jeu")
        
        st.markdown("---")
        
        # Section affichage
        st.markdown("### 🎨 Options d'affichage")
        
        num_players = st.slider("Nombre de joueurs", 
                              min_value=10, 
                              max_value=min(200, len(df_clean)), 
                              value=50,
                              help="Nombre maximum de joueurs à afficher")
        
        num_labels = st.slider("Étiquettes joueurs", 
                             min_value=0, 
                             max_value=20, 
                             value=10,
                             help="Nombre de noms de joueurs à afficher sur le graphique")
        
        show_trendline = st.checkbox("Ligne de tendance", value=False, help="Afficher la corrélation")

    # Filtrage des données
    if leagues and positions:
        df_filtered = df_clean[
            (df_clean["Minutes jouees"] >= min_minutes) & 
            (df_clean["Ligue"].isin(leagues)) & 
            (df_clean["Position"].isin(positions))
        ]
        
        if len(df_filtered) > 0:
            # Sélection des meilleurs joueurs basée sur une combinaison des deux stats
            df_filtered['score_combined'] = (
                df_filtered[stat_x] / df_filtered[stat_x].max() + 
                df_filtered[stat_y] / df_filtered[stat_y].max()
            )
            df_filtered = df_filtered.nlargest(num_players, 'score_combined')
            
            # Graphique principal amélioré
            st.markdown(f'<div class="subtitle">🎯 Analyse: {stat_y} vs {stat_x}</div>', unsafe_allow_html=True)
            
            # Création du scatter plot amélioré
            fig = px.scatter(
                df_filtered, 
                x=stat_x, 
                y=stat_y, 
                color="Ligue",
                size="Minutes jouees",
                hover_data={
                    "Joueur": True,
                    "Equipe": True if "Equipe" in df_filtered.columns else False,
                    "Position": True,
                    "Minutes jouees": True,
                    stat_x: ":.1f",
                    stat_y: ":.1f"
                },
                title=f"Corrélation entre {stat_x} et {stat_y}",
                color_discrete_sequence=px.colors.qualitative.Set3,
                size_max=15
            )
            
            # Amélioration du style du graphique
            fig.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='white')))
            
            # Ajout de la ligne de tendance si demandée
            if show_trendline and len(df_filtered) > 1:
                z = np.polyfit(df_filtered[stat_x], df_filtered[stat_y], 1)
                p = np.poly1d(z)
                fig.add_traces(go.Scatter(
                    x=df_filtered[stat_x].sort_values(),
                    y=p(df_filtered[stat_x].sort_values()),
                    mode='lines',
                    name='Tendance',
                    line=dict(dash='dash', color='red', width=2)
                ))
            
            # Ajout des étiquettes avec positionnement intelligent
            if num_labels > 0:
                top_labels = df_filtered.nlargest(num_labels, 'score_combined')
                
                for i, row in top_labels.iterrows():
                    # Positionnement intelligent des étiquettes
                    y_offset = max(df_filtered[stat_y]) * 0.03 * (i % 3 + 1)
                    x_offset = max(df_filtered[stat_x]) * 0.01 * (i % 2)
                    
                    fig.add_annotation(
                        x=row[stat_x] + x_offset,
                        y=row[stat_y] + y_offset,
                        text=f"<b>{row['Joueur']}</b>",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=1,
                        arrowcolor="rgba(0,0,0,0.5)",
                        font=dict(size=10, color="black"),
                        bgcolor="rgba(255, 255, 255, 0.8)",
                        bordercolor="rgba(0,0,0,0.3)",
                        borderwidth=1
                    )
            
            # Mise à jour du layout
            fig.update_layout(
                height=600,
                font=dict(size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    gridcolor='rgba(128,128,128,0.2)',
                    title_font=dict(size=14, color='#1e3c72')
                ),
                yaxis=dict(
                    gridcolor='rgba(128,128,128,0.2)',
                    title_font=dict(size=14, color='#1e3c72')
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calcul et affichage de la corrélation
            correlation = df_filtered[stat_x].corr(df_filtered[stat_y])
            st.info(f"📈 Coefficient de corrélation: {correlation:.3f}")
            
            # Layout en colonnes pour les histogrammes
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f'<div class="subtitle">📊 Distribution - {stat_x}</div>', unsafe_allow_html=True)
                fig_x = px.histogram(
                    df_filtered, 
                    x=stat_x, 
                    nbins=20,
                    color="Ligue",
                    title=f"Répartition des valeurs - {stat_x}",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_x.update_layout(
                    height=400,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_x, use_container_width=True)
            
            with col2:
                st.markdown(f'<div class="subtitle">📊 Distribution - {stat_y}</div>', unsafe_allow_html=True)
                fig_y = px.histogram(
                    df_filtered, 
                    x=stat_y, 
                    nbins=20,
                    color="Ligue",
                    title=f"Répartition des valeurs - {stat_y}",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_y.update_layout(
                    height=400,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_y, use_container_width=True)
            
            # Tableaux des tops avec styling amélioré
            st.markdown('<div class="subtitle">🏆 Classements</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🥇 Top 5 - {stat_x}**")
                top_x = df_filtered.nlargest(5, stat_x)[["Joueur", "Equipe", "Ligue", stat_x]]
                st.dataframe(
                    top_x,
                    use_container_width=True,
                    hide_index=True
                )
            
            with col2:
                st.markdown(f"**🥇 Top 5 - {stat_y}**")
                top_y = df_filtered.nlargest(5, stat_y)[["Joueur", "Equipe", "Ligue", stat_y]]
                st.dataframe(
                    top_y,
                    use_container_width=True,
                    hide_index=True
                )
            
            # Statistiques résumées
            with st.expander("📈 Statistiques descriptives"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{stat_x}**")
                    st.write(f"• Moyenne: {df_filtered[stat_x].mean():.2f}")
                    st.write(f"• Médiane: {df_filtered[stat_x].median():.2f}")
                    st.write(f"• Écart-type: {df_filtered[stat_x].std():.2f}")
                    st.write(f"• Maximum: {df_filtered[stat_x].max():.2f}")
                
                with col2:
                    st.markdown(f"**{stat_y}**")
                    st.write(f"• Moyenne: {df_filtered[stat_y].mean():.2f}")
                    st.write(f"• Médiane: {df_filtered[stat_y].median():.2f}")
                    st.write(f"• Écart-type: {df_filtered[stat_y].std():.2f}")
                    st.write(f"• Maximum: {df_filtered[stat_y].max():.2f}")
        
        else:
            st.warning("🚫 Aucun joueur ne correspond aux critères sélectionnés. Veuillez ajuster vos filtres.")
    
    else:
        st.warning("⚠️ Veuillez sélectionner au moins une ligue et une position.")

else:
    st.error("❌ Impossible de charger les données. Vérifiez que le fichier CSV est présent.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
    "FootStats Explorer 2025 - Analyse des performances footballistiques"
    "</div>", 
    unsafe_allow_html=True
)