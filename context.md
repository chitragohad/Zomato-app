# Project Context: AI-Powered Restaurant Recommendation System (Zomato Use Case)

This document captures the full context from `doc/problemStatement.txt` for building and extending this application.

---

## Overview

Build an **AI-powered restaurant recommendation service** inspired by Zomato. The system suggests restaurants based on user preferences by combining **structured restaurant data** with a **Large Language Model (LLM)** to produce personalized, human-like recommendations.

---

## Objective

Design and implement an application that:

1. Accepts user preferences (location, budget, cuisine, ratings, and more)
2. Uses a real-world restaurant dataset
3. Leverages an LLM to generate personalized, human-like recommendations
4. Displays clear, useful results to the user

---

## Data Source

| Item | Detail |
|------|--------|
| **Dataset** | Zomato restaurant data on Hugging Face |
| **URL** | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |
| **Relevant fields** | Restaurant name, location, cuisine, cost, rating, and related attributes |

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face
- Extract fields: restaurant name, location, cuisine, cost, rating, etc.

### 2. User Input

Collect user preferences:

| Preference | Examples / Notes |
|------------|------------------|
| **Location** | Delhi, Bangalore |
| **Budget** | low, medium, high |
| **Cuisine** | Italian, Chinese |
| **Minimum rating** | Numeric threshold |
| **Additional** | family-friendly, quick service, etc. |

### 3. Integration Layer

- Filter and prepare restaurant data based on user input
- Pass structured, filtered results into an LLM prompt
- Design a prompt that helps the LLM **reason** and **rank** options

### 4. Recommendation Engine (LLM)

The LLM should:

- Rank restaurants
- Provide explanations (why each recommendation fits the user)
- Optionally summarize the overall set of choices

### 5. Output Display

Present top recommendations in a user-friendly format. Each recommendation should include:

| Field | Description |
|-------|-------------|
| **Restaurant Name** | Name of the venue |
| **Cuisine** | Type(s) of food |
| **Rating** | User/restaurant rating |
| **Estimated Cost** | Price indication |
| **AI-generated explanation** | Why this restaurant was recommended |

---

## Architecture Summary

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Hugging Face   │────▶│  Data Ingestion  │────▶│  Structured DB  │
│  Zomato Dataset │     │  & Preprocessing │     │  / DataFrame    │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                            │
┌─────────────────┐     ┌──────────────────┐               │
│  User Preferences│────▶│  Filter & Prepare │◀──────────────┘
│  (location, etc)│     │  Relevant Records │
└─────────────────┘     └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  LLM Prompt      │
                        │  (rank + explain)│
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  Output Display  │
                        │  Top picks + why │
                        └──────────────────┘
```

---

## Key Requirements Checklist

- [ ] Load Zomato dataset from Hugging Face
- [ ] Preprocess and extract required fields
- [ ] UI or flow for user preference input
- [ ] Filter restaurants by user criteria before LLM call
- [ ] LLM integration with a well-designed ranking/explanation prompt
- [ ] Display: name, cuisine, rating, cost, AI explanation

---

## Source Document

Full original problem statement: `doc/problemStatement.txt`
