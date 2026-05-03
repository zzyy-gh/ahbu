"""
Spec: 30-implement/shared/eval/

Shared evaluation utilities. First-promotion event:
  - originating consumer: ecg-ppg-realworld P-4 (abstention sweep)
  - expected second consumer: any track requiring PPV-vs-coverage or
    selective-classification analysis (sleep-staging confidence
    stratification, affective-state abstention).
"""

from .abstention import selective_classification_curve  # noqa: F401
from .ppv_at_coverage import ppv_at_coverage  # noqa: F401
