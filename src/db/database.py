class SalesDatabase:
    def connect(host, port, dbname, user, password,):
        pass

    def disconnect():
        pass

    def is_connected() -> bool:
        pass

    def create_schema():
        pass

    def drop_schema():
        pass

    def import_dataset(dataset) -> int:
        pass

    def get_revenue_by_category() -> list[tuple[str, float]]:
        pass

    def get_top_sellers(n=5) -> list[tuple[str, float]]:
        pass

    def get_monthly_summary() -> list[tuple[str, float]]:
        pass

    def get_transaction_count() -> int:
        pass