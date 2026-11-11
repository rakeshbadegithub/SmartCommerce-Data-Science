
from pathlib import Path

folders = [
    "data/raw",
    "data/processed",
    "notebooks",
    "src/data_processing",
    "src/features",
    "src/models",
    "src/evaluation",
    "dashboard",
    "api",
    "models",
    "reports/figures"
]

files = [
    "notebooks/01_data_understanding.ipynb",
    "notebooks/02_data_cleaning.ipynb",
    "notebooks/03_eda.ipynb",
    "notebooks/04_customer_analysis.ipynb",
    "notebooks/05_machine_learning.ipynb",
    "dashboard/app.py",
    "api/main.py",
    "requirements.txt",
    "README.md"
]

# Create folders
for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)

# Create files
for file in files:
    Path(file).touch(exist_ok=True)

print("SmartCommerce project structure created successfully!")

