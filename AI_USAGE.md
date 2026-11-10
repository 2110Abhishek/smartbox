# AI Usage Documentation

This document transparently describes how AI assistance was utilized during the design and development of the **SmartBox Intelligent Packaging System**, detailing prompts, accepted suggestions, rejected/modified implementations, mistakes identified, and independent human verification.

---

## 1. AI Tools Used
- **Google Antigravity / Gemini 3.8 Flash (High)**: Used for architecture consultation, boilerplate generation, unit test scaffolding, and initial algorithm drafting.

---

## 2. Prompts Used
The primary prompt provided was the comprehensive SmartBox PRD v1.0 specification:
- *"Python/Django Hiring Assignment: AI-Assisted Box Selection System"* containing complete functional requirements for product management, box management, order management, 3D bin packing (extreme point heuristic), and acceptance criteria (AC-01 through AC-20).
- Follow-up internal implementation commands to scaffold Django apps, author geometry data structures, and debug test suite runs.

---

## 3. Output Accepted
1. **Modular Django Architecture**:
   - The separation of responsibilities into five discrete Django applications: `accounts`, `inventory`, `orders`, `recommendations`, and `dashboard`.
2. **Decoupled 3D Bin Packing Algorithm**:
   - Isolating `recommendations/algorithms/` (`geometry.py`, `orientation.py`, `collision.py`, `extreme_point.py`) completely from Django models and views, allowing pure-Python execution.
3. **Axis-Aligned Orientation Generation**:
   - Permuting 3D dimensions across all 6 spatial orientations and deduplicating equal dimensions (e.g. cubes having 1 unique orientation; square cuboids having 3).
4. **Separating Axis Theorem (SAT) for 3D Cuboids**:
   - Non-overlap checking with touching boundary allowance ($x_A^{end} == x_B$ considered valid adjacent placement without collision).
5. **Comprehensive Test Suite**:
   - Scaffolding unit tests matching all PRD scenario IDs: AL-01 to AL-10 (packing), RT-01 to RT-10 (recommendations), PT-01 to PT-06 (products), BT-01 to BT-06 (boxes), OT-01 to OT-06 (orders), and AUTH-01 to AUTH-05 (security).

---

## 4. Output Rejected or Modified
1. **Check Precedence in Extreme-Point Packing (`extreme_point.py`)**:
   - *Issue*: The initial AI code checked `total_volume > box_dims.volume` before checking whether any individual item exceeded the box boundaries. In test `AL-04` (a single oversized item inside a box), the engine reported *"Total product volume exceeds box internal volume"* instead of the geometrically precise *"Product exceeds box dimensions in all possible orientations"*.
   - *Modification*: We restructured the pipeline to validate each individual item's fit across all rotations first, before applying the total volume check.
2. **JSONField Serialization of `Decimal` and Model Instances**:
   - *Issue*: The AI initially stored raw Decimal values and the model `instance` inside `box_info` within `result_payload`. Calling `Recommendation.objects.create(...)` resulted in a `TypeError: Object of type Decimal is not JSON serializable`.
   - *Modification*: Configured `encoder=DjangoJSONEncoder` on `input_snapshot` and `result_payload` in `recommendations/models.py`, removed model object references, and serialized numeric attributes to clean strings and floats.
3. **App Test File Collision (`recommendations/tests.py`)**:
   - *Issue*: Django's `startapp recommendations` created a default `tests.py`, while our project architecture required a modular `recommendations/tests/` directory with separate test modules. Running `python manage.py test` produced an `ImportError: 'tests' module incorrectly imported`.
   - *Modification*: Deleted the redundant root `tests.py` in `recommendations/`, resolving the unittest discovery clash.

---

## 5. Mistakes Found
1. **Geometric Error Reporting Precedence**:
   - Relying on total volume pre-filtering as the first step masks specific dimensional bounding failures on single large items.
2. **Default JSON Serialization in Django SQLite Backend**:
   - Standard Python `json.dumps` fails on `Decimal` objects unless explicitly handled by `DjangoJSONEncoder`.
3. **Duplicate Test Module Naming**:
   - Having both `tests.py` and a `tests/` directory in the same Django app prevents the unittest runner from resolving the package hierarchy.

---

## 6. Verification
The implementation was independently verified through rigorous validation steps:
1. **Algorithmic Tracing**:
   - Traced coordinate placements by hand for benchmark multi-item orders (e.g. laptop $35\times25\times2$, mouse $12\times7\times4$, keyboard $45\times15\times4$) inside $45\times35\times20$ boxes to verify non-overlapping coordinates.
2. **Deterministic Regression Tests**:
   - Ran `python manage.py test --verbosity=2`, successfully executing all **66 automated tests in 11.3 seconds** with 0 errors and 0 failures.
3. **Database Snapshot Immutability Verification (`test_rt08`)**:
   - Created an order, ran a recommendation, altered the master product's dimensions to $100$ cm and the box cost to $\$99.99$, and confirmed that the existing recommendation retained its exact original snapshot values and coordinates.
4. **End-to-End Demo Seeding**:
   - Executed `python manage.py seed_demo_data` to confirm seamless database migration, user profile instantiation, inventory population, and real order recommendation flows.

---

## 7. Human Decisions
1. **Selection of Gravity-Sorted Extreme Point Heuristic**:
   - Chose the Extreme Point (EP) constructive heuristic with candidate points sorted by $(z \uparrow, y \uparrow, x \uparrow)$. This ensures items are placed on the bottom layer first, against the back wall, and packed left-to-right, closely replicating physical warehouse stacking.
2. **Decoupled Architecture Rule**:
   - Mandated that the entire 3D bin packing engine must operate on pure Python dataclasses (`Dimensions`, `Point3D`, `ItemToPack`, `Placement`) completely independent of Django ORM or HTTP request objects.
3. **Snapshot-Based Data Integrity**:
   - Implemented snapshot fields on `OrderItem` and `Recommendation` so historical shipping audits and cartonization decisions remain permanently reproducible regardless of future catalog modifications.
4. **Three-Tier Deterministic Box Ranking**:
   - Enforced deterministic ranking by `(cost, volume, code)` so identical order inputs always yield the same optimal recommendation.
