# Universal Fuzzy Data Matcher

A fast, domain-agnostic, production-grade web application for matching sample/reference datasets against large master datasets using dynamic column mapping, customizable weights, RapidFuzz multi-strategy matching, and alternative candidate review.

---

## 🌟 Key Features

- **100% Domain-Agnostic**: Works with any tabular dataset (e.g. Customers & Orders, Products & SKUs, Mobile Specifications, Employee Directories, Geographic Addresses, Catalogs).
- **Multi-File Master Datasets**: Automatically concatenates multiple master CSV/Excel files into a single index with source file tracking.
- **Dynamic Column Mapping & Weights**: Map any number of sample columns to corresponding master columns with user-defined percentage weights (validated to 100%).
- **Advanced Matching Algorithms**: RapidFuzz C++ core supporting `token_sort_ratio`, `token_set_ratio`, `ratio`, exact matching, numeric tolerance, and date proximity.
- **High-Performance Candidate Generation**: Inverted indexing enables sub-second lookups even across 100,000+ master rows.
- **Interactive Review Center**: Inspect uncertain matches (`REVIEW` and `NO MATCH`) with top 3 alternative candidate records.
- **Multi-Format Export Hub**: Download filtered or full results in styled Excel (`.xlsx`) or UTF-8 CSV (`.csv`).

---

## 🚀 Installation & Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Packages: `streamlit`, `pandas`, `rapidfuzz`, `openpyxl`)*

### 2. Launch the Web Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

---

## 📖 How to Use

### Step 1: Upload Datasets
- **Sample Data**: Upload your reference file (`.csv`, `.xlsx`, `.xls`) containing the query records you wish to look up.
- **Master Data**: Upload one or multiple reference/master files. The application combines them automatically.

### Step 2: Configure Matching Rules
1. Click **➕ Add Rule** to create matching pairs.
2. Select the **Sample Column** from the dropdown.
3. Select one or more **Master Column(s)** to compare against (e.g. Category and Full Item Name).
4. Assign a **Weight %** (the sum across all rules must equal 100%).
5. Select a **Matching Mode** (`Automatic`, `Text Fuzzy`, `Exact`, `Numeric`, `Date`).

### Step 3: Select Return Columns & Thresholds
- Choose which columns from the master dataset should be appended to the final results (e.g., `sale_order_code`, `SKU`, `Employee_ID`).
- Adjust confidence thresholds in the sidebar (Default: High Confidence $\ge 90$, Review Required $75 - 89$, No Match $< 75$).

### Step 4: Run Matching & Review
- Click **🚀 Run Fuzzy Matching** to process the data.
- Explore the interactive KPI metrics, search/filter table, and alternative candidates in the Review section.

### Step 5: Export
- Download All Results, High Confidence only, Review Required, or No Match files in `.xlsx` or `.csv`.

---

## 💡 Example Domain Use Cases

| Domain | Sample Input | Master Target | Return Columns |
|---|---|---|---|
| **E-Commerce Orders** | `Customer Name`, `Product` | `Customer_Name`, `Product_`, `item_name` | `sale_order_code`, `Order_Date` |
| **Product / SKU** | `Product Description` | `Title`, `Item_Description` | `SKU_Code`, `Unit_Price` |
| **Mobile Specs** | `RAM`, `Storage`, `Chipset`, `Display` | `RAM_Spec`, `ROM`, `Processor`, `Screen` | `Model_Name`, `Brand` |
| **HR / Employee** | `Employee Name`, `Department` | `Full_Name`, `Dept_Code` | `Employee_ID`, `Email` |
| **Address Verification** | `Person Name`, `Street`, `City` | `Recipient`, `Address_Line_1`, `City_Name`| `Account_Number` |

---

## 📂 Project Architecture

```
├── app.py              # Streamlit web user interface
├── matcher.py          # Fuzzy matching engine & candidate generator
├── file_loader.py      # Universal CSV/Excel multi-file reader & combiner
├── utils.py            # Generic text normalizer, type detector, Excel export
├── match_orders.py     # Batch CLI matching script for automated runs
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```
