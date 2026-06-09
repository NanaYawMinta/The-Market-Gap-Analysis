# 🍫 The Sugar Trap — Snack Market Intelligence Dashboard

A Streamlit dashboard for snack market gap analysis using the OpenFoodFacts dataset.

## Pages

| Page | Description |
|------|-------------|
| 📊 Executive Summary | KPIs, NOS ranking bar chart, key findings |
| 🎯 NOS Rankings | Formula breakdown, scatter plot, full rankings table |
| 🥗 Category Nutrition | Bar charts, radar comparison, nutrient deep-dive |
| 🤖 Market Clusters | KMeans cluster profiles, composition pie charts |
| 🌿 Ingredient Intelligence | Protein source frequency, formulation recommendations |
| 📈 Opportunity Finder | Interactive sliders — position your own product concept |

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud (Free)

1. Push this folder to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Click **Deploy** — done in ~2 minutes

No CSV files needed — all data is embedded in the app.

## Data Sources

- **Dataset**: OpenFoodFacts public database
- **Products analyzed**: 190,171 clean snack records
- **Categories**: 9 snack segments
- **Method**: KMeans clustering (k=4) + proprietary NOS scoring

## NOS Formula

```
NOS = (mean_protein + mean_fiber − mean_sugar) / log₁₊(product_count)
```

Higher NOS = stronger nutritional profile AND less market crowding.
