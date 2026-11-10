# SmartBox – Intelligent Shipping Box Selection System

[![SmartBox CI](https://github.com/example/smartbox/actions/workflows/tests.yml/badge.svg)](https://github.com/example/smartbox/actions/workflows/tests.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-5.2%20LTS-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **SmartBox** is a warehouse packaging recommendation and cartonization platform designed for ecommerce fulfillment. When a customer places an order, SmartBox evaluates available shipping boxes, executes a deterministic **3D Bin Packing Algorithm (Extreme Point Heuristic)** to ensure every product physically fits without collision, validates maximum payload weight constraints, and recommends the **lowest-cost suitable box** with transparent explanations and alternative options.

---

## Table of Contents
- [Executive Summary](#executive-summary)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Packing Algorithm Specification](#packing-algorithm-specification)
- [Tech Stack](#tech-stack)
- [Quickstart & Installation](#quickstart--installation)
- [Demo Seed Data & Default Logins](#demo-seed-data--default-logins)
- [Automated Testing](#automated-testing)
- [REST API Endpoints](#rest-api-endpoints)
- [Submission Deliverables](#submission-deliverables)

---

## Executive Summary

In high-volume ecommerce warehouses, manual box selection leads to:
1. **Oversized packaging:** Unnecessary packaging material expenses and excessive dimensional weight charges.
2. **Damaged goods / Fit failures:** Products forced into boxes that cannot physically accommodate them or exceed safe payload limits.
3. **Inconsistent fulfillment decisions:** Different warehouse workers picking different boxes for identical orders.

**Core Product Principle:** Recommend the cheapest packaging box capable of physically accommodating the entire order without violating dimensional or payload weight constraints.

---

## Key Features

- **3D Extreme Point Bin Packing:** Deterministic placement heuristic (Crainic et al.) testing all 6 axis-aligned 3D product orientations with complete collision detection.
- **Weight Capacity Validation:** Calculates $W_{total} = \sum (W_i \times Q_i)$ and rejects boxes exceeding maximum payload capacity.
- **Cheapest Eligible Box Selection:** Deterministically ranks eligible boxes by lowest packaging material cost, then smallest internal volume, and stable code ordering.
- **Alternative Box Comparison:** Displays all other eligible boxes in ascending cost order for operational flexibility.
- **Transparent Rejection Reasons:** Explains precisely why candidate boxes were rejected (e.g. weight limit exceeded, product exceeds dimensions in all rotations, packing heuristic boundary failure).
- **Immutable Historical Snapshots:** Preserves exact order item dimensions, weights, and box parameters upon calculation so future master catalog changes never alter past fulfillment records.
- **Warehouse Operations Dashboard:** Real-time KPI cards, pending packaging order queue, packaging material expenditure analytics, and box usage distributions.
- **Full REST API:** Exposes endpoints for products, boxes, orders, and cartonization recommendations.

---

## System Architecture

The project adheres to strict separation of concerns, decoupling the core 3D packing algorithm from Django views and database models:

```
smartbox/
├── config/                  # Django project configuration & settings
├── accounts/                # User authentication & role profiles (Admin, Staff)
├── inventory/               # Product catalog & Shipping box specifications
├── orders/                  # Order management & immutable item snapshots
├── recommendations/         # Recommendation engine & 3D bin packing
│   ├── algorithms/          # Pure-Python geometry, orientation, collision & EP packing
│   ├── services/            # Weight calculator, box filter, packing & ranking services
│   ├── models.py            # Recommendations, BoxEvaluationResult, ProductPlacementRecord
│   └── tests/               # 37 pure-Python unit tests + integration test suite
├── dashboard/               # Warehouse KPI dashboard & packaging analytics
├── templates/               # Clean, responsive Bootstrap 5 warehouse interface
├── docs/                    # Architecture deep-dive (architecture.md)
├── .github/workflows/       # GitHub Actions CI workflow (tests.yml)
├── AI_USAGE.md              # Transparent AI tool usage documentation
├── LEARNING_REFLECTION.md   # Personal developer engineering retrospective
├── TEST_OUTPUT.md           # Verifiable test execution output (66 tests passed)
├── chat-transcript.md       # Genuine development conversation transcript
└── requirements.txt         # Pinned project dependencies
```

For detailed architectural diagrams and coordinate math, see [docs/architecture.md](docs/architecture.md).

---

## Packing Algorithm Specification

1. **Volume & Dimension Pre-Filter:** Rejects boxes if total product volume exceeds box internal volume or if any item cannot fit alone in any orientation.
2. **Axis-Aligned Orientations:** Generates up to 6 unique spatial rotations:
   $$(L, W, H), (L, H, W), (W, L, H), (W, H, L), (H, L, W), (H, W, L)$$
   Symmetrical dimensions (cubes and square cuboids) are automatically deduplicated.
3. **Gravity-Ordered Candidate Extreme Points:** Candidate points are prioritized by $(z \uparrow, y \uparrow, x \uparrow)$, ensuring items are placed on the bottom of the box first, against the back wall, packing left-to-right.
4. **Collision Detection (SAT):** Validates that no two products overlap in 3D space:
   $$A_x^{end} \le B_x \lor B_x^{end} \le A_x \lor A_y^{end} \le B_y \lor B_y^{end} \le A_y \lor A_z^{end} \le B_z \lor B_z^{end} \le A_z$$
   Touching faces ($A_x^{end} = B_x$) are allowed and represent valid adjacent placements.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11 / 3.12 |
| **Framework** | Django 5.2 LTS |
| **API** | Django REST Framework |
| **Database** | SQLite (development/tests) / PostgreSQL-compatible |
| **Frontend** | HTML5, Bootstrap 5, Bootstrap Icons, Vanilla JS |
| **Testing** | Django TestCase & Python unittest (66 automated tests) |
| **CI/CD** | GitHub Actions |

---

## Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/smartbox.git
cd smartbox
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations
```bash
python manage.py migrate
```

### 5. Seed Demo Warehouse Data
Populates standard shipping boxes, sample products, warehouse staff accounts, and test orders:
```bash
python manage.py seed_demo_data
```

### 6. Start Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## Demo Seed Data & Default Logins

The `seed_demo_data` command creates ready-to-use warehouse accounts:

| Username | Password | Role | Access Level |
|---|---|---|---|
| `admin` | `admin123` | Administrator | Full admin, inventory master data, analytics |
| `warehouse` | `warehouse123` | Warehouse Staff | Order management, box recommendations, packaging |

---

## Automated Testing

The project includes **66 comprehensive automated tests** covering every functional requirement and edge case specified in the PRD:

- **Packing Algorithm (AL-01 to AL-10):** Rotations, boundary limits, overlap prevention, touching contact, multi-quantity units, and full container rejection.
- **Recommendation Logic (RT-01 to RT-10):** Cost optimization, volume tie-breaking, code stability, weight limit rejection, and identical-request determinism.
- **Inventory Master Data (PT-01 to PT-06 & BT-01 to BT-06):** Positive dimensions, positive weights, non-negative costs, uniqueness constraints, and soft deactivation.
- **Order Management (OT-01 to OT-06):** Multi-item total weight calculation, quantity validation, cancelled order blocking, and immutable snapshot preservation.
- **Security & Dashboard (AUTH-01 to AUTH-05 & DASH-01 to DASH-06):** Session protection, profile instantiation, and persisted KPI metrics.

### Run All Tests:
```bash
python manage.py test --verbosity=2
```

All 66 tests pass with 0 errors and 0 failures. The unedited terminal test log is recorded in [TEST_OUTPUT.md](TEST_OUTPUT.md).

---

## REST API Endpoints

Base URL: `/api/v1/`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/products/` | List all products |
| `POST` | `/api/v1/products/` | Create a new product |
| `GET` | `/api/v1/boxes/` | List all shipping boxes |
| `POST` | `/api/v1/boxes/` | Create a new shipping box |
| `GET` | `/api/v1/orders/` | List all orders |
| `POST` | `/api/v1/orders/` | Create a new order |
| `POST` | `/api/v1/orders/{id}/recommend/` | Run 3D packing recommendation for order |
| `GET` | `/api/v1/orders/{id}/recommendations/` | List recommendation history for order |
| `GET` | `/api/v1/recommendations/{id}/` | Get full recommendation payload & placements |
| `POST` | `/api/v1/recommendations/{id}/confirm/` | Confirm selected box for order packaging |
| `POST` | `/api/v1/recommendations/{id}/complete/` | Mark order packaging as completed |

### Example Recommendation Response:
```json
{
  "id": 1,
  "order": 1,
  "selected_box_code": "BOX-M",
  "selected_box_name": "Medium Standard Box",
  "selected_cost": "25.00",
  "total_weight": "3.20",
  "algorithm_version": "extreme_point_v1",
  "has_suitable_box": true,
  "is_confirmed": false,
  "box_results": [
    {
      "box_code": "BOX-M",
      "cost": "25.00",
      "volume": "31500.0000",
      "is_eligible": true,
      "rank": 1,
      "weight_utilization_pct": 26.67,
      "volume_utilization_pct": 21.59,
      "placements": [
        {
          "item_sku": "LAPTOP-PRO-15",
          "unit_index": 1,
          "x": "0.00", "y": "0.00", "z": "0.00",
          "placed_length": "35.00", "placed_width": "25.00", "placed_height": "2.00"
        }
      ]
    }
  ]
}
```

---

## Submission Deliverables

1. **Source Code:** Full modular Django repository.
2. **README.md:** This setup, architecture, and feature guide.
3. **AI_USAGE.md:** Full disclosure of AI tools, prompts, accepted suggestions, rejected/modified outputs, and human decisions ([AI_USAGE.md](AI_USAGE.md)).
4. **TEST_OUTPUT.md:** Verifiable output from `python manage.py test --verbosity=2` ([TEST_OUTPUT.md](TEST_OUTPUT.md)).
5. **LEARNING_REFLECTION.md:** Personal retrospective written by the developer on 3D packing math, data drift, and architectural trade-offs ([LEARNING_REFLECTION.md](LEARNING_REFLECTION.md)).
6. **Chat Transcript:** Attached genuine export in [chat-transcript.md](chat-transcript.md) and [chat-transcript.jsonl](chat-transcript.jsonl).
7. **CI Pipeline:** Automated GitHub Actions test workflow in [.github/workflows/tests.yml](.github/workflows/tests.yml).
