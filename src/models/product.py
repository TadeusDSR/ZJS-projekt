class Product:
	def __init__(self, product_id, name, category, price):
		if not isinstance(product_id, str):
			raise ValueError("Product_id musi byc tekstem")

		if not (4 <= len(product_id) <= 10):
			raise ValueError("Niepoprawna dlugosc product_id")
		
		if " " in product_id:
			raise ValueError("Product_id nie moze zawierac spacji")
		
		if not name.strip():
			raise ValueError("Nazwa produktu nie moze byc pusta")
		
		if not category.strip():
			raise ValueError("Kategoria nie moze byc pusta")
		
		# if not isinstance(price, (int, float)):
		# 	raise ValueError("Cena musi byc liczba")

		self._product_id = product_id
		self._name = name
		self._category = category
		self.price = float(price)

	@property
	def product_id(self):
		return self._product_id
	
	@property
	def name(self):
		return self._name
	
	@property
	def category(self):
		return self._category

	@property
	def price(self):
		return self._price

	@price.setter
	def price(self, value):
		if value <= 0:
			raise ValueError(f"Niepoprawna cena: {value}")
		self._price = value

	def apply_discount(self, percent):
		if not (0 <= percent <= 100):
				raise ValueError("Rabat musi byc 0 - 100")
		return self.price * (1 - percent / 100)

	def __eq__(self, other):
		return isinstance(other, Product) and self.product_id == other.product_id

	def __str__(self):
		return f"[{self.product_id}] {self.name} ({self.category}) - {self.price:.2f} PLN"