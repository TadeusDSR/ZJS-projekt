import os
import json
from datetime import datetime
from src.io.file_processor import FileProcessor, SdfParseError
from src.analysis.statistics import SalesStatistics
from src.io.excel_exporter import ExcelExporter
from src.db.database import SalesDatabase, DatabaseError


class ConsoleApp:

	def __init__(self, reports_dir):
		self.processor = FileProcessor()
		self.dataset = None
		self.errors = []
		self.metadata = {}
		self.reports_dir = reports_dir
		self.database = SalesDatabase()

	def run(self):
		while True:
			self.print_header()

			print("1. Wczytaj plik SDF")
			print("2. Statystyki ogólne")
			print("3. Filtruj i przeglądaj")
			print("4. Raport TXT")
			print("5. Eksport JSON")
			print("6. Informacje o zbiorze")
			print("7. Eksport Excel")
			print("8. Baza danych")
			print("0. Wyjście")

			choice = input(">> ")

			try:
				if choice == "1":
					self.load()
				elif choice == "2":
					self.show_stats()
				elif choice == "3":
					self.filter_menu()
				elif choice == "4":
					self.export_txt()
				elif choice == "5":
					self.export_json()
				elif choice == "6":
					self.info()
				elif choice == "7":
					self.export_excel()
				elif choice == "8":
					self.database_menu()
				elif choice == "0":
					break
			except Exception as e:
				print("Błąd:", e)

	def print_header(self):
			if self.metadata:
				print(f"{self.metadata.get('owner')} | {self.metadata.get('index')}")
			if self.dataset:
				print(f"Rekordy: {len(self.dataset)}")

	def load(self):
		path = input("Ścieżka: ")
		try:
			self.dataset, self.errors, self.metadata = self.processor.parse_sdf(path)

			print(f"Wczytano: {len(self.dataset)}")
			print(f"Odrzucono: {len(self.errors)}")
			print(f"Produkty: {len(self.dataset.categories())}")

			if self.errors:
				for e in self.errors[:10]:
					print(e)
				if len(self.errors) > 10:
					print(f"... +{len(self.errors)-10} więcej")

		except FileNotFoundError:
			print("Błąd: plik nie istnieje")

		except PermissionError:
			print("Błąd: brak uprawnień do pliku")

		except SdfParseError as e:
				print("BŁĄD KRYTYCZNY:", e)

	def show_stats(self, dataset=None):
		dataset = dataset or self.dataset
		if not dataset:
			print("Brak danych")
			return

		stats = SalesStatistics(dataset)
		
		total = stats.total_revenue()
		avg = stats.average_transaction()

		print(f"Przychód: {total:,.2f} PLN".replace(",", " "))
		print(f"Średnia: {avg:,.2f} PLN".replace(",", " "))
		print(f"Liczba transakcji: {len(dataset)}")

		best = stats.best_seller()
		if best:
			print(f"Najlepszy sprzedawca: {best[0]} ({best[1]:,.2f} PLN)".replace(",", " "))

		month = stats.best_month()
		if month:
			print(f"Najlepszy miesiąc: {month[0]} ({month[1]:,.2f} PLN)".replace(",", " "))

		print("\nPrzychód wg kategorii:")
		cat = stats.by_category()
		for key, value in cat.items():
			pct = value / total * 100
			print(f"{key}: {value:,.2f} PLN ({pct:,.1f}%)".replace(",", " "))

		print("\nPrzychód wg regionów:")
		reg = stats.by_region()
		for key, value in reg.items():
			pct = value / total * 100
			print(f"{key}: {value:,.2f} PLN ({pct:,.1f}%)".replace(",", " "))

		print("\nTop produkty:")
		for product, value in stats.top_products():
			print(f"{product}: {value:,.2f} PLN".replace(",", " "))

	def filter_menu(self):
		if not self.dataset:
			print("Brak danych")
			return

		print("1. Kategoria")
		print("2. Sprzedawca")
		print("3. Region")
		print("4. Zakres dat")

		choice = input(">> ")

		if choice == "1":
			val = input("Kategoria: ")
			ds = self.dataset.filter_by_category(val)
		elif choice == "2":
			val = input("Sprzedawca: ")
			ds = self.dataset.filter_by_seller(val)
		elif choice == "3":
			val = input("Region: ")
			ds = self.dataset.filter_by_region(val)
		elif choice == "4":
			d1 = datetime.strptime(input("Od: "), "%d.%m.%Y").date()
			d2 = datetime.strptime(input("Do: "), "%d.%m.%Y").date()
			ds = self.dataset.filter_by_date_range(d1, d2)
		else:
			print("Niepoprawna opcja")
			return

		print(f"Wynik: {len(ds)}")
		self.show_stats(ds)

	def export_txt(self):
		if not self.dataset:
			print("Brak danych")
			return

		stats = SalesStatistics(self.dataset)

		now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
		index = self.metadata.get("index", "unknown")

		filename = f"{index}_raport_{now}.txt"
		path = os.path.join(self.reports_dir, filename)

		os.makedirs(self.reports_dir, exist_ok=True)

		total = stats.total_revenue()
		avg = stats.average_transaction()

		lines = []

		lines.append("DATASET")
		for key, value in self.metadata.items():
			lines.append(f"{key}: {value}")

		lines.append("\nSTATYSTYKI")
		lines.append(f"Łączny przychód: {total:,.2f} PLN".replace(",", " "))
		lines.append(f"Średnia transakcja: {avg:,.2f} PLN".replace(",", " "))
		lines.append(f"Liczba transakcji: {len(self.dataset)}")

		lines.append("\nMIESIĘCZNIE")
		for key, value in stats.monthly_summary().items():
			lines.append(f"{key}: {value:,.2f} PLN".replace(",", " "))

		lines.append("\nSPRZEDAWCY")
		for key, value in stats.by_seller().items():
			lines.append(f"{key}: {value:,.2f} PLN".replace(",", " "))

		lines.append("\nREGIONY")
		for key, value in stats.by_region().items():
			lines.append(f"{key}: {value:,.2f} PLN".replace(",", " "))

		with open(path, "w", encoding="utf-8") as f:
			f.write("\n".join(lines))

		print("Raport zapisany:", path)

	def export_json(self):
		if not self.dataset:
			print("Brak danych")
			return

		stats = SalesStatistics(self.dataset)

		data = {
			"metadata": self.metadata,
			"statistics": {
				"total": stats.total_revenue(),
				"average": stats.average_transaction(),
				"by_category": stats.by_category(),
				"by_region": stats.by_region(),
				"by_seller": stats.by_seller(),
				"monthly": stats.monthly_summary()
			},
			"records": [record.to_dict() for record in self.dataset]
		}

		now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
		index = self.metadata.get("index", "unknown")

		filename = f"{index}_export_{now}.json"
		path = os.path.join(self.reports_dir, filename)

		os.makedirs(self.reports_dir, exist_ok=True)

		with open(path, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=2, ensure_ascii=False)

		print("Zapisano:", path)

	def info(self):
		if not self.dataset:
			print("Brak danych")
			return

		dates = [record.date for record in self.dataset]
		print("Liczba rekordów:", len(self.dataset))
		print("Liczba produktów:", len(self.dataset.categories()))
		print("Zakres dat:", min(dates), "-", max(dates))
		print("Kategorie:", self.dataset.categories())
		print("Sprzedawcy:", self.dataset.sellers())
		print("Regiony:", self.dataset.regions())

	def export_excel(self):
		if not self.dataset:
			print("Brak danych")
			return

		try:
			exporter = ExcelExporter()

			now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
			index = self.metadata.get("index", "unknown")

			filename = f"{index}_excel_{now}.xlsx"
			path = os.path.join(self.reports_dir, filename)

			os.makedirs(self.reports_dir, exist_ok=True)

			stats = SalesStatistics(self.dataset)

			exporter.export(self.dataset, stats, path)

			print("Zapisano Excel:", path)

		except Exception as e:
			print("Błąd eksportu Excel:", e)

	def database_menu(self):
		while True:
			if self.database.is_connected():
				print("[połączono]")

			print("a) Połącz z bazą")
			print("b) Utwórz schemat")
			print("c) Importuj dane")
			print("d) Zapytania analityczne")
			print("e) Usuń schemat")
			print("0) Powrót")

			choice = input(">> ")

			try:
				if choice == "a":
					self.connect_db()

				elif choice == "b":
					if not self.database.is_connected():
						print("Brak połączenia")
						continue
					self.database.create_schema()
					print("OK: schema utworzona")

				elif choice == "c":
					if not self.database.is_connected():
						print("Brak połączenia")
						continue
					count = self.database.import_dataset(self.dataset)
					print(f"Zaimportowano: {count}")

				elif choice == "d":
					if not self.database.is_connected():
						print("Brak połączenia")
						continue
					self.db_queries_menu()

				elif choice == "e":
					if not self.database.is_connected():
						print("Brak połączenia")
						continue

					confirm = input("Wpisz 'tak' aby usunąć: ")
					if confirm.lower() == "tak":
						self.database.drop_schema()
						print("Usunięto schemat")

				elif choice == "0":
					break

			except DatabaseError as e:
				print("DB ERROR:", e)

	def connect_db(self):
		host = input("host: ")
		port = input("port: ")
		dbname = input("dbname: ")
		user = input("user: ")
		password = input("password: ")

		self.database.connect(host, port, dbname, user, password)

		print(f"Połączono z {host}/{dbname}")

	def db_queries_menu(self):
		while True:
			print("1. Przychód wg kategorii")
			print("2. Top 5 sprzedawców")
			print("3. Podsumowanie miesięczne")
			print("4. Liczba transakcji")
			print("0. Powrót")

			choice = input(">> ")

			try:
				if choice == "1":
					self.print_money_table(self.database.get_revenue_by_category())

				elif choice == "2":
					self.print_money_table(self.database.get_top_sellers(5))

				elif choice == "3":
					self.print_money_table(self.database.get_monthly_summary())

				elif choice == "4":
					print("Transakcje:", self.database.get_transaction_count())

				elif choice == "0":
					break

			except DatabaseError as e:
				print("DATABASSE ERROR:", e)

	def print_money_table(self, data):
		for k, v in data:
			print(f"{k}: {v:,.2f} PLN".replace(",", " "))