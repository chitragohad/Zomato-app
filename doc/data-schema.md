# Data Schema: Zomato Hugging Face Dataset

**Source:** [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)  
**Rows:** 51,717  
**Primary city:** Bangalore (~97% of records)

---

## Raw Columns (Hugging Face)

| Raw column | Type | Example | Canonical mapping |
|------------|------|---------|-------------------|
| `name` | string | `Jalsa` | `name` |
| `address` | string | `942, 21st Main Road..., Bangalore` | `city` (extracted), `raw_metadata.address` |
| `location` | string | `Banashankari` | `location_detail` |
| `rate` | string | `4.1/5` | `rating` (float 0–5) |
| `votes` | int | `775` | `votes` |
| `cuisines` | string | `North Indian, Mughlai, Chinese` | `cuisines` (list) |
| `approx_cost(for two people)` | string | `800` | `cost_for_two` (int INR) |
| `url` | string | `https://www.zomato.com/...` | `raw_metadata.url`, used in `id` hash |
| `rest_type` | string | `Casual Dining` | `raw_metadata.rest_type` |
| `listed_in(city)` | string | `Banashankari` | `raw_metadata.listed_in_city` (area, not city) |
| `online_order` | string | `Yes` | not mapped (Phase 1) |
| `book_table` | string | `Yes` | not mapped |
| `phone` | string | — | not mapped |
| `dish_liked` | string | — | not mapped |
| `reviews_list` | string | — | not mapped |
| `menu_item` | string | — | not mapped |
| `listed_in(type)` | string | `Buffet` | not mapped |

---

## Canonical Schema (Parquet cache)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | SHA256 hash prefix of name+address+url |
| `name` | string | yes | |
| `city` | string | yes | Extracted from address; aliases normalized |
| `location_detail` | string | null | Zomato `location` field (area) |
| `cuisines` | list[string] | yes | Split on `,` |
| `rating` | float | null | Parsed from `rate`; null if missing/invalid |
| `cost_for_two` | int | null | INR for two people |
| `budget_tier` | string | null | `low` / `medium` / `high` via 33/66 percentiles |
| `votes` | int | null | |
| `raw_metadata` | object | yes | url, address, rest_type, listed_in_city |

---

## City Extraction Rules

1. Scan address for major cities (Delhi, Mumbai, Hyderabad, …)
2. Scan for Bangalore keywords (`bangalore`, `bengaluru`, …)
3. Map last address segment via `CITY_ALIASES`
4. Default to `Bangalore` for area-only addresses (dataset is Bangalore-centric)

---

## Null Rates (approximate, raw data)

| Field | Null % |
|-------|--------|
| `name` | 0% |
| `address` | 0% |
| `rate` | ~15% |
| `cuisines` | <1% |
| `approx_cost(for two people)` | <1% |

---

## Budget Tier Assignment

Uses 33rd and 66th percentiles of `cost_for_two` (clipped at 1st–99th percentile):

- `low`: cost ≤ p33
- `medium`: p33 < cost ≤ p66
- `high`: cost > p66

Rows with null `cost_for_two` have null `budget_tier`.
