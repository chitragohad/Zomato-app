import sys
from pathlib import Path

import pandas as pd
import pytest

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.preprocessor import preprocess_dataframe


@pytest.fixture
def sample_raw_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "name": "Test Restaurant",
                "address": "123 Main Road, Koramangala, Bangalore",
                "location": "Koramangala",
                "rate": "4.5/5",
                "votes": 100,
                "cuisines": "North Indian, Chinese",
                "approx_cost(for two people)": "800",
                "url": "https://example.com/1",
                "rest_type": "Casual Dining",
                "listed_in(city)": "Koramangala",
            },
            {
                "name": "Budget Bites",
                "address": "45 Street, Indiranagar, Bengaluru",
                "location": "Indiranagar",
                "rate": "-",
                "votes": 10,
                "cuisines": "South Indian",
                "approx_cost(for two people)": "",
                "url": "https://example.com/2",
                "rest_type": "Quick Bites",
                "listed_in(city)": "Indiranagar",
            },
            {
                "name": "",
                "address": "No name row, Bangalore",
                "location": None,
                "rate": "3.0/5",
                "votes": 5,
                "cuisines": "Italian",
                "approx_cost(for two people)": "300",
                "url": "",
                "rest_type": None,
                "listed_in(city)": None,
            },
        ]
    )


@pytest.fixture
def sample_processed_df(sample_raw_df) -> pd.DataFrame:
    return preprocess_dataframe(sample_raw_df)
