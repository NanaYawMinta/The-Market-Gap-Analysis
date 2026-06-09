# Snack Market Gap Analysis

A snack manufacturer wants to identify underserved product opportunities using nutritional data from OpenFoodFacts.

Source: OpenFoodFacts

330,000+ snack products extracted from the global food database.

1. Data Ingestion
2. Data Cleaning
3. Category Engineering
4. Nutritional Feature Engineering
5. Nutrition Opportunity Score (NOS)
6. K-Means Segmentation
7. Ingredient Intelligence
8. Interactive Streamlit Dashboard

## Executive Summary

This project analyzes over 330,000 snack products from OpenFoodFacts to identify underserved opportunities in the snack market.

After cleaning and categorizing products, a custom Nutrition Opportunity Score (NOS) was developed to quantify market gaps based on protein, fiber, sugar, and category saturation.

The analysis identified protein bars as the strongest opportunity category. K-Means clustering further revealed a distinct high-protein segment characterized by high protein, high fiber, and relatively low sugar content.

Ingredient analysis showed that soy, peanuts, whey, and almonds are the most common protein sources among successful high-protein products.

Based on these findings, the recommended product strategy is a high-protein snack delivering 20–30g protein, less than 12g sugar, and 6–10g fiber.


## Candidate's Choice Feature

A custom Nutrition Opportunity Score (NOS) was introduced to identify underserved market segments.

NOS combines nutritional quality and market saturation into a single metric:

NOS = (Protein + Fiber - Sugar) / log(1 + Product Count)

This feature was not required in the project brief but was added to provide a quantitative ranking of market opportunities rather than relying solely on visual inspection.

The metric enables direct comparison between categories and supports data-driven product recommendations.


## Key Findings

- Protein Bars achieved the highest Nutrition Opportunity Score (3.39).
- A distinct High-Protein cluster was identified through K-Means segmentation.
- Most products are concentrated in high-sugar regions.
- High-protein, low-sugar snacks remain comparatively scarce.
- Soy, peanuts, whey, and almonds are the dominant protein ingredients.


## Recommendation

Develop a high-protein snack containing:

- 20–30g protein
- Less than 12g sugar
- 6–10g fiber

The data suggests this segment is underserved relative to demand.
