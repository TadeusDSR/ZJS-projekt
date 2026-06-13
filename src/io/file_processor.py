import re
import datetime
from src.models.product import Product
from src.models.sale_record import SaleRecord
from src.models.sales_dataset import SalesDataset

RE_SEPERATOR = re.compile(r'^---$')
RE_HEADER_FIELD = re.compile(r'(?P<key>.+):(?P<value>.+)')
RE_DATE = re.compile(r'(?P<day>.+)\.(?P<month>.+)\.(?P<year>.+)')
RE_PRODUCT_LINE = re.compile(r'(?P<id>.+)\|(?P<name>.+)\|(?P<category>.+)\|(?P<price>.+)')
RE_TRANSACTION_LINE = re.compile(r"""
	(?P<date>.+)
	\|
	(?P<pid>.+)	
	\|
	(?P<quantity>.+)
	\|
	(?P<seller>.+)
	\|
	(?P<region>.+)
	""", re.VERBOSE)

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

		metadata = {}

		expected_order = ["DATASET", "PRODUCTS", "TRANSACTIONS"]
		current_index = 0
		section = None

		for i, raw in enumerate(lines, start=1):
			line = raw.strip()

			if not line or RE_SEPERATOR.match(line):
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
				if section == "DATASET":
					try:
						match = RE_HEADER_FIELD.match(line)

						if not match:
							raise ValueError(f"Niepoprawny format pola")
						
						metadata[match.group("key")] = match.group("value")

					except ValueError as e:
						errors.append(f"Linia {i} (DATASET): {e}")

				elif section == "PRODUCTS":
					try:
						match = RE_PRODUCT_LINE.match(line)
						
						if not match:
							raise ValueError("Niepoprawna ilosc pol")
						
						products[match.group("id")] = Product(
							match.group("id"),
							match.group("name"),
							match.group("category"),
							match.group("price")
							)
					
					except ValueError as e:
						errors.append(f"Linia {i} (PRODUCTS): {e}")

				elif section == "TRANSACTIONS":
					try:
						match = RE_TRANSACTION_LINE.match(line)

						if not match:
							raise ValueError(f"Niepoprawna ilosc pol")

						if match.group("pid") not in products:
							raise ValueError("Nieznany produkt")
						
						date = match.group("date")
						date_match = RE_DATE.match(date)

						if not date_match:
							raise ValueError("Niepoprawny format daty")

						day = int(date_match.group("day"))
						month = int(date_match.group("month"))
						year = int(date_match.group("year"))

						if not 1 <= day <= 31:
							raise ValueError("Niepoprawna data dnia")
						
						if not 1 <= month <= 12:
							raise ValueError("Niepoprawna data miesiaca")
						
						if not 1000 <= year <= 9999:
							raise ValueError("Niepoprawna data roku")
						
						date_obj = datetime.date(year, month, day)

						dataset.add(SaleRecord(
							products[match.group("pid")],
							match.group("quantity"),
							date_obj,
							match.group("seller"),
							match.group("region")
						))

					except ValueError as e:
						errors.append(f"Linia {i} (TRANSACTIONS): {e}")

			except Exception as e:
				errors.append(f"Linia {i}: {e}")

		return dataset, errors, metadata