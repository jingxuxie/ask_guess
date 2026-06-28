# Failure Examples

## api_ask_needed / test_equivalent_000122
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare folder would you like me to move to the table?
- Answer: the spare one
- Final action: `{'action': 'move', 'target_id': 'spare_folder_brown_122_a', 'type': 'ACT'}`

## api_ecu / test_equivalent_000122
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Are you referring to moving the spare folder owned by Jordan or the one owned by Alex?
- Answer: the spare one
- Final action: `{'action': 'move', 'target_id': 'spare_folder_brown_122_b', 'type': 'ACT'}`

## api_ask_needed / test_equivalent_000182
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare folder would you like me to move to the table?
- Answer: the spare one
- Final action: `{'action': 'move', 'target_id': 'spare_folder_black_182_a', 'type': 'ACT'}`

## api_ecu / test_equivalent_000182
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Are you asking to move the folder owned by Jordan, Sam, or Riley?
- Answer: the spare one
- Final action: `{'action': 'move', 'target_id': 'spare_folder_black_182_a', 'type': 'ACT'}`

## api_ask_needed / test_equivalent_000257
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare box would you like me to move to the table?
- Answer: the spare one in the office wall a
- Final action: `{'action': 'move', 'target_id': 'spare_box_white_257_a', 'type': 'ACT'}`

## api_ecu / test_equivalent_000257
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Are you asking to move a specific spare box owned by a particular person, or any spare box in general?
- Answer: the spare one in the office wall a
- Final action: `{'action': 'move', 'target_id': 'spare_box_white_257_a', 'type': 'ACT'}`

## api_ask_needed / test_equivalent_000212
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare chair would you like me to move to the table?
- Answer: the spare one in the hallway wall b
- Final action: `{'action': 'move', 'target_id': 'spare_chair_brown_212_b', 'type': 'ACT'}`

## api_ecu / test_equivalent_000212
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Are you asking to move a specific spare chair owned by Riley, Taylor, or Jordan?
- Answer: the spare one in the hallway wall b
- Final action: `{'action': 'move', 'target_id': 'spare_chair_brown_212_b', 'type': 'ACT'}`

## api_direct_act / test_preference_000174
- Split/category: test / preference_social (owner_visible)
- Asked: False | Oracle should ask: False
- Success: False | Reward: -1.0
- Final action: `{'action': 'move', 'target_id': 'pref_mug_red_174_a', 'type': 'ACT'}`

## api_ask_needed / test_preference_000174
- Split/category: test / preference_social (owner_visible)
- Asked: False | Oracle should ask: False
- Success: False | Reward: -1.0
- Final action: `{'action': 'move', 'target_id': 'pref_mug_red_174_a', 'type': 'ACT'}`

## api_ask_needed / test_equivalent_000337
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Which spare box would you like me to move to the table?
- Answer: the spare one in the hallway shelf c
- Final action: `{'action': 'move', 'target_id': 'spare_box_brown_337_c', 'type': 'ACT'}`

## api_ecu / test_equivalent_000337
- Split/category: test / equivalent_outcome (interchangeable_targets)
- Asked: True | Oracle should ask: False
- Success: True | Reward: 0.9
- Question: Are you asking to move Riley's spare brown box or Alex's?
- Answer: the spare one in the hallway shelf c
- Final action: `{'action': 'move', 'target_id': 'spare_box_brown_337_c', 'type': 'ACT'}`

## api_direct_act / test_preference_000284
- Split/category: test / preference_social (owner_visible)
- Asked: False | Oracle should ask: False
- Success: False | Reward: -1.0
- Final action: `{'action': 'move', 'target_id': 'pref_book_red_284_a', 'type': 'ACT'}`

## api_ecu / test_preference_000284
- Split/category: test / preference_social (owner_visible)
- Asked: False | Oracle should ask: False
- Success: False | Reward: -1.0
- Final action: `{'action': 'move to office_shelf', 'target_id': 'pref_book_red_284_a', 'type': 'ACT'}`

## api_direct_act / test_referential_000395
- Split/category: test / referential (two_matching_objects)
- Asked: False | Oracle should ask: True
- Success: False | Reward: -1.0
- Final action: `{'action': 'pick_up', 'target_id': 'box_black_cracked_395_a', 'type': 'ACT'}`

## api_ask_needed / test_referential_000395
- Split/category: test / referential (two_matching_objects)
- Asked: False | Oracle should ask: True
- Success: False | Reward: -1.0
- Final action: `{'action': 'pick_up', 'target_id': 'box_black_cracked_395_a', 'type': 'ACT'}`

## api_ecu / test_referential_000395
- Split/category: test / referential (two_matching_objects)
- Asked: False | Oracle should ask: True
- Success: False | Reward: -1.0
- Final action: `{'action': 'bring', 'target_id': 'box_black_cracked_395_a', 'type': 'ACT'}`

## api_direct_act / test_preference_000339
- Split/category: test / preference_social (owner_hidden)
- Asked: False | Oracle should ask: True
- Success: False | Reward: -1.0
- Final action: `{'action': 'move', 'target_id': 'pref_box_red_339_b', 'type': 'ACT'}`

## api_ask_needed / test_preference_000339
- Split/category: test / preference_social (owner_hidden)
- Asked: True | Oracle should ask: True
- Success: False | Reward: -1.05
- Question: Which box would you like me to put away: the red box on the office table or the red box on the kitchen shelf?
- Answer: the one in the kitchen shelf
- Final action: `{'action': 'move', 'target_id': 'pref_box_red_339_b', 'type': 'ACT'}`

## api_ecu / test_preference_000339
- Split/category: test / preference_social (owner_hidden)
- Asked: True | Oracle should ask: True
- Success: False | Reward: -1.05
- Question: Are you referring to the red box on the office table or the one on the kitchen shelf?
- Answer: the one in the kitchen shelf
- Final action: `{'action': 'pick_up', 'target_id': 'pref_box_red_339_b', 'type': 'ACT'}`

