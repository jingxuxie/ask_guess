# Failure Examples

## api_ask_needed / test_equivalent_000122
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare folder should I move to the table?
- Answer: the spare one
- Final action: `{'action': 'move', 'target_id': 'spare_folder_brown_122_a', 'type': 'ACT'}`

## api_ask_needed_cot / test_equivalent_000122
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare folder should I move to the table?
- Answer: the spare one
- Final action: `{'action': 'move', 'target_id': 'spare_folder_brown_122_a', 'type': 'ACT'}`

## api_ask_needed / test_equivalent_000182
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare folder should I move to the table?
- Answer: the spare one
- Final action: `{'action': 'move', 'target_id': 'spare_folder_black_182_a', 'type': 'ACT'}`

## api_ask_needed_cot / test_equivalent_000182
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare folder should I move to the table: Riley’s, Sam’s, or Jordan’s?
- Answer: the spare one
- Final action: `{'action': 'move', 'target_id': 'spare_folder_black_182_a', 'type': 'ACT'}`

## api_ask_needed_cot / test_equivalent_000257
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare box should I move to the table?
- Answer: the spare one in the office wall a
- Final action: `{'action': 'move', 'target_id': 'spare_box_white_257_a', 'type': 'ACT'}`

## api_ask_needed / test_equivalent_000212
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare chair should I move to the table?
- Answer: the spare one in the hallway wall b
- Final action: `{'action': 'move', 'target_id': 'spare_chair_brown_212_b', 'type': 'ACT'}`

## api_ask_needed_cot / test_equivalent_000212
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare chair should I move to the table?
- Answer: the spare one in the hallway wall b
- Final action: `{'action': 'move', 'target_id': 'spare_chair_brown_212_b', 'type': 'ACT'}`

## api_ask_needed_cot / test_equivalent_000337
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare box should I move to the table?
- Answer: the spare one in the hallway shelf c
- Final action: `{'action': 'move', 'target_id': 'spare_box_brown_337_c', 'type': 'ACT'}`

## api_ask_needed / test_equivalent_000057
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare chair should I move to the table?
- Answer: the spare one in the office corner a
- Final action: `{'action': 'move', 'target_id': 'spare_chair_black_57_a', 'type': 'ACT'}`

## api_ask_needed_cot / test_equivalent_000057
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare chair should I move to the table?
- Answer: the spare one in the office corner a
- Final action: `{'action': 'move', 'target_id': 'spare_chair_black_57_a', 'type': 'ACT'}`

## api_ask_needed / test_context_000386
- Split/category: test / context_resolved (active_workspace_salience)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.85
- Question: Which book would you like me to bring: the red book on the living room table or the red book stored in the office cabinet?
- Answer: the one in the living room table
- Final action: `{'action': 'bring', 'target_id': 'book_red_active_386_a', 'type': 'ACT'}`

## api_ask_needed_cot / test_context_000386
- Split/category: test / context_resolved (active_workspace_salience)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.85
- Question: Which book would you like me to bring?
- Answer: the in use one in the living room table
- Final action: `{'action': 'bring', 'target_id': 'book_red_active_386_a', 'type': 'ACT'}`

## api_ask_needed / test_equivalent_000252
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare box should I move to the table?
- Answer: the spare one in the office corner b
- Final action: `{'action': 'move', 'target_id': 'spare_box_white_252_b', 'type': 'ACT'}`

## api_ask_needed_cot / test_equivalent_000252
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare box should I move to the table?
- Answer: the spare one in the office corner b
- Final action: `{'action': 'move', 'target_id': 'spare_box_white_252_b', 'type': 'ACT'}`

## api_direct_act / test_referential_000395
- Split/category: test / referential (two_matching_objects)
- Asked: False | Oracle should ask: True
- Success: True | Reward: 1.0
- Final action: `{'action': 'bring', 'target_id': 'box_black_dirty_395_b', 'type': 'ACT'}`

## api_direct_act / test_preference_000339
- Split/category: test / preference_social (owner_hidden)
- Asked: False | Oracle should ask: True
- Success: False | Reward: -1.0
- Final action: `{'action': 'put_away', 'target_id': 'pref_box_red_339_a', 'type': 'ACT'}`

## api_ask_needed / test_equivalent_000217
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare folder should I move to the table?
- Answer: the spare one
- Final action: `{'action': 'move', 'target_id': 'spare_folder_white_217_a', 'type': 'ACT'}`

## api_ask_needed_cot / test_equivalent_000217
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare folder should I move to the table?
- Answer: the spare one
- Final action: `{'action': 'move', 'target_id': 'spare_folder_white_217_a', 'type': 'ACT'}`

## api_ask_needed / test_context_000261
- Split/category: test / context_resolved (active_workspace_salience)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.85
- Question: Which book do you want me to bring: the blue book on the office counter or the blue book stored in the hallway cabinet?
- Answer: the in use one in the office counter
- Final action: `{'action': 'bring', 'target_id': 'book_blue_active_261_a', 'type': 'ACT'}`

## api_ask_needed_cot / test_context_000261
- Split/category: test / context_resolved (active_workspace_salience)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.85
- Question: Which book would you like me to bring: the blue book on the office counter or the blue book stored in the hallway cabinet?
- Answer: the in use one in the office counter
- Final action: `{'action': 'bring', 'target_id': 'book_blue_active_261_a', 'type': 'ACT'}`
