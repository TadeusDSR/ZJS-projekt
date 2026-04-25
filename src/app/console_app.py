import os
from datetime import datetime
from src.io.file_processor import FileProcessor, SdfParseError
from src.analysis.statistics import SalesStatistics


class ConsoleApp:

    def __init__(self, reports_dir):
        self.processor = FileProcessor()
        self.dataset = None
        self.errors = []
        self.metadata = {}
        self.reports_dir = reports_dir

    def run(self):
        while True:
            self.print_header()

            print("1. Wczytaj plik SDF")
            print("2. Statystyki ogólne")
            print("3. Filtruj i przeglądaj")
            print("4. Raport TXT")
            print("5. Eksport JSON")
            print("6. Informacje o zbiorze")
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
                elif choice == "0":
                    break
            except Exception as e:
                print("Błąd:", e)

    def print_header(self):
        print("\n=== SYSTEM SPRZEDAŻY ===")
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

            if self.errors:
                for e in self.errors[:10]:
                    print(e)
                if len(self.errors) > 10:
                    print(f"... +{len(self.errors)-10} więcej")

        except SdfParseError as e:
            print("BŁĄD KRYTYCZNY:", e)

    def show_stats(self, dataset=None):
        dataset = dataset or self.dataset
        if not dataset:
            print("Brak danych")
            return

        stats = SalesStatistics(dataset)

        total = stats.total_revenue()
        print("Przychód:", total)
        print("Średnia:", stats.average_transaction())

        print("\nTop produkty:")
        for p, v in stats.top_products():
            print(p, v)

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
            return

        print(f"Wynik: {len(ds)}")
        self.show_stats(ds)

    def export_txt(self):
        if not self.dataset:
            print("Brak danych")
            return

        stats = SalesStatistics(self.dataset)

        filename = f"{self.metadata['index']}_raport_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
        path = os.path.join(self.reports_dir, filename)

        content = f"Raport\nPrzychód: {stats.total_revenue()}\n"

        self.processor.save_txt(path, content)
        print("Zapisano:", path)

    def export_json(self):
        if not self.dataset:
            print("Brak danych")
            return

        stats = SalesStatistics(self.dataset)

        data = {
            "metadata": self.metadata,
            "total": stats.total_revenue(),
            "records": [r.to_dict() for r in self.dataset]
        }

        filename = f"{self.metadata['index']}_export_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
        path = os.path.join(self.reports_dir, filename)

        self.processor.save_json(path, data)
        print("Zapisano:", path)

    def info(self):
        if not self.dataset:
            print("Brak danych")
            return

        print("Kategorie:", self.dataset.categories())
        print("Sprzedawcy:", self.dataset.sellers())
        print("Regiony:", self.dataset.regions())