import json
from datetime import datetime
from src.models.product import Product
from src.models.sale_record import SaleRecord
from src.models.sales_dataset import SalesDataset


class SdfParseError(Exception):
	pass


class FileProcessor:
	def parse_sdf(self, path):
		try:
			with open(path, encoding="utf-8") as f:
				lines = f.readlines()
		except FileNotFoundError:
			raise SdfParseError(f"Plik nie istnieje: {path}")
		except PermissionError:
			raise SdfParseError(f"Brak dostępu do pliku: {path}")

		dataset = SalesDataset()
		products = {}
		errors = []

		section = None
		metadata = {}

		expected_order = ["DATASET", "PRODUCTS", "TRANSACTIONS"]
		current_index = 0

		for i, raw in enumerate(lines, start=1):
			line = raw.strip()

			if not line or line == "---":
				continue

			if line.startswith("#"):
				if current_index >= len(expected_order):
					raise SdfParseError("Za dużo sekcji w pliku")
				section_name = line[1:]

				if section_name != expected_order[current_index]:
					raise SdfParseError(f"Błędna kolejność sekcji. Oczekiwano #{expected_order[current_index]}, otrzymano #{section_name}")

				current_index += 1
				section = section_name
				continue
			
			try:
				if section is None:
					raise SdfParseError("Brak sekcji")
				elif section == "DATASET":
					if ":" in line:
						k, v = line.split(":", 1)
						metadata[k.strip()] = v.strip()

				elif section == "PRODUCTS":
					pid, name, cat, price = line.split("|")
					products[pid] = Product(pid, name, cat, float(price))

				elif section == "TRANSACTIONS":
					date, pid, quantity, seller, region = line.split("|")

					if pid not in products:
						raise ValueError("Nieznany produkt")

					date_obj = datetime.strptime(date, "%d.%m.%Y").date()

					dataset.add(SaleRecord(
						products[pid],
						int(quantity),
						date_obj,
						seller,
						region
				))

			except Exception as e:
				errors.append(f"Linia {i}: {str(e)}")

		return dataset, errors, metadata

	def save_txt(self, path, content):
			with open(path, "w", encoding="utf-8") as f:
					f.write(content)

	def save_json(self, path, data):
			with open(path, "w", encoding="utf-8") as f:
					json.dump(data, f, indent=2, ensure_ascii=False)