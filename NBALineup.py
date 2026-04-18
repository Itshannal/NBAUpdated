import pandas as pd
import streamlit as st
import plotly.express as px

#1 Page Setup
st.set_page_config(page_title="NBA Lineup 2026", layout="wide")

st.markdown("""
    <style>
    .metric-container { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    .stMetric { background-color: #838B8B; padding: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)


#2 Loading Data
@st.cache_data
def load_and_process_data():
    df = pd.read_csv('nba2026.csv')

    df['player_list'] = df['GROUP_NAME'].str.split(' - ')

    df_players = df.explode('player_list')


    player_profiles = df_players.groupby('player_list').agg({
        'PTS': 'mean',
        'PLUS_MINUS': 'mean',
        'FG_PCT': 'mean',
        'FG3_PCT': 'mean',
        'AST': 'mean',
        'REB': 'mean',
        'MIN': 'sum'
    }).reset_index().rename(columns={'player_list': 'PLAYER_NAME'})

    return df, player_profiles

try:
    df_lineups, df_ind = load_and_process_data()
except Exception as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()

#3 Filter Control
st.sidebar.title("Lineup Selection")
st.sidebar.info("Select a team, then pick any 5 players to project their combined performance based on historical averages.")

teams = sorted(df_lineups['team'].unique())
selected_team = st.sidebar.selectbox("Select a team:", options=teams)

team_players = sorted(df_ind[df_ind['PLAYER_NAME'].isin(
    df_lineups[df_lineups['team'] == selected_team].explode('player_list')['player_list'].unique()
)]['PLAYER_NAME'])


selected_5 = st.sidebar.multiselect(
    "Construct your 5-man unit:",
    options=team_players,
    default=team_players[:5] if len(team_players) >= 5 else None
)

#4 Projection
if len(selected_5) == 5:

    selected_stats = df_ind[df_ind['PLAYER_NAME'].isin(selected_5)]

    #Theoretical Lineup
    proj_pts = selected_stats['PTS'].sum()
    proj_pm = selected_stats['PLUS_MINUS'].mean()
    proj_fg = selected_stats['FG_PCT'].mean()
    proj_3p = selected_stats['FG3_PCT'].mean()

    actual_match = df_lineups[df_lineups['player_list'].apply(lambda x: set(x) == set(selected_5))]

    #5 Main Page
    st.title("NBA Theoretical Lineup Projection")

    # Header Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Projected PPG", f"{proj_pts:.1f}")
    m2.metric("Projected Net +/-", f"{proj_pm:.2f}")
    m3.metric("Avg FG%", f"{proj_fg:.1%}")
    m4.metric("Avg 3P%", f"{proj_3p:.1%}")

    st.divider()

    #Charts
    st.subheader("Individual Contribution to +/-")
    fig_pm = px.bar(
        selected_stats,
        x='PLAYER_NAME',
        y='PLUS_MINUS',
        color='PLUS_MINUS',
        color_continuous_scale='RdYlGn',
        text_auto='.2f'
    )
    fig_pm.update_layout(showlegend=False)
    st.plotly_chart(fig_pm, use_container_width=True)

    st.subheader("Shot Efficiency Comparison")
    fig_ext = px.scatter(
        selected_stats,
        x='FG_PCT',
        y='FG3_PCT',
        size='PTS',
        text='PLAYER_NAME',
        labels={'FG_PCT': 'Field Goal %', 'FG3_PCT': '3-Point %'},
        color='PLAYER_NAME'
    )
    st.plotly_chart(fig_ext, use_container_width=True)

    #Historical Context
    st.subheader("Historical Context")
    if not actual_match.empty:
        st.success(f"This exact lineup has played {actual_match['MIN'].values[0]} minutes together.")
        st.dataframe(actual_match[['GROUP_NAME', 'MIN', 'W_PCT', 'PLUS_MINUS']])
    else:
        st.warning("No historical data found for this exact 5-man combination.")
        st.info(
            "The metrics above are **theoretical projections** based on individual player impact across all other lineups they've appeared in.")

else:
    st.title("NBA Lineup Lab")
    st.warning("Please select exactly 5 players from the sidebar to begin the analysis.")