/* ==========================================================================
   Universal Match AI — MOCK DATA ONLY
   Replace every value here with Streamlit/Python injected JSON, e.g.:
     st.markdown(f"<script>window.UMA_DATA = {json.dumps(payload)}<\/script>")
   Nothing in this file is business logic — it only feeds the UI.
   ========================================================================== */
window.UMA_DATA = {
  // Placeholder tokens rendered into {{...}} slots in index.html
  tokens: {
    total_records: "12,540",
    matched_records: "10,982",
    review_records: "1,120",
    no_match_records: "438",
    match_rate: "87.6%",
    records_processed: "8,420 / 12,540",
    progress: "67%",
    rows_used: "312,400",
    rows_quota: "500,000",
    recent_jobs: "6 jobs",
    result_rows: "12,540 rows",
  },

  matchRate: 87.6,

  qualityChart: [
    { label: "90–100", value: 6820, tone: "success" },
    { label: "80–89", value: 2960, tone: "success" },
    { label: "70–79", value: 1120, tone: "warning" },
    { label: "60–69", value: 640, tone: "warning" },
    { label: "50–59", value: 320, tone: "danger" },
    { label: "< 50", value: 118, tone: "danger" },
  ],

  confChart: [
    { label: "50–59", value: 210, tone: "danger" },
    { label: "60–69", value: 430, tone: "warning" },
    { label: "70–79", value: 890, tone: "warning" },
    { label: "80–89", value: 2960, tone: "success" },
    { label: "90–94", value: 3510, tone: "success" },
    { label: "95–100", value: 3310, tone: "success" },
  ],

  files: {
    reference: [
      { name: "customer_orders_july.xlsx", size: "3.4 MB", rows: "12,540", cols: "9" },
    ],
    master: [
      { name: "master_products.csv", size: "1.1 MB", rows: "4,210", cols: "6" },
      { name: "master_customers.xlsx", size: "2.7 MB", rows: "8,904", cols: "11" },
    ],
  },

  referenceColumns: ["Customer Name", "Product", "City", "Order Ref", "Email"],
  masterColumns: ["Customer_Name", "Product_", "City_Name", "Order ID", "Email_Address", "Date"],

  rules: [
    { ref: "Customer Name", master: "Customer_Name", weight: 60 },
    { ref: "Product", master: "Product_", weight: 40 },
  ],

  returnColumns: [
    { name: "Order ID", on: true },
    { name: "Product", on: true },
    { name: "Customer", on: false },
    { name: "Date", on: false },
    { name: "Region", on: false },
    { name: "Unit Price", on: false },
  ],

  tasks: [
    { name: "Preparing data", note: "Normalising 12,540 reference rows" },
    { name: "Finding candidates", note: "Blocking on Customer_Name" },
    { name: "Calculating similarity", note: "RapidFuzz token_set_ratio" },
    { name: "Generating results", note: "Assembling return columns" },
  ],

  jobs: [
    { name: "July customer reconciliation", ref: "customer_orders_july.xlsx", rows: "12,540", rate: 87.6, status: "high", created: "2 hours ago" },
    { name: "Vendor master cleanup", ref: "vendors_q2.csv", rows: "4,102", rate: 92.4, status: "high", created: "Yesterday" },
    { name: "Product catalog merge", ref: "catalog_export.xlsx", rows: "18,908", rate: 74.1, status: "review", created: "2 days ago" },
    { name: "Retail store mapping", ref: "stores_apac.csv", rows: "912", rate: 96.8, status: "high", created: "3 days ago" },
    { name: "Legacy CRM import", ref: "crm_dump_2019.xlsx", rows: "31,455", rate: 61.2, status: "none", created: "5 days ago" },
    { name: "Supplier deduplication", ref: "suppliers_all.csv", rows: "7,204", rate: 83.9, status: "review", created: "1 week ago" },
  ],

  results: [
    {
      sample: "Acme Industreis Pvt Ltd",
      best: "Acme Industries Private Limited",
      id: "ORD-100241",
      confidence: 94,
      status: "high",
      original: { "Customer Name": "Acme Industreis Pvt Ltd", Product: "Steel Bolt M8 x 40mm" },
      matched: { Customer_Name: "Acme Industries Private Limited", Product_: "Steel Bolt M8 40 mm" },
      scores: [{ col: "Customer Name", score: 96 }, { col: "Product", score: 91 }],
      candidates: [
        { label: "Acme Industries Private Limited", score: 94 },
        { label: "Acme Industrial Products Ltd", score: 88 },
        { label: "Acme Inds. Pvt.", score: 81 },
      ],
    },
    {
      sample: "globex corp - mumbai",
      best: "Globex Corporation (Mumbai)",
      id: "ORD-100388",
      confidence: 97,
      status: "high",
      original: { "Customer Name": "globex corp - mumbai", Product: "Hydraulic Pump 2L" },
      matched: { Customer_Name: "Globex Corporation (Mumbai)", Product_: "Hydraulic Pump 2 L" },
      scores: [{ col: "Customer Name", score: 98 }, { col: "Product", score: 95 }],
      candidates: [
        { label: "Globex Corporation (Mumbai)", score: 97 },
        { label: "Globex Corp Pune", score: 84 },
        { label: "Globe X Corporation", score: 72 },
      ],
    },
    {
      sample: "Initech Solutons",
      best: "Initech Solutions LLP",
      id: "ORD-100455",
      confidence: 82,
      status: "review",
      original: { "Customer Name": "Initech Solutons", Product: "Copper Wire 4mm" },
      matched: { Customer_Name: "Initech Solutions LLP", Product_: "Copper Wire 4 mm coil" },
      scores: [{ col: "Customer Name", score: 88 }, { col: "Product", score: 73 }],
      candidates: [
        { label: "Initech Solutions LLP", score: 82 },
        { label: "Initech Software Solutions", score: 79 },
        { label: "Initek Solution", score: 68 },
      ],
    },
    {
      sample: "Umbrella Hlth. Supplies",
      best: "Umbrella Health Supplies Co",
      id: "ORD-100512",
      confidence: 78,
      status: "review",
      original: { "Customer Name": "Umbrella Hlth. Supplies", Product: "Nitrile Glove L" },
      matched: { Customer_Name: "Umbrella Health Supplies Co", Product_: "Nitrile Gloves Large" },
      scores: [{ col: "Customer Name", score: 84 }, { col: "Product", score: 69 }],
      candidates: [
        { label: "Umbrella Health Supplies Co", score: 78 },
        { label: "Umbrella Healthcare Ltd", score: 74 },
        { label: "Umbra Health Supply", score: 61 },
      ],
    },
    {
      sample: "Zz Trading 998",
      best: "—",
      id: "—",
      confidence: 41,
      status: "none",
      original: { "Customer Name": "Zz Trading 998", Product: "Unknown SKU 998" },
      matched: { Customer_Name: "—", Product_: "—" },
      scores: [{ col: "Customer Name", score: 44 }, { col: "Product", score: 36 }],
      candidates: [
        { label: "ZZ Traders", score: 41 },
        { label: "Z Trading Co", score: 38 },
        { label: "Zed Trading 99", score: 33 },
      ],
    },
    {
      sample: "Soylent Foods  Pvt.",
      best: "Soylent Foods Pvt Ltd",
      id: "ORD-100603",
      confidence: 99,
      status: "high",
      original: { "Customer Name": "Soylent Foods  Pvt.", Product: "Protein Bar 40g" },
      matched: { Customer_Name: "Soylent Foods Pvt Ltd", Product_: "Protein Bar 40 g" },
      scores: [{ col: "Customer Name", score: 99 }, { col: "Product", score: 98 }],
      candidates: [
        { label: "Soylent Foods Pvt Ltd", score: 99 },
        { label: "Soylent Food Products", score: 86 },
        { label: "Soy Lent Foods", score: 70 },
      ],
    },
  ],
};
