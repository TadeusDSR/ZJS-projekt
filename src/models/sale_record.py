from datetime import datetime

class SaleRecord:
	def __init__(self, product, quantity, date, seller, region):
		VALID_REGIONS = {"WA","KR","GD","PO","WR","LO","RZ","BY","ZG","OP"}

		if not seller.strip():
			raise ValueError("Pusty sprzedawca")
	
		if not region in VALID_REGIONS:
			raise ValueError("Nieprawidowy region")

		self._product = product
		self.quantity = quantity
		self._date = date
		self._seller = seller
		self._region = region

	@property
	def product(self):
		return self._product

	@property
	def quantity(self):
		return self._quantity

	@quantity.setter
	def quantity(self, value):
		if value < 1:
			raise ValueError("Ilość >= 0")
		self._quantity = value

	@property
	def date(self):
		return self._date

	@property
	def seller(self):
		return self._seller

	@property
	def region(self):
		return self._region

	def total_value(self):
		return self.quantity * self.product.price

	def to_dict(self):
		return {
			"date": self.date.isoformat(),
			"product_id": self.product.product_id,
			"name": self.product.name,
			"category": self.product.category,
			"quantity": self.quantity,
			"price": self.product.price,
			"total": self.total_value(),
			"seller": self.seller,
			"region": self.region
		}

	def __str__(self):
		return f"{self.date} | {self.product.name} | {self.quantity} | {self.total_value():.2f} PLN | {self.seller} | {self.region}"