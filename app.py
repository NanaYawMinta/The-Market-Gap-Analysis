import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Snack Market Gap Analysis",
    layout="wide"
)

cluster_df = pd.read_csv("data/cluster_df.csv")
nos_df = pd.read_csv("data/nos_df.csv")
ingredient_counts = pd.read_csv("data/ingredient_counts.csv")

st.title("🥨 Snack Market Gap Analysis")

st.markdown("""
This project identifies underserved opportunities in the snack market
using nutritional data from OpenFoodFacts.
""")


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Products",
    f"{len(cluster_df):,}"
)

col2.metric(
    "Categories",
    cluster_df["snack_category"].nunique()
)

col3.metric(
    "Clusters",
    cluster_df["cluster"].nunique()
)

col4.metric(
    "Opportunity Products",
    f"{((cluster_df['proteins_100g'] >= 20) & (cluster_df['sugars_100g'] <= 12)).sum():,}"
)

st.divider()

st.subheader("📌 Executive Recommendation")

st.success(
"""
Based on nutritional clustering, category analysis,
and the Nutrition Opportunity Score (NOS),

the strongest market opportunity is:

• High-protein snacks
• Less than 12g sugar
• Around 20g protein per 100g

The Protein Bar category achieved the highest
Nutrition Opportunity Score.
"""
)



st.divider()

st.subheader("Sugar vs Protein Market Landscape")

sample_df = cluster_df.sample(
    min(10000, len(cluster_df)),
    random_state=42
)

fig = px.scatter(
    sample_df,
    x="sugars_100g",
    y="proteins_100g",
    color="snack_category",
    opacity=0.6,
    title="Nutrient Matrix"
)

fig.add_vline(
    x=12,
    line_dash="dash"
)

fig.add_hline(
    y=20,
    line_dash="dash"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.divider()

st.subheader("Nutrition Opportunity Score (NOS)")


fig = px.bar(
    nos_df.sort_values(
        "NOS",
        ascending=False
    ),
    x="snack_category",
    y="NOS"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.divider()

st.subheader("Top Protein Ingredients")


fig = px.bar(
    ingredient_counts.head(10),
    x="ingredient",
    y="count"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.divider()

st.subheader("Market Segments")


cluster_summary = (
    cluster_df
    .groupby("cluster")
    [
        [
            "proteins_100g",
            "sugars_100g",
            "fiber_100g",
            "fat_100g"
        ]
    ]
    .mean()
    .round(2)
)

st.dataframe(
    cluster_summary,
    use_container_width=True
)


st.divider()



st.divider()

st.subheader("Market Segments Discovered by K-Means")


cluster_sample = cluster_df.sample(
    min(10000, len(cluster_df)),
    random_state=42
)

fig = px.scatter(
    cluster_sample,
    x="sugars_100g",
    y="proteins_100g",
    color="cluster",
    title="K-Means Segmentation of Snack Products",
    opacity=0.6
)

fig.add_vline(
    x=12,
    line_dash="dash"
)

fig.add_hline(
    y=20,
    line_dash="dash"
)

st.plotly_chart(
    fig,
    use_container_width=True
)



cluster_names = {
    0: "Energy Dense Snacks",
    1: "Light Snacks",
    2: "High Sugar Snacks",
    3: "High Protein Snacks"
}

cluster_df["cluster_name"] = (
    cluster_df["cluster"]
    .map(cluster_names)
)


cluster_df["cluster_name"].value_counts()





st.subheader("🎯 Opportunity Zone")



st.markdown(
"""
The dashed lines represent:

- 20g protein threshold
- 12g sugar threshold

Products in the upper-left quadrant are
high-protein and low-sugar.

This quadrant contains relatively few products
compared to the rest of the market, indicating
an attractive product-development opportunity.
"""
)

st.success(
"""
RECOMMENDED PRODUCT STRATEGY

Target Segment:
High-Protein Snacks

Target Nutrition Profile:
• Protein: 20–30g per 100g
• Sugar: < 12g per 100g
• Fiber: 6–10g per 100g

Evidence:
1. Protein Bars achieved the highest Nutrition Opportunity Score.
2. K-Means identified a distinct high-protein cluster.
3. Most products are concentrated in high-sugar regions.
4. High-protein, low-sugar products remain comparatively scarce.
5. Soy, whey, peanuts and almonds appear repeatedly in successful products.

Business Implication:
The strongest opportunity is not another cookie or candy product.
The data suggests developing a functional, protein-focused snack
with controlled sugar content.
"""
)


st.subheader(" Nutrition Opportunity Score")


st.markdown(
"""
I created a custom metric called the Nutrition Opportunity Score (NOS).

NOS rewards categories that combine:

- High protein
- High fiber
- Low sugar

while adjusting for category size.

This converts a subjective question
('Which category looks promising?')
into a quantitative ranking.

The result was Protein Bars ranking #1.
"""
)
