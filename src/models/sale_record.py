import datetime

class SaleRecord:
	VALID_REGIONS = {"WA","KR","GD","PO","WR","LO","RZ","BY","ZG","OP"}
	
	def __init__(self, product, quantity, date, seller, region):
		# if not isinstance(quantity, int):
		# 	raise ValueError("Ilosc musi byc liczba")

		if not seller.strip():
			raise ValueError("Sprzedawca nie moze byc pusty")
	
		if not region in self.VALID_REGIONS:
			raise ValueError("Niepoprawny kod regionu")

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
		try:
			value = int(value)
		except ValueError:
			raise ValueError("Ilosc musi byc liczba")

		if value < 1:
			raise ValueError("Ilość musi byc > 0")
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
		return self.quantity * self._product.price

	def to_dict(self):
		return {
			"date": self._date.isoformat(),
			"product_id": self._product.product_id,
			"name": self._product.name,
			"category": self._product.category,
			"quantity": self.quantity,
			"price": self._product.price,
			"total": self.total_value(),
			"seller": self._seller,
			"region": self._region
		}

	def __str__(self):
		return f"{self._date} {self._product.name} {self.quantity} {self.total_value():.2f} PLN {self._seller} {self._region}"