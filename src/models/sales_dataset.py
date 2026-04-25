class SalesDataset():
  def __init__(self, records=None):
    self.records = records or []

  def add(self, record):
    self.records.append(record)

  def __len__(self):
    return len(self.records)

  def __iter__(self):
    return iter(self.records)

  def __contains__(self, item):
    return item in self.records

  def filter_by_category(self, category):
    return SalesDataset([r for r in self.records if r.product.category.lower() == category.lower()])

  def filter_by_seller(self, seller):
    return SalesDataset([r for r in self.records if r.seller.lower() == seller.lower()])

  def filter_by_region(self, region):
    return SalesDataset([r for r in self.records if r.region.lower() == region.lower()])

  def filter_by_date_range(self, start, end):
    return SalesDataset([r for r in self.records if start <= r.date <= end])

  def categories(self):
    return set(r.product.category for r in self.records)

  def sellers(self):
    return set(r.seller for r in self.records)

  def regions(self):
    return set(r.region for r in self.records)