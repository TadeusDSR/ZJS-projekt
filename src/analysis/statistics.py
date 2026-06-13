class SalesStatistics:
    def __init__(self, dataset):
        self.dataset = dataset

    def total_revenue(self):
        return sum(record.total_value() for record in self.dataset)

    def average_transaction(self):
        if len(self.dataset) == 0:
            return 0.0
        return self.total_revenue() / len(self.dataset)

    def revenue_by(self, key_func):
        result = {}

        for record in self.dataset:
            key = key_func(record)
            result[key] = result.get(key, 0.0) + record.total_value()

        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    def by_category(self):
        return self.revenue_by(lambda record: record.product.category)

    def by_seller(self):
        return self.revenue_by(lambda record: record.seller)

    def by_region(self):
        return self.revenue_by(lambda record: record.region)

    def monthly_summary(self):
        result = {}

        for record in self.dataset:
            key = record.date.strftime("%Y-%m")
            result[key] = result.get(key, 0.0) + record.total_value()

        return dict(sorted(result.items()))

    def top_products(self, n=5):
        result = {}

        for record in self.dataset:
            name = record.product.name
            result[name] = result.get(name, 0.0) + record.total_value()

        return sorted(result.items(), key=lambda x: x[1], reverse=True)[:n]

    def best_seller(self):
        return max(self.by_seller().items(), key=lambda x: x[1])

    def best_month(self):
        return max(self.monthly_summary().items(), key=lambda x: x[1])