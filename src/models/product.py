class Product:
	def __init__(self, product_id, name, category, price):
		self.product_id = product_id
		self.name = name
		self.category = category
		self.price = price

	@property
	def price(self):
		return self._price

	@price.setter
	def price(self, value):
		if value <= 0:
			raise ValueError(f"Nieprawidłowa cena: {value}")
		self._price = value

	def apply_discount(self, percent):
		if not (0 <= percent <= 100):
				raise ValueError("Nieprawidłowy rabat")
		return self.price * (1 - percent / 100)

	def __eq__(self, other):
		return isinstance(other, Product) and self.product_id == other.product_id

	def __str__(self):
		return f"[{self.product_id}] {self.name} ({self.category}) - {self.price:.2f} PLN"