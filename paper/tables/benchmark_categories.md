# Benchmark Categories

Counts and oracle ask rates are computed from the canonical generated dataset.

| Category | Episodes | Oracle ask | Expected behavior | Diagnostic role | Example instruction |
| --- | --- | --- | --- | --- | --- |
| Referential ambiguity | 280 | 1.000 | Ask | Multiple matching objects; wrong target matters. | Can you bring me the black box? |
| Context-resolved | 280 | 0.000 | Act | Language is underspecified, but context/salience resolves it. | Pass me the folder I'm using. |
| Equivalent outcome | 280 | 0.000 | Act | Multiple targets exist, but any choice succeeds. | Move a spare folder to the table. |
| Risk-sensitive | 280 | 1.000 | Ask | Moderate uncertainty with high wrong-action cost. | Delete the old draft. |
| Preference/social | 280 | 0.500 | Ask iff owner hidden | Owner or preference determines whether to ask or act. | Put my cup away. |
