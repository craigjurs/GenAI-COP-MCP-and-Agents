# Design Document

## DonorEvaluator Class

---

### Overview

`DonorEvaluator` is a Python class designed to assist phlebotomists and clinic staff in estimating a donor’s total blood volume (TBV), calculating the maximum allowable blood draw volume, and assessing donor eligibility based on a comprehensive set of input data. It performs necessary unit normalization and applies medical criteria to ensure safe donation practices.

---

### Functional Requirements

- Accept optional donor name or ID.
- Accept donor age (years), gender, weight, height, hemoglobin level, and optionally the last donation date.
- Convert weight and height to metric (kg, cm) units.
- Calculate TBV using Nadler’s formula:
  - For males:  
    TBV = 0.3669 × (height_m)^3 + 0.03219 × weight_kg + 0.6041
  - For females:  
    TBV = 0.3561 × (height_m)^3 + 0.03308 × weight_kg + 0.1833
  - For others/unknown: average of male and female formulas.
- Compute max draw volume as 10% of TBV in milliliters.
- Validate eligibility based on:
  - Age ≥ 16
  - Weight ≥ 50 kg
  - Hemoglobin ≥ 12.5 g/dL
  - If last donation date is provided, at least 56 days ago.
- Return eligibility (✅/❌), reasons if ineligible, TBV (liters), max draw volume (mL), days since last donation (if applicable), and donor id/name.

---

### Data Inputs and Normalization

| Input                | Type       | Optionality | Notes                                         |
|----------------------|------------|-------------|-----------------------------------------------|
| donor_name_or_id      | str        | Optional    | Identification or name                         |
| age                  | int        | Required    | Years, must be >= 16                           |
| gender               | str        | Required    | "Male", "Female", "Other" (case-insensitive) |
| weight               | float      | Required    | Weight value                                   |
| weight_unit          | str        | Required    | "kg" or "lbs" (case-insensitive)              |
| height               | float      | Required    | Height value                                   |
| height_unit          | str        | Required    | "cm" or "inches" (case-insensitive)           |
| hemoglobin           | float      | Required    | g/dL                                           |
| last_donation_date   | str or date| Optional    | ISO 8601 (`YYYY-MM-DD`) or `datetime.date`    |

- Weight converted to kilograms (if in lbs: multiply by 0.453592).
- Height converted to centimeters (if in inches: multiply by 2.54).
- Height converted to meters for TBV formula.

---

### Internal Constants


WEIGHT_LBS_TO_KG = 0.453592
HEIGHT_IN_TO_CM = 2.54
MIN_AGE = 16
MIN_WEIGHT_KG = 50
MIN_HEMOGLOBIN = 12.5
MIN_DAYS_SINCE_DONATION = 56


---

### Class Interface and Methods


from datetime import datetime, date
from typing import Optional, Union, Dict, List

class DonorEvaluator:
    def __init__(self,
                 donor_name_or_id: Optional[str] = None,
                 age: int = None,
                 gender: str = None,
                 weight: float = None,
                 weight_unit: str = None,
                 height: float = None,
                 height_unit: str = None,
                 hemoglobin: float = None,
                 last_donation_date: Optional[Union[str, date]] = None):
        """
        Initialize the DonorEvaluator with donor information.
        Raises ValueError for missing or invalid required parameters.
        """

    def _convert_weight_to_kg(self, weight: float, unit: str) -> float:
        """
        Converts weight to kilograms if needed.
        Raises ValueError if unit is unrecognized.
        """

    def _convert_height_to_cm(self, height: float, unit: str) -> float:
        """
        Converts height to centimeters if needed.
        Raises ValueError if unit is unrecognized.
        """

    def _calculate_tbv(self, height_cm: float, weight_kg: float, gender: str) -> float:
        """
        Calculate Total Blood Volume in liters using Nadler’s formula.
        Height is converted to meters internally for the formula.
        Gender is case-insensitive with handling for 'other'.
        """

    def _calculate_max_draw_volume(self, tbv_liters: float) -> int:
        """
        Compute 10% of TBV, return in milliliters as integer.
        """

    def _days_since_last_donation(self, last_donation_date: Optional[Union[str, date]]) -> Optional[int]:
        """
        Calculate the number of days since last donation.
        Returns None if last_donation_date is not provided.
        Raises ValueError if date parsing fails or date is in the future.
        """

    def evaluate(self) -> Dict[str, Optional[Union[bool, str, List[str], float, int]]]:
        """
        Perform eligibility checks and calculations. Returns structured dictionary:
          - 'eligible': bool
          - 'eligibility_status': str ("✅ Eligible" or "❌ Ineligible")
          - 'reasons': List[str] (empty if eligible)
          - 'total_blood_volume_l': float (3 decimals)
          - 'max_draw_volume_ml': int
          - 'days_since_last_donation': int or None
          - 'donor_name_or_id': str or None
        """


---

### Data Flow and Logic

1. **Initialization:**

   - Check presence of required parameters.
   - Normalize gender to lowercase and validate.
   - Convert weight and height units.
   - Parse `last_donation_date` if provided.

2. **Computations:**

   - Convert height to meters for TBV calculation.
   - Calculate TBV using appropriate Nadler formula.
   - Calculate max draw volume as 10% of TBV in mL.
   - Calculate days since last donation if applicable.

3. **Eligibility Checks:**

   - Age ≥ 16
   - Weight ≥ 50 kg
   - Hemoglobin ≥ 12.5 g/dL
   - Days since last donation ≥ 56 (if date provided)

4. **Build output:**

   - If all checks pass, mark eligible with ✅
   - Else, mark ineligible with ❌ and accumulate reasons
   - Include calculated volumes and days since last donation in output.

---

### Eligibility Messages

| Condition                  | Failure Message                                |
|----------------------------|-----------------------------------------------|
| Age < 16                   | "Age must be at least 16 years."               |
| Weight < 50 kg             | "Weight must be at least 50 kg."                |
| Hemoglobin < 12.5 g/dL     | "Hemoglobin must be at least 12.5 g/dL."       |
| Last donation < 56 days ago| "Last donation must be at least 56 days ago."  |

---

### Example Output


{
    "eligible": True,
    "eligibility_status": "✅ Eligible",
    "reasons": [],
    "total_blood_volume_l": 4.890,
    "max_draw_volume_ml": 489,
    "days_since_last_donation": 120,
    "donor_name_or_id": "JohnDoe123"
}


Or if not eligible:


{
    "eligible": False,
    "eligibility_status": "❌ Ineligible",
    "reasons": [
        "Weight must be at least 50 kg.",
        "Last donation must be at least 56 days ago."
    ],
    "total_blood_volume_l": 3.755,
    "max_draw_volume_ml": 375,
    "days_since_last_donation": 20,
    "donor_name_or_id": "JohnDoe123"
}


---

### Error Handling

- Invalid or missing required inputs raise `ValueError` with clear messages.
- Unrecognized units raise `ValueError`.
- If `last_donation_date` string fails to parse or is in the future, a `ValueError` is raised.
- The evaluate method itself does not raise; pre-validation enforced in init.

---

### Dependencies

- Python Standard Library:
  - `datetime` for date parsing and calculations
  - `typing` for type hints (optional)

---

### Summary

The `DonorEvaluator` encapsulates all aspects of donor eligibility determination and blood volume estimation. It ensures all inputs are normalized, validated, and calculated according to established medical formulas and safety guidelines. Structured output allows integration with UI or downstream processes used in clinic workflows.