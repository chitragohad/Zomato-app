from src.data.repository import RestaurantRepository

__all__ = ["RestaurantRepository"]


def __getattr__(name: str):
    if name in ("ingest_dataset", "load_raw_dataset"):
        from src.data.loader import ingest_dataset, load_raw_dataset
        return ingest_dataset if name == "ingest_dataset" else load_raw_dataset
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
