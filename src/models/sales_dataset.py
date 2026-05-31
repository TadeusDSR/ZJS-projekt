from datetime import datetime
from src.models.sale_record import SaleRecord

class SalesDataset():
  def __init__(self, records=None):
    self._records = list(records) if records else []

  def add(self, record):
    self._records.append(record)

  def __len__(self):
    return len(self._records)

  def __iter__(self):
    return iter(self._records)

  def __contains__(self, item):
    return item in self._records

  def filter_by_category(self, category):
    if not isinstance(category, str):
      raise ValueError("Kategoria musi byc tekstem")
    
    if not category.strip():
      raise ValueError("Kategoria nie moze byc pusta")

    return SalesDataset([
      record for record in self._records
      if record.product.category.lower() == category.lower()
    ])

  def filter_by_seller(self, seller):
    if not isinstance(seller, str):
      raise ValueError("Sprzedawca musi byc tekstem")
    
    if not seller.strip():
      raise ValueError("Sprzedawca nie moze byc pusty")
    
    return SalesDataset([
      record for record in self._records
      if record.seller.lower() == seller.lower()
    ])

  def filter_by_region(self, region):
    if not isinstance(region, str):
      raise ValueError("Region musi byc tekstem")
    
    if not region.strip():
      raise ValueError("Region nie moze byc pusty")
    
    if not region.upper() in SaleRecord.VALID_REGIONS:
      raise ValueError("Niepoprawny kod regionu")

    return SalesDataset([
      record for record in self._records
      if record.region.lower() == region.lower()
    ])

  def filter_by_date_range(self, start, end):
    if not isinstance(start, datetime.date):
      raise ValueError("Poczatkowa data musi byc typu date")
    
    if not isinstance(end, datetime.date):
      raise ValueError("Koncowa data musi byc typu date")
    
    if start > end:
      raise ValueError("Poczatkowa data nie moze byc pozniejsza od koncowej")
    
    return SalesDataset([
      record for record in self._records
      if start <= record.date <= end
    ])

  def categories(self):
    return {record.product.category for record in self._records}

  def sellers(self):
    return {record.seller for record in self._records}

  def regions(self):
    return {record.region for record in self._records}