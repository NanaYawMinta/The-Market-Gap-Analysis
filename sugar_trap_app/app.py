import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Sugar Trap | Snack Market Intelligence",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# THEME COLORS
# ─────────────────────────────────────────────────────────
TEAL    = "#0D9488"
NAVY    = "#0F1F3D"
CORAL   = "#F96167"
AMBER   = "#F59E0B"
MINT    = "#5EEAD4"
GRAY    = "#64748B"

# ─────────────────────────────────────────────────────────
# EMBEDDED DATA  (from notebook outputs — no CSVs needed)
# ─────────────────────────────────────────────────────────

CATEGORY_SUMMARY_CSV = """snack_category,proteins_100g,sugars_100g,fiber_100g,health_score
candy_chocolate,6.33,40.86,3.93,-30.59
chips,6.57,3.48,4.04,7.13
cookies,6.64,27.35,3.24,-17.47
crackers,10.17,4.52,4.45,10.09
nuts,16.02,14.44,6.04,7.62
other_snacks,7.37,31.53,3.81,-20.35
popcorn,7.10,16.93,6.71,-3.12
pretzels,9.97,6.36,3.78,7.39
protein_bars,28.89,12.53,8.39,24.74
"""

NOS_CSV = """snack_category,product_count,mean_protein,mean_fiber,mean_sugar,NOS
protein_bars,1388,28.693201,8.387256,12.547789,3.390204
pretzels,155,9.967249,3.783722,6.361876,1.463229
crackers,2438,10.158954,4.447430,4.518401,1.293440
nuts,8917,15.899840,6.025479,14.319633,0.836173
chips,15272,6.530784,4.018823,3.481242,0.733702
popcorn,1481,7.028829,6.622308,17.022154,-0.461711
cookies,50816,6.587076,3.216145,27.329076,-1.617375
other_snacks,90623,7.341601,3.741007,30.666817,-1.715735
candy_chocolate,14678,6.322704,3.935741,40.776728,-3.180919
"""

INGREDIENT_CSV = """ingredient,count
soy,4022
pea,3607
peanut,2420
peanuts,2036
whey,1688
almond,1541
almonds,1284
cashew,1131
egg,1059
oats,919
soy protein,605
pea protein,358
"""

CLUSTER_SUMMARY_CSV = """cluster,energy_kcal,fat_100g,sugars_100g,fiber_100g,proteins_100g,label,description
0,501.29,27.93,27.92,3.29,6.91,Indulgent Sweets,"High-fat, high-sugar. Dominated by cookies, chips, candy."
1,276.21,9.47,11.47,2.93,5.81,Light Snackers,"Lower calorie, moderate sugar. Mixed savory snacks, some cookies."
2,370.55,6.08,57.34,2.71,3.44,Sugar-Heavy,"Very high sugar, low fat. Candy and sweet confections."
3,509.58,34.26,10.32,9.95,20.79,Protein & Fiber Champions,"High protein (20.8g), high fiber (9.95g), low sugar. Nuts & protein bars."
"""

CLUSTER_COMPOSITION = {
    0: {"other_snacks": 40604, "cookies": 35230, "chips": 12706, "candy_chocolate": 10228,
        "nuts": 2472, "crackers": 996, "popcorn": 594, "protein_bars": 83, "pretzels": 38},
    1: {"other_snacks": 24695, "cookies": 9102, "chips": 2336, "candy_chocolate": 1309,
        "crackers": 1190, "nuts": 697, "popcorn": 388, "pretzels": 112, "protein_bars": 77},
    2: {"other_snacks": 18395, "cookies": 6064, "candy_chocolate": 2419, "popcorn": 260,
        "nuts": 130, "chips": 65, "protein_bars": 11, "crackers": 9},
    3: {"other_snacks": 8532, "nuts": 5929, "cookies": 1362, "protein_bars": 1285,
        "candy_chocolate": 1139, "chips": 666, "crackers": 317, "popcorn": 279, "pretzels": 7},
}

# ─────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    category_summary = pd.read_csv(StringIO(CATEGORY_SUMMARY_CSV))
    nos_df = pd.read_csv(StringIO(NOS_CSV))
    ingredient_counts = pd.read_csv(StringIO(INGREDIENT_CSV))
    cluster_summary = pd.read_csv(StringIO(CLUSTER_SUMMARY_CSV))

    # Clean category labels
    for df in [category_summary, nos_df]:
        col = "snack_category"
        df[col] = df[col].str.replace("_", " ").str.title()

    cluster_summary["label"] = cluster_summary["label"]

    return category_summary, nos_df, ingredient_counts, cluster_summary

category_summary, nos_df, ingredient_counts, cluster_summary = load_data()

CATEGORY_COLORS = {
    "Protein Bars":     TEAL,
    "Nuts":             "#22D3C3",
    "Pretzels":         AMBER,
    "Crackers":         "#84CC16",
    "Chips":            "#A3E635",
    "Popcorn":          "#FBBF24",
    "Cookies":          CORAL,
    "Other Snacks":     "#FB923C",
    "Candy Chocolate":  "#F43F5E",
}

# ─────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #F0FAFA; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F1F3D 0%, #1a3356 100%);
    }
    [data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    [data-testid="stSidebar"] .stRadio label { color: #5EEAD4 !important; font-weight: 600; }

    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #0D9488;
        margin-bottom: 8px;
    }
    .metric-value { font-size: 2rem; font-weight: 800; color: #0D9488; margin: 0; }
    .metric-label { font-size: 0.85rem; color: #64748B; margin: 0; }

    /* Insight boxes */
    .insight-box {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 8px rgba(0,0,0,0.07);
        margin-bottom: 12px;
    }
    .insight-box h4 { color: #0F1F3D; margin-top: 0; margin-bottom: 6px; font-size: 0.95rem; }
    .insight-box p  { color: #475569; margin: 0; font-size: 0.88rem; line-height: 1.5; }

    /* Page title */
    .page-header {
        background: linear-gradient(135deg, #0F1F3D 0%, #1a3a6b 100%);
        border-radius: 14px;
        padding: 28px 36px;
        margin-bottom: 24px;
    }
    .page-header h1 { color: white; margin: 0 0 6px 0; font-size: 1.9rem; }
    .page-header p  { color: #5EEAD4; margin: 0; font-size: 1rem; }

    /* NOS badge */
    .nos-positive { color: #0D9488; font-weight: 800; }
    .nos-negative { color: #F96167; font-weight: 800; }

    /* Section header */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F1F3D;
        margin: 8px 0 16px 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #0D9488;
    }

    /* Hide streamlit branding */
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍫 The Sugar Trap")
    st.markdown("*Snack Market Intelligence*")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊 Executive Summary",
         "🎯 NOS Rankings",
         "🥗 Category Nutrition",
         "🤖 Market Clusters",
         "🌿 Ingredient Intelligence",
         "📈 Opportunity Finder"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Dataset**")
    st.markdown("OpenFoodFacts · 190,171 products")
    st.markdown("**Categories**")
    st.markdown("9 snack segments")
    st.markdown("**Method**")
    st.markdown("KMeans + NOS scoring")
    st.markdown("---")
    st.markdown("<small style='color:#64748B'>Helix CPG Partners<br>Market Intelligence Assessment</small>",
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────
def metric_card(value, label, color=TEAL):
    st.markdown(f"""
    <div class="metric-card" style="border-left-color:{color}">
        <p class="metric-value" style="color:{color}">{value}</p>
        <p class="metric-label">{label}</p>
    </div>""", unsafe_allow_html=True)

def section_title(text):
    st.markdown(f'<p class="section-title">{text}</p>', unsafe_allow_html=True)

def insight_box(title, body):
    st.markdown(f"""
    <div class="insight-box">
        <h4>{title}</h4>
        <p>{body}</p>
    </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ═════════════════════════════════════════════════════════
if page == "📊 Executive Summary":
    st.markdown("""
    <div class="page-header">
        <h1>🍫 The Sugar Trap</h1>
        <p>Snack Market Gap Analysis · OpenFoodFacts · 190,171 products across 9 categories</p>
    </div>""", unsafe_allow_html=True)

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("190,171", "Products Analyzed", TEAL)
    with c2: metric_card("+3.39", "Top NOS — Protein Bars", "#22D3C3")
    with c3: metric_card("−15.8", "Avg Health Score (all snacks)", CORAL)
    with c4: metric_card("4", "Market Clusters (KMeans)", AMBER)

    st.markdown("")
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        section_title("NOS Rankings at a Glance")
        nos_sorted = nos_df.copy().sort_values("NOS")
        colors = [TEAL if v >= 0 else CORAL for v in nos_sorted["NOS"]]

        fig = go.Figure(go.Bar(
            x=nos_sorted["NOS"],
            y=nos_sorted["snack_category"],
            orientation="h",
            marker_color=colors,
            text=[f"+{v:.2f}" if v >= 0 else f"{v:.2f}" for v in nos_sorted["NOS"]],
            textposition="outside",
            textfont_size=12,
        ))
        fig.update_layout(
            height=380,
            margin=dict(l=10, r=80, t=10, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#E2E8F0", zeroline=True,
                       zerolinecolor="#94A3B8", zerolinewidth=2,
                       title="Nutritional Opportunity Score (NOS)"),
            yaxis=dict(showgrid=False, title=""),
            font=dict(family="Inter, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_title("Key Findings")
        insight_box("🏆 Protein Bars Lead",
            "NOS of +3.39 — strongest nutritional signal vs. only 1,388 products. Massively underserved relative to demand.")
        insight_box("🍬 Sugar Dominates the Market",
            "Average health score across all snacks is −15.8. Sugar overload is the norm — candy averages 40.9g/100g.")
        insight_box("🌿 Plant Protein is Underused",
            "Soy & pea protein appear in under 5K opportunity products. Clear formulation white space for innovation.")
        insight_box("🎯 Cluster 3 = Opportunity Zone",
            "KMeans Cluster 3 shows 20.8g protein, 9.95g fiber, only 10.3g sugar — sparse and nutritionally superior.")

    st.markdown("---")
    st.markdown("### Final Recommendation")
    st.success("**Launch target: High-protein, plant-based snack bar** · Protein ≥25g · Sugar <12g · Fiber ≥6g · Leverage soy, pea, or whey protein sources")


# ═════════════════════════════════════════════════════════
# PAGE 2 — NOS RANKINGS
# ═════════════════════════════════════════════════════════
elif page == "🎯 NOS Rankings":
    st.markdown("""
    <div class="page-header">
        <h1>🎯 Nutritional Opportunity Score</h1>
        <p>NOS = (mean_protein + mean_fiber − mean_sugar) / log₁₊(product_count)</p>
    </div>""", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        section_title("Formula Explained")
        st.markdown("""
        The **NOS** is a proprietary market intelligence metric that combines:
        
        | Component | Direction | Rationale |
        |-----------|-----------|-----------|
        | Mean Protein | ➕ Rewards | Consumer demand for protein |
        | Mean Fiber | ➕ Rewards | Health positioning value |
        | Mean Sugar | ➖ Penalizes | Unhealthy perception |
        | log₁₊(count) | ÷ Dampens | Penalizes saturated markets |
        
        **Higher NOS = better nutritional profile AND less competition.**
        """)

        st.markdown("")
        section_title("All Category Scores")
        nos_display = nos_df[["snack_category","NOS","product_count","mean_protein","mean_fiber","mean_sugar"]].copy()
        nos_display.columns = ["Category","NOS","Products","Avg Protein","Avg Fiber","Avg Sugar"]
        nos_display = nos_display.sort_values("NOS", ascending=False).reset_index(drop=True)
        nos_display["NOS"] = nos_display["NOS"].round(2)

        def color_nos(val):
            color = "#0D9488" if val > 0 else "#F96167"
            return f"color: {color}; font-weight: 700"

        st.dataframe(
            nos_display.style.map(color_nos, subset=["NOS"]),
            use_container_width=True,
            hide_index=True,
        )

    with col_right:
        section_title("NOS vs Market Size")
        fig = px.scatter(
            nos_df,
            x="product_count",
            y="NOS",
            size="mean_protein",
            color="snack_category",
            color_discrete_map={k: v for k, v in CATEGORY_COLORS.items()},
            text="snack_category",
            hover_data={"mean_protein": ":.1f", "mean_sugar": ":.1f", "mean_fiber": ":.1f"},
            labels={"product_count": "Number of Products in Market",
                    "NOS": "Nutritional Opportunity Score",
                    "mean_protein": "Avg Protein (g)"},
        )
        fig.update_traces(textposition="top center", textfont_size=10)
        fig.add_hline(y=0, line_dash="dash", line_color=GRAY, opacity=0.6)
        fig.update_layout(
            height=480,
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=True, gridcolor="#E2E8F0", title="Number of Products (Market Size)"),
            yaxis=dict(showgrid=True, gridcolor="#E2E8F0", title="NOS"),
            margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info("💡 **Top-left quadrant** = high NOS + small market = strongest opportunity. Protein Bars sit there clearly.")


# ═════════════════════════════════════════════════════════
# PAGE 3 — CATEGORY NUTRITION
# ═════════════════════════════════════════════════════════
elif page == "🥗 Category Nutrition":
    st.markdown("""
    <div class="page-header">
        <h1>🥗 Category Nutritional Profiles</h1>
        <p>Mean macronutrients per 100g across 9 snack categories · 190,171 clean products</p>
    </div>""", unsafe_allow_html=True)

    # Selector
    nutrient = st.selectbox(
        "Select nutrient to compare:",
        ["health_score", "proteins_100g", "sugars_100g", "fiber_100g"],
        format_func=lambda x: {
            "health_score": "Health Score (Protein + Fiber − Sugar)",
            "proteins_100g": "Average Protein (g per 100g)",
            "sugars_100g": "Average Sugar (g per 100g)",
            "fiber_100g": "Average Fiber (g per 100g)",
        }[x],
    )

    sorted_df = category_summary.sort_values(nutrient, ascending=False)
    bar_colors = [TEAL if v >= 0 else CORAL for v in sorted_df[nutrient]]

    fig = px.bar(
        sorted_df,
        x="snack_category",
        y=nutrient,
        color_discrete_sequence=[TEAL],
        text=sorted_df[nutrient].round(1),
        labels={"snack_category": "Snack Category", nutrient: nutrient.replace("_", " ").title()},
    )
    fig.update_traces(marker_color=bar_colors, textposition="outside")
    fig.update_layout(
        height=380,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        font=dict(family="Inter, sans-serif"),
        xaxis=dict(showgrid=False, tickangle=-20),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0"),
        margin=dict(t=20, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("")
    section_title("Full Nutritional Profile Comparison")

    # Radar chart — multi-category comparison
    selected_cats = st.multiselect(
        "Select categories to compare on radar:",
        options=category_summary["snack_category"].tolist(),
        default=["Protein Bars", "Cookies", "Nuts", "Candy Chocolate"],
    )

    if selected_cats:
        fig2 = go.Figure()
        radar_cols = ["proteins_100g", "fiber_100g", "sugars_100g", "health_score"]
        radar_labels = ["Protein", "Fiber", "Sugar", "Health Score"]

        for cat in selected_cats:
            row = category_summary[category_summary["snack_category"] == cat].iloc[0]
            vals = [row[c] for c in radar_cols]
            # Normalize for radar
            maxes = [category_summary[c].abs().max() for c in radar_cols]
            norm = [v / m * 10 for v, m in zip(vals, maxes)]
            norm.append(norm[0])
            fig2.add_trace(go.Scatterpolar(
                r=norm,
                theta=radar_labels + [radar_labels[0]],
                name=cat,
                fill="toself",
                opacity=0.65,
            ))

        fig2.update_layout(
            height=400,
            polar=dict(radialaxis=dict(visible=True, showticklabels=False)),
            showlegend=True,
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif"),
            margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("")
    section_title("Raw Data Table")
    display_df = category_summary.rename(columns={
        "snack_category": "Category",
        "proteins_100g": "Protein (g)",
        "sugars_100g": "Sugar (g)",
        "fiber_100g": "Fiber (g)",
        "health_score": "Health Score",
    })
    st.dataframe(display_df.style.background_gradient(subset=["Health Score"], cmap="RdYlGn"),
                 use_container_width=True, hide_index=True)


# ═════════════════════════════════════════════════════════
# PAGE 4 — MARKET CLUSTERS
# ═════════════════════════════════════════════════════════
elif page == "🤖 Market Clusters":
    st.markdown("""
    <div class="page-header">
        <h1>🤖 KMeans Market Segmentation</h1>
        <p>4 clusters identified from energy, fat, sugar, fiber, protein · StandardScaler normalization</p>
    </div>""", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        section_title("Cluster Nutritional Profiles")
        cluster_display = cluster_summary[["cluster","label","energy_kcal","proteins_100g","sugars_100g","fiber_100g","fat_100g"]].copy()
        cluster_display.columns = ["ID","Cluster Name","Energy (kcal)","Protein","Sugar","Fiber","Fat"]
        st.dataframe(cluster_display, use_container_width=True, hide_index=True)

        st.markdown("")
        section_title("Cluster Descriptions")
        colors_map = {
            "Indulgent Sweets": CORAL,
            "Light Snackers": AMBER,
            "Sugar-Heavy": "#F43F5E",
            "Protein & Fiber Champions": TEAL,
        }
        for _, row in cluster_summary.iterrows():
            c = colors_map.get(row["label"], GRAY)
            st.markdown(f"""
            <div class="insight-box" style="border-left: 4px solid {c}; padding-left: 16px;">
                <h4 style="color:{c}">Cluster {int(row['cluster'])} — {row['label']}</h4>
                <p>{row['description']}</p>
            </div>""", unsafe_allow_html=True)

    with col_right:
        section_title("Macro Comparison by Cluster")
        nutrients = ["proteins_100g", "sugars_100g", "fiber_100g", "fat_100g"]
        labels = ["Protein", "Sugar", "Fiber", "Fat"]
        cluster_colors = [CORAL, AMBER, "#F43F5E", TEAL]

        fig = go.Figure()
        for i, (_, row) in enumerate(cluster_summary.iterrows()):
            fig.add_trace(go.Bar(
                name=f"C{int(row['cluster'])}: {row['label']}",
                x=labels,
                y=[row[n] for n in nutrients],
                marker_color=cluster_colors[i],
                opacity=0.85,
            ))

        fig.update_layout(
            barmode="group",
            height=360,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#E2E8F0", title="g per 100g"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
            margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        section_title("Cluster Composition (Product Count)")
        selected_cluster = st.selectbox("View cluster:", [0, 1, 2, 3],
            format_func=lambda x: f"Cluster {x} — {cluster_summary.loc[x, 'label']}")

        comp = CLUSTER_COMPOSITION[selected_cluster]
        comp_df = pd.DataFrame(list(comp.items()), columns=["Category", "Products"])
        comp_df["Category"] = comp_df["Category"].str.replace("_", " ").str.title()
        comp_df = comp_df.sort_values("Products", ascending=False)

        fig3 = px.pie(comp_df, values="Products", names="Category",
                      color_discrete_sequence=px.colors.sequential.Teal)
        fig3.update_layout(height=300, margin=dict(t=10, b=10),
                           paper_bgcolor="white", font=dict(family="Inter, sans-serif"))
        st.plotly_chart(fig3, use_container_width=True)


# ═════════════════════════════════════════════════════════
# PAGE 5 — INGREDIENT INTELLIGENCE
# ═════════════════════════════════════════════════════════
elif page == "🌿 Ingredient Intelligence":
    st.markdown("""
    <div class="page-header">
        <h1>🌿 Ingredient Intelligence</h1>
        <p>Protein source frequency in High-Protein / Low-Sugar opportunity products</p>
    </div>""", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        section_title("Protein Source Frequency")

        top_n = st.slider("Show top N ingredients:", 5, 12, 10)
        ing_top = ingredient_counts.head(top_n).sort_values("count")

        fig = go.Figure(go.Bar(
            x=ing_top["count"],
            y=ing_top["ingredient"],
            orientation="h",
            marker=dict(
                color=ing_top["count"],
                colorscale=[[0, "#5EEAD4"], [0.5, "#0D9488"], [1, "#0F1F3D"]],
                showscale=False,
            ),
            text=ing_top["count"].apply(lambda x: f"{x:,}"),
            textposition="outside",
        ))
        fig.update_layout(
            height=420,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=True, gridcolor="#E2E8F0", title="Number of Products Containing Ingredient"),
            yaxis=dict(showgrid=False, title=""),
            margin=dict(t=10, r=70, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_title("Ingredient Strategy")
        insight_box("🥇 Soy Leads (4,022 products)",
            "Most prevalent protein source. Versatile, cost-effective, and widely accepted — plant-based workhorse.")
        insight_box("🟢 Pea Protein Rising (3,607)",
            "Close second. Cleaner label perception than soy for health-conscious consumers. Strong allergen profile.")
        insight_box("🥜 Peanuts Strong (4,456 combined)",
            "Peanut + Peanuts combined dominate whole-food sources. Great for bars with whole-food positioning.")
        insight_box("🥛 Whey Holds (1,688)",
            "Traditional sports nutrition staple. Declining in new launches but high adoption in existing protein bars.")
        insight_box("🌰 Tree Nuts (2,956 combined)",
            "Almond + Almonds + Cashew signal premium positioning. Higher cost but strong consumer pull.")

        st.markdown("")
        section_title("Formulation Recommendation")
        st.success("""
        **Optimal protein stack for new entrant:**
        - Primary: Pea protein isolate (clean label + allergen-friendly)
        - Secondary: Soy protein concentrate (cost efficiency)
        - Texture: Almond or oat base
        - Target: ≥25g protein per 100g, <12g sugar
        """)


# ═════════════════════════════════════════════════════════
# PAGE 6 — OPPORTUNITY FINDER
# ═════════════════════════════════════════════════════════
elif page == "📈 Opportunity Finder":
    st.markdown("""
    <div class="page-header">
        <h1>📈 Interactive Opportunity Finder</h1>
        <p>Set your product's nutritional target and discover your market position</p>
    </div>""", unsafe_allow_html=True)

    col_form, col_chart = st.columns([1, 1], gap="large")

    with col_form:
        section_title("Define Your Target Product")
        target_protein = st.slider("Target Protein (g per 100g)", 0, 40, 25)
        target_sugar   = st.slider("Target Sugar (g per 100g)",   0, 60, 10)
        target_fiber   = st.slider("Target Fiber (g per 100g)",   0, 20, 6)

        st.markdown("")
        target_nos = (target_protein + target_fiber - target_sugar) / np.log1p(1)
        raw_nos_relative = (target_protein + target_fiber - target_sugar)

        st.markdown("---")
        st.markdown("### Your Product Score")

        health_score = target_protein + target_fiber - target_sugar
        c1, c2 = st.columns(2)
        with c1:
            color = TEAL if health_score > 0 else CORAL
            metric_card(f"{health_score:.1f}", "Health Score (P+F−S)", color)
        with c2:
            # Compare against category benchmarks
            comparable = nos_df[
                (nos_df["mean_protein"].between(target_protein - 8, target_protein + 8)) |
                (nos_df["mean_sugar"].between(target_sugar - 8, target_sugar + 8))
            ]["snack_category"].tolist()
            metric_card(len(comparable), "Comparable categories", AMBER)

        st.markdown("")
        # Recommendation
        if target_protein >= 20 and target_sugar <= 15:
            st.success("✅ **Strong Position** — Your protein/sugar profile aligns with the highest-NOS opportunity zone (Protein Bars / Cluster 3).")
        elif target_protein >= 12 and target_sugar <= 10:
            st.info("🔵 **Good Position** — Crackers/Nuts territory. Competitive but defensible with strong branding.")
        elif target_sugar > 30:
            st.error("🔴 **High Sugar Warning** — This profile sits in the crowded, low-NOS zone. Differentiating will be very difficult.")
        else:
            st.warning("🟡 **Moderate** — Decent nutritional profile but watch sugar content. Reduce sugar or increase protein for a stronger NOS.")

        section_title("How You Compare to Categories")
        comp_data = nos_df[["snack_category","mean_protein","mean_sugar","mean_fiber"]].copy()
        comp_data["type"] = "Market Category"

        your_row = pd.DataFrame([{
            "snack_category": "🎯 YOUR PRODUCT",
            "mean_protein": target_protein,
            "mean_sugar": target_sugar,
            "mean_fiber": target_fiber,
            "type": "Your Product",
        }])
        comp_data = pd.concat([comp_data, your_row], ignore_index=True)

        comp_data["health_score"] = comp_data["mean_protein"] + comp_data["mean_fiber"] - comp_data["mean_sugar"]

        comp_melted = comp_data.melt(
            id_vars=["snack_category", "type"],
            value_vars=["mean_protein", "mean_sugar", "mean_fiber"],
            var_name="Nutrient", value_name="Value"
        )
        comp_melted["Nutrient"] = comp_melted["Nutrient"].map({
            "mean_protein": "Protein", "mean_sugar": "Sugar", "mean_fiber": "Fiber"
        })

        fig_comp = px.bar(
            comp_melted[comp_melted["snack_category"].isin(
                ["🎯 YOUR PRODUCT", "Protein Bars", "Nuts", "Cookies", "Candy Chocolate", "Crackers"]
            )],
            x="snack_category", y="Value", color="Nutrient",
            barmode="group",
            color_discrete_map={"Protein": TEAL, "Sugar": CORAL, "Fiber": AMBER},
            labels={"snack_category": "", "Value": "g per 100g"},
        )
        fig_comp.update_layout(
            height=280,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=False, tickangle=-15),
            yaxis=dict(showgrid=True, gridcolor="#E2E8F0"),
            legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"),
            margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    with col_chart:
        section_title("Protein vs Sugar Landscape")
        scatter_df = nos_df.copy()

        fig_scatter = go.Figure()

        # Market categories
        for _, row in scatter_df.iterrows():
            fig_scatter.add_trace(go.Scatter(
                x=[row["mean_sugar"]],
                y=[row["mean_protein"]],
                mode="markers+text",
                marker=dict(
                    size=np.sqrt(row["product_count"]) / 8,
                    color=TEAL if row["NOS"] > 0 else CORAL,
                    opacity=0.7,
                    line=dict(width=1.5, color="white"),
                ),
                text=[row["snack_category"]],
                textposition="top center",
                textfont=dict(size=10),
                name=row["snack_category"],
                showlegend=False,
                hovertemplate=(
                    f"<b>{row['snack_category']}</b><br>"
                    f"Protein: {row['mean_protein']:.1f}g<br>"
                    f"Sugar: {row['mean_sugar']:.1f}g<br>"
                    f"NOS: {row['NOS']:.2f}<extra></extra>"
                ),
            ))

        # Your product
        fig_scatter.add_trace(go.Scatter(
            x=[target_sugar],
            y=[target_protein],
            mode="markers+text",
            marker=dict(size=22, color=AMBER, symbol="star",
                        line=dict(width=2, color=NAVY)),
            text=["🎯 You"],
            textposition="top center",
            textfont=dict(size=13, color=NAVY),
            name="Your Product",
            showlegend=True,
            hovertemplate=f"<b>Your Product</b><br>Protein: {target_protein}g<br>Sugar: {target_sugar}g<extra></extra>",
        ))

        # Quadrant lines
        fig_scatter.add_hline(y=6.4, line_dash="dash", line_color=GRAY, opacity=0.4)
        fig_scatter.add_vline(x=26.0, line_dash="dash", line_color=GRAY, opacity=0.4)

        # Opportunity annotation
        fig_scatter.add_annotation(
            x=5, y=38, text="✅ OPPORTUNITY ZONE<br>High Protein / Low Sugar",
            showarrow=False, font=dict(color=TEAL, size=11),
            bgcolor="rgba(240,255,255,0.8)", bordercolor=TEAL,
        )
        fig_scatter.add_annotation(
            x=50, y=4, text="❌ Saturated Zone<br>Low Protein / High Sugar",
            showarrow=False, font=dict(color=CORAL, size=11),
            bgcolor="rgba(255,240,240,0.8)", bordercolor=CORAL,
        )

        fig_scatter.update_layout(
            height=500,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=True, gridcolor="#E2E8F0", title="Average Sugar (g per 100g)", range=[-2, 50]),
            yaxis=dict(showgrid=True, gridcolor="#E2E8F0", title="Average Protein (g per 100g)", range=[-1, 35]),
            legend=dict(x=0.85, y=0.05),
            margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.caption("Bubble size = number of products. Teal = positive NOS, Coral = negative NOS. ⭐ = your target product.")
