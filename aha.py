from src.models.product import Product
from src.io.file_processor import FileProcessor

myProduct = Product("0000", "aaa", "dwada", 1.0)

newFP = FileProcessor()
newFP.parse_sdf("data/309459.sdf")

print(newFP.parse_sdf("data/309459.sdf")[0].regions())