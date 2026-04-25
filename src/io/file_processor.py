import json
from datetime import datetime
from src.models.product import Product
from src.models.sale_record import SaleRecord
from src.models.sales_dataset import SalesDataset


class SdfParseError(Exception):
    pass


class FileProcessor:

    VALID_REGIONS = {"WA","KR","GD","PO","WR","LO","RZ","BY","ZG","OP"}

    def parse_sdf(self, path):
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        dataset = SalesDataset()
        products = {}
        errors = []

        section = None
        metadata = {}

        for i, raw in enumerate(lines, start=1):
            line = raw.strip()

            if not line or line == "---":
                continue

            # sekcje
            if line.startswith("#"):
                if line == "#DATASET":
                    section = "DATASET"
                elif line == "#PRODUCTS":
                    section = "PRODUCTS"
                elif line == "#TRANSACTIONS":
                    section = "TRANSACTIONS"
                continue

            try:
                # DATASET
                if section == "DATASET":
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip()

                # PRODUCTS
                elif section == "PRODUCTS":
                    pid, name, cat, price = line.split("|")
                    products[pid] = Product(pid, name, cat, float(price))

                # TRANSACTIONS
                elif section == "TRANSACTIONS":
                    d, pid, qty, seller, region = line.split("|")

                    if pid not in products:
                        raise ValueError("Nieznany produkt")

                    if region not in self.VALID_REGIONS:
                        raise ValueError("Nieprawidłowy region")

                    date_obj = datetime.strptime(d, "%d.%m.%Y").date()

                    dataset.add(SaleRecord(
                        products[pid],
                        int(qty),
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