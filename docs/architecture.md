# SmartBox Architecture & Engineering Design

## 1. System Overview

SmartBox is a modular, high-reliability warehouse packaging and cartonization decision engine built with Python 3.11+ and Django 5.2. It analyzes multi-product customer orders, filters candidate shipping boxes by physical dimensions and weight capacity, and executes a deterministic **3D Bin Packing Algorithm (Extreme Point Heuristic)** to recommend the lowest-cost suitable box capable of packing all products.

```
                  ┌────────────────────────────────────────┐
                  │          Warehouse User / API          │
                  └───────────────────┬────────────────────┘
                                      │
                         HTTP / REST API Requests
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │             Django Web UI              │
                  │   (Accounts, Inventory, Orders, Recs)  │
                  └───────────────────┬────────────────────┘
                                      │
                         DTOs / Snapshot Payload
                                      │
                                      ▼
    ┌────────────────────────────────────────────────────────────────────┐
    │              Recommendation Service Layer (Pure Python)            │
    │  ┌───────────────────────┐              ┌───────────────────────┐  │
    │  │   Weight Calculator   │              │      Box Filter       │  │
    │  └───────────┬───────────┘              └───────────┬───────────┘  │
    │              │                                      │              │
    │              ▼                                      ▼              │
    │  ┌──────────────────────────────────────────────────────────────┐  │
    │  │                        Packing Service                       │  │
    │  └──────────────────────────────┬───────────────────────────────┘  │
    │                                 │                                  │
    │                                 ▼                                  │
    │  ┌──────────────────────────────────────────────────────────────┐  │
    │  │                   3D Extreme Point Engine                    │  │
    │  │    • Orientation Permutations (up to 6 unique rotations)     │  │
    │  │    • Separating Axis Collision Detection                     │  │
    │  │    • Candidate Point Projection (Crainic et al. EP Heuristic)│  │
    │  └──────────────────────────────┬───────────────────────────────┘  │
    │                                 │                                  │
    │                                 ▼                                  │
    │  ┌──────────────────────────────────────────────────────────────┐  │
    │  │                        Ranking Service                       │  │
    │  │            Key: (Lowest Cost, Lowest Volume, Code)           │  │
    │  └──────────────────────────────────────────────────────────────┘  │
    └─────────────────────────────────┬──────────────────────────────────┘
                                      │
                      Persist Immutable Snapshots & Rec
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │          Relational Storage            │
                  │        (SQLite / PostgreSQL)           │
                  └────────────────────────────────────────┘
```

---

## 2. Decoupled Service Architecture

A core architectural principle of SmartBox is the **complete decoupling of the recommendation engine and 3D bin packing calculations from Django database models and HTTP views**.

### Benefits:
1. **Zero Database Lockup:** Bin packing calculations execute entirely in-memory using pure Python dataclasses (`Dimensions`, `Point3D`, `ItemToPack`, `Placement`).
2. **Deterministic Reproducibility:** Given identical inputs and algorithm version, results are 100% reproducible across different environments.
3. **High Testability:** Fast unit test execution (37 algorithm tests execute in < 0.01 seconds without spinning up test databases).
4. **Reusability:** The packing algorithms can be imported into CLI tools, asynchronous workers (Celery), or microservices without modifying code.

---

## 3. 3D Extreme Point (EP) Bin Packing Algorithm

The 3D bin packing problem is strongly NP-hard. SmartBox utilizes a deterministic Extreme Point (EP) constructive heuristic based on Crainic, Perboli, and Pezzella (2008).

### Step 1: Pre-filtering & Sorting
- Fast volume check: $\sum V_{product} \le V_{box}$. If false, reject immediately.
- Dimensional check: verify each product can fit alone inside the box in at least one orientation.
- Product sort order: descending by $(V_{product}, \text{longest side}, \text{weight}, \text{sku})$.

### Step 2: Axis-Aligned Orientations
A rectangular cuboid with dimensions $(L, W, H)$ possesses up to 6 axis-aligned 3D orientations:
1. $(L, W, H)$
2. $(L, H, W)$
3. $(W, L, H)$
4. $(W, H, L)$
5. $(H, L, W)$
6. $(H, W, L)$
Duplicate orientations are deduplicated (e.g. cubes have 1 unique orientation; square cuboids have 3).

### Step 3: Candidate Extreme Point Generation & Sorting
- Initial candidate point: $(0, 0, 0)$ (box origin).
- Candidate points are prioritized using $(z \uparrow, y \uparrow, x \uparrow)$, ensuring physical packing starts on the floor/bottom of the box, against the back wall, filling left-to-right.
- When an item is placed at $(p_x, p_y, p_z)$ with oriented dimensions $(l, w, h)$, new extreme points are projected:
  - $(p_x + l, p_y, p_z)$
  - $(p_x, p_y + w, p_z)$
  - $(p_x, p_y, p_z + h)$
  - Additional projection points along axes aligned with existing item faces and container boundaries.
- Candidate points located strictly inside existing placed items are eliminated.

### Step 4: Collision Detection (Separating Axis Theorem)
For any candidate placement $[x_A, x_A + l_A] \times [y_A, y_A + w_A] \times [z_A, z_A + h_A]$ against existing placement $B$:
The items are non-overlapping if and only if at least one axis is separated:
$$x_A^{end} \le x_B \quad\lor\quad x_B^{end} \le x_A \quad\lor\quad y_A^{end} \le y_B \quad\lor\quad y_B^{end} \le y_A \quad\lor\quad z_A^{end} \le z_B \quad\lor\quad z_B^{end} \le z_A$$
Touching faces ($x_A^{end} == x_B$) are separated and represent valid adjacent contact.

---

## 4. Immutable Historical Snapshot Integrity

In warehouse operations, master data changes frequently (e.g., box suppliers change prices, or product packaging is redesigned). If an order or recommendation referenced live product dimensions, auditing an order from 3 months ago would yield altered results.

SmartBox resolves this through **immutable point-in-time snapshots**:
- `OrderItem` captures `product_sku_snapshot`, `product_name_snapshot`, `length_snapshot`, `width_snapshot`, `height_snapshot`, `weight_snapshot` upon item creation.
- `Recommendation` persists `input_snapshot` (all order item dimensions and boxes evaluated) and `result_payload`.
- `BoxEvaluationResult` and `ProductPlacementRecord` store exact 3D coordinates $(x, y, z)$ and dimensions at the moment the recommendation was calculated.
- Master data modifications or soft-deactivations do not alter historical records.

---

## 5. Ranking and Recommendation Criteria

When multiple boxes satisfy both weight limits and 3D packing validation:
1. **Primary Criterion:** Lowest packaging material cost ($\$ cost$).
2. **Secondary Criterion:** Lowest internal volume ($cm^3$).
3. **Tertiary Criterion:** Stable alphabetical box code ordering.

The first box becomes the primary recommendation, while remaining eligible boxes are displayed as sorted alternative options.
