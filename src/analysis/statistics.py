from collections import defaultdict

class SalesStatistics:
  def __init__(self, dataset):
    self.dataset = dataset

  def total_revenue(self):
    return sum(r.total_value() for r in self.dataset)

  def average_transaction(self):
    if len(self.dataset) == 0:
      raise ValueError("Pusty zbiór")
    return self.total_revenue() / len(self.dataset)

  def revenue_by(self, key_func):
    result = defaultdict(float)
    for r in self.dataset:
      result[key_func(r)] += r.total_value()
    return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

  def by_category(self):
    return self.revenue_by(lambda r: r.product.category)

  def by_seller(self):
    return self.revenue_by(lambda r: r.seller)

  def by_region(self):
    return self.revenue_by(lambda r: r.region)

  def monthly_summary(self):
    result = defaultdict(float)
    for r in self.dataset:
      key = r.date.strftime("%Y-%m")
      result[key] += r.total_value()
    return dict(sorted(result.items()))

  def top_products(self, n=5):
    result = defaultdict(float)
    for r in self.dataset:
      result[r.product.name] += r.total_value()
    return sorted(result.items(), key=lambda x: x[1], reverse=True)[:n]

  def best_seller(self):
    return next(iter(self.by_seller().items()), None)

  def best_month(self):
    return max(self.monthly_summary().items(), key=lambda x: x[1], default=None)