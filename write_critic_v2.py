
output_path = r'C:/Users/zzyy/Desktop/ahbu/10-pain-point/affective-state/methodology-critic-v2.md'
bt = chr(96)
sep = '---'
nl = chr(10)

sections = []

# Header
sections.append(f'> **Spec:** {bt}10-pain-point/affective-state/admission.md{bt}')
sections.append('')
sections.append('# Critic pass -- affective-state methodology (v2, re-lock review) -- 2026-05-03')
sections.append('')
sections.append('**Artifacts reviewed:**')
sections.append(f'- {bt}20-plan/affective-state/unlock-note-2026-05-03.md{bt}')
sections.append(f'- {bt}20-plan/affective-state/protocol-lock.md{bt} (re-locked 2026-05-03)')
sections.append(f'- {bt}20-plan/affective-state/approach.md{bt} (revised 2026-05-03)')
sections.append(f'- {bt}20-plan/affective-state/risk-register.md{bt} (revised 2026-05-03)')
sections.append(f'- {bt}30-implement/affective-state/runs/feature_schema_v1.yaml{bt} (locked P-1)')
sections.append(f'- {bt}30-implement/affective-state/runs/pilot_p1_1777729248.json{bt}')
sections.append(f'- {bt}30-implement/affective-state/runs/pilot_p2_1777731569.json{bt}')
sections.append(f'- {bt}30-implement/affective-state/runs/pilot_p2_1777731646.json{bt}')
sections.append(f'- {bt}30-implement/affective-state/runs/pilot_p3_1777731781.json{bt}')
sections.append(f'- {bt}30-implement/affective-state/runs/pilot_p6_1777730572.json{bt}')
sections.append(f'- {bt}10-pain-point/affective-state/admission.md{bt}')
sections.append('')

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(nl.join(sections))
print('Header written, lines:', len(sections))
