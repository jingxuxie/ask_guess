# Scenario Samples
## context_resolved
### test_context_000251
- Instruction: Pass me the folder I'm using.
- Variant: active_workspace_salience
- Oracle should ask: False
- Costs: ask=0.15, wrong=0.2
- Objects:
  - folder_white_active_251_a (white folder, in_use, living_room_desk, owner=Sam, salience=0.96)
  - folder_white_stored_251_b (white folder, stored, kitchen_cabinet, owner=Sam, salience=0.04)
- Candidate intents:
  - `{"action": "bring", "intent_id": "i1", "prior": 0.97, "success_equivalence_class": "folder_white_active_251_a_success", "target_id": "folder_white_active_251_a"}`
  - `{"action": "bring", "intent_id": "i2", "prior": 0.03, "success_equivalence_class": "folder_white_stored_251_b_success", "target_id": "folder_white_stored_251_b"}`

### test_context_000386
- Instruction: Bring me the book.
- Variant: active_workspace_salience
- Oracle should ask: False
- Costs: ask=0.15, wrong=0.2
- Objects:
  - book_red_active_386_a (red book, in_use, living_room_table, owner=Sam, salience=0.96)
  - book_red_stored_386_b (red book, stored, office_cabinet, owner=Taylor, salience=0.04)
- Candidate intents:
  - `{"action": "bring", "intent_id": "i1", "prior": 0.97, "success_equivalence_class": "book_red_active_386_a_success", "target_id": "book_red_active_386_a"}`
  - `{"action": "bring", "intent_id": "i2", "prior": 0.03, "success_equivalence_class": "book_red_stored_386_b_success", "target_id": "book_red_stored_386_b"}`

## equivalent_outcome
### test_equivalent_000122
- Instruction: Move a spare folder to the table.
- Variant: interchangeable_targets
- Oracle should ask: False
- Costs: ask=0.1, wrong=0.5
- Objects:
  - spare_folder_brown_122_a (brown folder, spare, living_room_shelf_a, owner=Jordan, salience=0.36)
  - spare_folder_brown_122_b (brown folder, spare, living_room_wall_b, owner=Jordan, salience=0.33)
  - spare_folder_brown_122_c (brown folder, spare, living_room_wall_c, owner=Alex, salience=0.31)
- Candidate intents:
  - `{"action": "move", "intent_id": "i1", "prior": 0.36, "success_equivalence_class": "any_spare_folder_success", "target_id": "spare_folder_brown_122_a"}`
  - `{"action": "move", "intent_id": "i2", "prior": 0.33, "success_equivalence_class": "any_spare_folder_success", "target_id": "spare_folder_brown_122_b"}`
  - `{"action": "move", "intent_id": "i3", "prior": 0.31, "success_equivalence_class": "any_spare_folder_success", "target_id": "spare_folder_brown_122_c"}`

### test_equivalent_000182
- Instruction: Move a spare folder to the table.
- Variant: interchangeable_targets
- Oracle should ask: False
- Costs: ask=0.1, wrong=0.5
- Objects:
  - spare_folder_black_182_a (black folder, spare, office_shelf_a, owner=Jordan, salience=0.36)
  - spare_folder_black_182_b (black folder, spare, office_wall_b, owner=Sam, salience=0.33)
  - spare_folder_black_182_c (black folder, spare, office_corner_c, owner=Riley, salience=0.31)
- Candidate intents:
  - `{"action": "move", "intent_id": "i1", "prior": 0.36, "success_equivalence_class": "any_spare_folder_success", "target_id": "spare_folder_black_182_a"}`
  - `{"action": "move", "intent_id": "i2", "prior": 0.33, "success_equivalence_class": "any_spare_folder_success", "target_id": "spare_folder_black_182_b"}`
  - `{"action": "move", "intent_id": "i3", "prior": 0.31, "success_equivalence_class": "any_spare_folder_success", "target_id": "spare_folder_black_182_c"}`

## preference_social
### test_preference_000294
- Instruction: Put my cup away.
- Variant: owner_visible
- Oracle should ask: False
- Costs: ask=0.05, wrong=1.0
- Objects:
  - pref_cup_black_294_a (black cup, personal, kitchen_desk, owner=Sam, salience=0.99)
  - pref_cup_black_294_b (black cup, guest, kitchen_counter, owner=Taylor, salience=0.01)
- Candidate intents:
  - `{"action": "put_away", "intent_id": "i1", "prior": 0.99, "success_equivalence_class": "pref_cup_black_294_a_success", "target_id": "pref_cup_black_294_a"}`
  - `{"action": "put_away", "intent_id": "i2", "prior": 0.01, "success_equivalence_class": "pref_cup_black_294_b_success", "target_id": "pref_cup_black_294_b"}`

### test_preference_000174
- Instruction: Put my mug away.
- Variant: owner_visible
- Oracle should ask: False
- Costs: ask=0.05, wrong=1.0
- Objects:
  - pref_mug_red_174_a (red mug, personal, kitchen_table, owner=Taylor, salience=0.99)
  - pref_mug_red_174_b (red mug, guest, office_counter, owner=Sam, salience=0.01)
- Candidate intents:
  - `{"action": "put_away", "intent_id": "i1", "prior": 0.99, "success_equivalence_class": "pref_mug_red_174_a_success", "target_id": "pref_mug_red_174_a"}`
  - `{"action": "put_away", "intent_id": "i2", "prior": 0.01, "success_equivalence_class": "pref_mug_red_174_b_success", "target_id": "pref_mug_red_174_b"}`

## referential
### test_referential_000395
- Instruction: Can you bring me the black box?
- Variant: two_matching_objects
- Oracle should ask: True
- Costs: ask=0.05, wrong=1.0
- Objects:
  - box_black_cracked_395_a (black box, cracked, kitchen_table, owner=Alex, salience=0.54)
  - box_black_dirty_395_b (black box, dirty, bedroom_counter, owner=Riley, salience=0.46)
- Candidate intents:
  - `{"action": "bring", "intent_id": "i1", "prior": 0.5371, "success_equivalence_class": "box_black_cracked_395_a_success", "target_id": "box_black_cracked_395_a"}`
  - `{"action": "bring", "intent_id": "i2", "prior": 0.4629, "success_equivalence_class": "box_black_dirty_395_b_success", "target_id": "box_black_dirty_395_b"}`

### test_referential_000375
- Instruction: Can you bring me the red book?
- Variant: two_matching_objects
- Oracle should ask: True
- Costs: ask=0.05, wrong=1.0
- Objects:
  - book_red_clean_375_a (red book, clean, office_sink, owner=Riley, salience=0.54)
  - book_red_cracked_375_b (red book, cracked, kitchen_cabinet, owner=Morgan, salience=0.46)
- Candidate intents:
  - `{"action": "bring", "intent_id": "i1", "prior": 0.4869, "success_equivalence_class": "book_red_clean_375_a_success", "target_id": "book_red_clean_375_a"}`
  - `{"action": "bring", "intent_id": "i2", "prior": 0.5131, "success_equivalence_class": "book_red_cracked_375_b_success", "target_id": "book_red_cracked_375_b"}`

## risk_sensitive
### test_risk_000033
- Instruction: Delete the old draft.
- Variant: high_wrong_action_cost
- Oracle should ask: True
- Costs: ask=0.05, wrong=3.0
- Objects:
  - old_draft_private_33_a (blue draft, old_private, office_desk, owner=Riley, salience=0.78)
  - old_draft_shared_33_b (blue draft, old_shared, office_shelf, owner=Jordan, salience=0.22)
- Candidate intents:
  - `{"action": "delete", "intent_id": "i1", "prior": 0.8409, "success_equivalence_class": "old_draft_private_33_a_success", "target_id": "old_draft_private_33_a"}`
  - `{"action": "delete", "intent_id": "i2", "prior": 0.1591, "success_equivalence_class": "old_draft_shared_33_b_success", "target_id": "old_draft_shared_33_b"}`

### test_risk_000043
- Instruction: Delete the old folder.
- Variant: high_wrong_action_cost
- Oracle should ask: True
- Costs: ask=0.05, wrong=3.0
- Objects:
  - old_folder_private_43_a (blue folder, old_private, office_folder, owner=Riley, salience=0.78)
  - old_folder_shared_43_b (blue folder, old_shared, office_shelf, owner=Alex, salience=0.22)
- Candidate intents:
  - `{"action": "delete", "intent_id": "i1", "prior": 0.7947, "success_equivalence_class": "old_folder_private_43_a_success", "target_id": "old_folder_private_43_a"}`
  - `{"action": "delete", "intent_id": "i2", "prior": 0.2053, "success_equivalence_class": "old_folder_shared_43_b_success", "target_id": "old_folder_shared_43_b"}`

