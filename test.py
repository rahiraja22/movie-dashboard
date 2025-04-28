import streamlit as st

st.title('WEB SCARPING VISUALIZATION')


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load your dataset
@st.cache_data
def load_data():
    df = pd.read_csv("C:/Users/Office/Desktop/Home_files/imdb/clean_combined_output.csv")  # Change to your CSV filename
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df['duration'] = df['duration'].replace(0, pd.NA)  # Replace 0 with NaN
    return df



df = load_data()



st.title("🎬 Movie Data Visualizations")
st.markdown("Explore movie insights using **interactive Streamlit visualizations**")

# 1. Top 10 Movies by Rating & Voting
st.header("🏆 Top 10 Movies by Rating & Voting Count")
top_movies = df[df['voting_count'] > 1000].sort_values(by=['rating', 'voting_count'], ascending=False).head(10)
st.dataframe(top_movies[['movie_name', 'rating', 'voting_count']])

# 2. Genre Distribution
st.header("🎭 gentre Distribution")
genre_count = df['gentre'].value_counts()
fig1 = px.bar(x=genre_count.index, y=genre_count.values, labels={'x': 'Gentre', 'y': 'Number of Movies'})
st.plotly_chart(fig1)

# 3. Average Duration by Genre
st.header("⏳ Average Duration by gentre")
avg_duration = df.groupby('gentre')['duration'].mean().dropna().sort_values()
fig2 = px.bar(x=avg_duration.values, y=avg_duration.index, orientation='h',
              labels={'x': 'Avg Duration (mins)', 'y': 'gentre'})
st.plotly_chart(fig2)



# 4. Voting Trends by Genre
st.header("🗳️ Average Voting Count by gentre")
avg_votes = df.groupby('gentre')['voting_count'].mean().sort_values(ascending=False)
fig3 = px.bar(x=avg_votes.index, y=avg_votes.values, labels={'x': 'gentre', 'y': 'Average Votes'})
st.plotly_chart(fig3)

# 5. Rating Distribution
st.header("⭐ Rating Distribution")
fig4, ax = plt.subplots()
sns.histplot(df['rating'], bins=20, kde=True, ax=ax)
st.pyplot(fig4)



# 6. Genre-Based Rating Leaders
st.header("👑 Top-Rated Movie in Each Genre")
top_per_genre = df.loc[df.groupby('gentre')['rating'].idxmax()]
st.dataframe(top_per_genre[['gentre', 'movie_name', 'rating']])

# 7. Most Popular Genres by Total Voting (Pie)
st.header("🥧 Most Popular Genres by Total Voting Count")
genre_votes = df.groupby('gentre')['voting_count'].sum()
fig5 = px.pie(names=genre_votes.index, values=genre_votes.values)
st.plotly_chart(fig5)

# 8. Duration Extremes
st.header("📏 Shortest & Longest Movies")
shortest = df.loc[df['duration'].idxmin()]
longest = df.loc[df['duration'].idxmax()]
col1, col2 = st.columns(2)
with col1:
    st.metric("🎬 Shortest Movie", f"{shortest['movie_name']}", f"{shortest['duration']} mins")
with col2:
    st.metric("🎥 Longest Movie", f"{longest['movie_name']}", f"{longest['duration']} mins")

# 9. Ratings by Genre (Heatmap)
st.header("🔥 Average Ratings by Gentre")
heat_data = df.groupby('gentre')['rating'].mean().reset_index()
fig6, ax2 = plt.subplots(figsize=(10, 1.5))
sns.heatmap([heat_data['rating']], annot=True, fmt=".1f", cmap="coolwarm", xticklabels=heat_data['gentre'])
ax2.set_yticklabels(["rating"])
st.pyplot(fig6)

# 10. Correlation: Rating vs Voting Count
st.header("📊 Rating vs Voting Count Correlation")
fig7 = px.scatter(df, x='voting_count', y='rating', color='gentre',
                  hover_data=['movie_name'], title="rating vs Voting Count")
st.plotly_chart(fig7)




#filtration apply



import streamlit as st
import pymysql
import pandas as pd

# 💾 MySQL Connection using pymysql
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Rajarahi@22",
        database="mydatabase",
        cursorclass=pymysql.cursors.DictCursor
    )

# 🧠 Fetch filtered movies
def fetch_filtered_movies_data(duration, rating, votes, genre):
    con = get_connection()
    cursor = con.cursor()

    # 🕒 Duration SQL
    if duration == "< 2 hrs":
        duration_condition = "Duration < 120"
    elif duration == "2–3 hrs":
        duration_condition = "Duration BETWEEN 120 AND 180"
    elif duration == "> 3 hrs":
        duration_condition = "Duration > 180"
    else:
        duration_condition = "1"  # no filtering

    # 🛠️ Final SQL Query
    query = f"""
        SELECT * FROM movies_data
        WHERE {duration_condition}
        AND Rating >= %s
        AND Voting_Count >= %s
    """

    params = [rating, votes]

    if genre != "All":
        query += " AND gentre = %s"
        params.append(genre)

    cursor.execute(query, params)
    results = cursor.fetchall()
    con.close()

    return pd.DataFrame(results)

# 🎬 Streamlit App
st.title("🎬 Movie Filter App (with PyMySQL)")

# 🎛️ Filters inside expander
with st.expander("🎛️ Click to Select Filters"):
    duration_filter = st.selectbox("🕒 Duration", ["All", "< 2 hrs", "2–3 hrs", "> 3 hrs"])
    rating_filter = st.slider("⭐ Minimum IMDb Rating", 0.0, 10.0, 7.0, 0.1)
    votes_filter = st.number_input("👥 Minimum Voting Count", min_value=1000, value=100000)
    genre_filter = st.selectbox("🎭 Genre", ["All", "Western", "History", "Animation", "Adventure","Biograby"])
    apply_filter = st.button("🎯 Apply Filters")

# 📋 Table Output
if apply_filter:
    filtered_df = fetch_filtered_movies_data(duration_filter, rating_filter, votes_filter, genre_filter)

    if not filtered_df.empty:
        with st.expander("📋 Filtered Results (Click to Expand Table)"):
            st.subheader("📋 Filtered Results (SQL WHERE Style)")
            st.write(f"✅ {len(filtered_df)} movies match all selected conditions.")
            st.dataframe(
                filtered_df[['movie_name', 'gentre', 'Rating', 'Voting_Count', 'Duration']]
                .sort_values(by='Rating', ascending=False)
                .reset_index(drop=True),
                use_container_width=True
            )
    else:
        st.warning("😕 No movies found for the selected filters.")









