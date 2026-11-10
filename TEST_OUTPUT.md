# Test Run Output

Execution command:
```bash
python manage.py test --verbosity=2
```

Executed on: Python 3.11.9, Django 5.2.19, SQLite in-memory test database.

```text
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 66 test(s).
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: accounts, admin, auth, contenttypes, inventory, orders, recommendations, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying accounts.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying inventory.0001_initial... OK
  Applying orders.0001_initial... OK
  Applying recommendations.0001_initial... OK
  Applying recommendations.0002_alter_recommendation_input_snapshot_and_more... OK
  Applying sessions.0001_initial...test_auth01_login_required_for_protected_pages (accounts.tests.AuthenticationTests.test_auth01_login_required_for_protected_pages)
AUTH-01: Anonymous users cannot access dashboard or orders without login. ... ok
test_auth02_user_profile_creation_on_user_created (accounts.tests.AuthenticationTests.test_auth02_user_profile_creation_on_user_created)
AUTH-02: Profile created with appropriate role. ... ok
test_auth03_authenticated_user_can_access_dashboard (accounts.tests.AuthenticationTests.test_auth03_authenticated_user_can_access_dashboard)
AUTH-03: Authenticated user can access protected dashboard. ... ok
test_auth04_user_can_logout (accounts.tests.AuthenticationTests.test_auth04_user_can_logout)
AUTH-04: User can securely log out. ... ok
test_auth05_inactive_user_cannot_login (accounts.tests.AuthenticationTests.test_auth05_inactive_user_cannot_login)
AUTH-05: Inactive user cannot log in. ... ok
test_analytics_view (dashboard.tests.DashboardTests.test_analytics_view) ... ok
test_dash01_to_06_dashboard_statistics (dashboard.tests.DashboardTests.test_dash01_to_06_dashboard_statistics)
DASH-01 to DASH-06: Displays active products, boxes, orders, costs and updates from DB. ... ok
test_pt01_create_valid_product (inventory.tests.ProductModelTests.test_pt01_create_valid_product)
PT-01: Create valid product -> Product created. ... ok
test_pt02_duplicate_sku_raises_error (inventory.tests.ProductModelTests.test_pt02_duplicate_sku_raises_error)
PT-02: Duplicate SKU -> Integrity failure. ... ok
test_pt03_zero_or_negative_dimensions_validation (inventory.tests.ProductModelTests.test_pt03_zero_or_negative_dimensions_validation)
PT-03: Zero or negative dimensions -> Validation failure. ... ok
test_pt04_negative_weight_validation (inventory.tests.ProductModelTests.test_pt04_negative_weight_validation)
PT-04: Negative weight -> Validation failure. ... ok
test_pt05_missing_product_name_validation (inventory.tests.ProductModelTests.test_pt05_missing_product_name_validation)
PT-05: Missing product name -> Validation failure. ... ok
test_pt06_deactivate_product (inventory.tests.ProductModelTests.test_pt06_deactivate_product)
PT-06: Deactivate product -> Product is marked inactive. ... ok
test_bt01_create_valid_box (inventory.tests.ShippingBoxModelTests.test_bt01_create_valid_box)
BT-01: Create valid box -> Box created. ... ok
test_bt02_duplicate_box_code_raises_error (inventory.tests.ShippingBoxModelTests.test_bt02_duplicate_box_code_raises_error)
BT-02: Duplicate box code -> Validation failure. ... ok
test_bt03_negative_cost_validation (inventory.tests.ShippingBoxModelTests.test_bt03_negative_cost_validation)
BT-03: Negative cost -> Validation failure. ... ok
test_bt04_zero_internal_dimensions_validation (inventory.tests.ShippingBoxModelTests.test_bt04_zero_internal_dimensions_validation)
BT-04: Zero internal dimensions -> Validation failure. ... ok
test_bt05_zero_payload_capacity_validation (inventory.tests.ShippingBoxModelTests.test_bt05_zero_payload_capacity_validation)
BT-05: Zero payload capacity -> Validation failure. ... ok
test_bt06_inactive_box (inventory.tests.ShippingBoxModelTests.test_bt06_inactive_box)
BT-06: Inactive box status set. ... ok
test_ot01_create_valid_order (orders.tests.OrderModelTests.test_ot01_create_valid_order)
OT-01: Create valid order -> Order created. ... ok
test_ot02_order_with_no_items_blocks_recommendation (orders.tests.OrderModelTests.test_ot02_order_with_no_items_blocks_recommendation)
OT-02: Order with no items -> Recommendation blocked. ... ok
test_ot03_quantity_zero_validation_failure (orders.tests.OrderModelTests.test_ot03_quantity_zero_validation_failure)
OT-03: Quantity is zero or negative -> Validation failure. ... ok
test_ot04_multiple_products_correct_total_weight (orders.tests.OrderModelTests.test_ot04_multiple_products_correct_total_weight)
OT-04: Multiple products -> Correct total weight. ... ok
test_ot05_multiple_units_item_expansion (orders.tests.OrderModelTests.test_ot05_multiple_units_item_expansion)
OT-05: Multiple units of same product -> Correct item expansion. ... ok
test_ot06_cancelled_order_blocks_recommendation (orders.tests.OrderModelTests.test_ot06_cancelled_order_blocks_recommendation)
OT-06: Cancelled order -> Recommendation blocked. ... ok
test_snapshot_preservation_on_product_update (orders.tests.OrderModelTests.test_snapshot_preservation_on_product_update)
Historical snapshot must not change when product master is modified. ... ok
test_confirmation_and_packaging_lifecycle (recommendations.tests.test_integration.RecommendationIntegrationTests.test_confirmation_and_packaging_lifecycle) ... ok
test_e2e_recommendation_flow_cheapest_eligible_selected (recommendations.tests.test_integration.RecommendationIntegrationTests.test_e2e_recommendation_flow_cheapest_eligible_selected)
End-to-end: Keyboard does not fit in Small Box (38 > 20), fits in Medium and Large. Medium is cheaper. ... ok
test_rt08_historical_recommendation_remains_unchanged_after_master_edits (recommendations.tests.test_integration.RecommendationIntegrationTests.test_rt08_historical_recommendation_remains_unchanged_after_master_edits)
RT-08: Master data changes do not overwrite historical recommendation records. ... ok
test_al05_two_products_overlap (recommendations.tests.test_collision.CollisionTests.test_al05_two_products_overlap)
AL-05: Two products overlap -> overlap detected. ... ok
test_al06_two_products_touch_boundaries_no_overlap (recommendations.tests.test_collision.CollisionTests.test_al06_two_products_touch_boundaries_no_overlap)
AL-06: Two products touch boundaries -> Valid placement, no overlap. ... ok
test_collision_with_existing_placements (recommendations.tests.test_collision.CollisionTests.test_collision_with_existing_placements) ... ok
test_exceeds_box_height (recommendations.tests.test_collision.CollisionTests.test_exceeds_box_height) ... ok
test_exceeds_box_length (recommendations.tests.test_collision.CollisionTests.test_exceeds_box_length) ... ok
test_exceeds_box_width (recommendations.tests.test_collision.CollisionTests.test_exceeds_box_width) ... ok
test_negative_coordinate_invalid (recommendations.tests.test_collision.CollisionTests.test_negative_coordinate_invalid) ... ok
test_within_box_exact_match (recommendations.tests.test_collision.CollisionTests.test_within_box_exact_match) ... ok
test_within_box_valid (recommendations.tests.test_collision.CollisionTests.test_within_box_valid) ... ok
test_cube_has_single_unique_orientation (recommendations.tests.test_orientation.OrientationTests.test_cube_has_single_unique_orientation) ... ok
test_irregular_cuboid_has_six_orientations (recommendations.tests.test_orientation.OrientationTests.test_irregular_cuboid_has_six_orientations) ... ok
test_rotation_disabled_returns_single_orientation (recommendations.tests.test_orientation.OrientationTests.test_rotation_disabled_returns_single_orientation) ... ok
test_square_cuboid_has_three_orientations (recommendations.tests.test_orientation.OrientationTests.test_square_cuboid_has_three_orientations) ... ok
test_al01_product_fits_without_rotation (recommendations.tests.test_packing.PackingAlgorithmTests.test_al01_product_fits_without_rotation)
AL-01: Product fits without rotation -> Successful placement. ... ok
test_al02_product_fits_only_after_rotation (recommendations.tests.test_packing.PackingAlgorithmTests.test_al02_product_fits_only_after_rotation)
AL-02: Product fits only after rotation -> Successful placement. ... ok
test_al03_product_exceeds_box_length (recommendations.tests.test_packing.PackingAlgorithmTests.test_al03_product_exceeds_box_length)
AL-03: Product exceeds box length in given orientation without rotation. ... ok
test_al04_product_exceeds_all_possible_orientations (recommendations.tests.test_packing.PackingAlgorithmTests.test_al04_product_exceeds_all_possible_orientations)
AL-04: Product exceeds all possible orientations -> Placement failure. ... ok
test_al05_two_products_overlap_prevented (recommendations.tests.test_packing.PackingAlgorithmTests.test_al05_two_products_overlap_prevented)
AL-05: Algorithm ensures placed items never overlap. ... ok
test_al06_two_products_touch_boundaries_valid (recommendations.tests.test_packing.PackingAlgorithmTests.test_al06_two_products_touch_boundaries_valid)
AL-06: Two products touch boundaries -> Valid placement. ... ok
test_al07_multiple_products_fit (recommendations.tests.test_packing.PackingAlgorithmTests.test_al07_multiple_products_fit)
AL-07: Multiple different products fit -> All products placed. ... ok
test_al08_product_quantity_greater_than_one (recommendations.tests.test_packing.PackingAlgorithmTests.test_al08_product_quantity_greater_than_one)
AL-08: Product quantity > 1 -> Each instance placed. ... ok
test_al09_product_extends_beyond_box_height (recommendations.tests.test_packing.PackingAlgorithmTests.test_al09_product_extends_beyond_box_height)
AL-09: Product extends beyond box height -> Placement rejected. ... ok
test_al10_no_valid_candidate_point_remains (recommendations.tests.test_packing.PackingAlgorithmTests.test_al10_no_valid_candidate_point_remains)
AL-10: No valid candidate point remains when box is full -> Packing failure. ... ok
test_empty_order_raises_validation_error (recommendations.tests.test_recommendations.RecommendationServiceTests.test_empty_order_raises_validation_error) ... ok
test_rt01_one_suitable_box (recommendations.tests.test_recommendations.RecommendationServiceTests.test_rt01_one_suitable_box)
RT-01: One suitable box -> That box recommended. ... ok
test_rt02_multiple_suitable_boxes_cheapest_recommended (recommendations.tests.test_recommendations.RecommendationServiceTests.test_rt02_multiple_suitable_boxes_cheapest_recommended)
RT-02: Multiple suitable boxes -> Cheapest box recommended. ... ok
test_rt03_equal_box_costs_smaller_volume_preferred (recommendations.tests.test_recommendations.RecommendationServiceTests.test_rt03_equal_box_costs_smaller_volume_preferred)
RT-03: Equal box costs -> Smaller volume preferred. ... ok
test_rt04_equal_costs_and_volumes_code_determines_order (recommendations.tests.test_recommendations.RecommendationServiceTests.test_rt04_equal_costs_and_volumes_code_determines_order)
RT-04: Equal costs and volumes -> Box code determines order. ... ok
test_rt05_weight_capacity_exceeded (recommendations.tests.test_recommendations.RecommendationServiceTests.test_rt05_weight_capacity_exceeded)
RT-05: Weight capacity exceeded -> Box rejected. ... ok
test_rt06_no_suitable_box (recommendations.tests.test_recommendations.RecommendationServiceTests.test_rt06_no_suitable_box)
RT-06: No suitable box -> No recommendation returned. ... ok
test_rt07_inactive_box_excluded (recommendations.tests.test_recommendations.RecommendationServiceTests.test_rt07_inactive_box_excluded)
RT-07: Inactive box -> Box excluded. ... ok
test_rt09_repeated_identical_request_is_deterministic (recommendations.tests.test_recommendations.RecommendationServiceTests.test_rt09_repeated_identical_request_is_deterministic)
RT-09: Repeated identical request -> Same result. ... ok
test_rt10_all_candidate_boxes_rejected_reasons_displayed (recommendations.tests.test_recommendations.RecommendationServiceTests.test_rt10_all_candidate_boxes_rejected_reasons_displayed)
RT-10: All candidate boxes rejected -> Explanations displayed. ... ok
test_empty_items_weight (recommendations.tests.test_weight_calculation.WeightCalculationTests.test_empty_items_weight) ... ok
test_multiple_quantities_weight (recommendations.tests.test_weight_calculation.WeightCalculationTests.test_multiple_quantities_weight) ... ok
test_prd_example_weight (recommendations.tests.test_weight_calculation.WeightCalculationTests.test_prd_example_weight) ... ok
test_single_item_weight (recommendations.tests.test_weight_calculation.WeightCalculationTests.test_single_item_weight) ... ok

----------------------------------------------------------------------
Ran 66 tests in 11.300s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
OK
System check identified no issues (0 silenced).
```

