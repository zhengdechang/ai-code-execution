curl -X POST http://127.0.0.1:5000/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "import numpy as np\n\ndata = [1, 2, 3, 4, 5]\nmean = np.mean(data)\nvariance = np.var(data)\nstd_dev = np.std(data)\n\nprint(f\"Mean: {mean}\")\nprint(f\"Variance: {variance}\")\nprint(f\"Standard Deviation: {std_dev}\")",
  "required_packages": [
    "numpy"
  ]
}'
