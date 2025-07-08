from datetime import datetime, date
from typing import Optional, Union, Dict, List

WEIGHT_LBS_TO_KG = 0.453592
HEIGHT_IN_TO_CM = 2.54
MIN_AGE = 16
MIN_WEIGHT_KG = 50
MIN_HEMOGLOBIN = 12.5
MIN_DAYS_SINCE_DONATION = 56

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
        if age is None:
            raise ValueError("Age is required.")
        if gender is None:
            raise ValueError("Gender is required.")
        if weight is None:
            raise ValueError("Weight is required.")
        if weight_unit is None:
            raise ValueError("Weight unit is required.")
        if height is None:
            raise ValueError("Height is required.")
        if height_unit is None:
            raise ValueError("Height unit is required.")
        if hemoglobin is None:
            raise ValueError("Hemoglobin level is required.")
        if not isinstance(age, int) or age < 0:
            raise ValueError("Age must be a non-negative integer.")
        self.age = age

        gender_norm = gender.strip().lower()
        if gender_norm not in {"male", "female", "other"}:
            raise ValueError("Gender must be 'Male', 'Female', or 'Other' (case-insensitive).")
        self.gender = gender_norm

        if not isinstance(weight, (int, float)) or weight <= 0:
            raise ValueError("Weight must be a positive number.")
        self.weight_kg = self._convert_weight_to_kg(weight, weight_unit)

        if not isinstance(height, (int, float)) or height <= 0:
            raise ValueError("Height must be a positive number.")
        self.height_cm = self._convert_height_to_cm(height, height_unit)

        if not isinstance(hemoglobin, (int, float)) or hemoglobin <= 0:
            raise ValueError("Hemoglobin must be a positive number.")
        self.hemoglobin = hemoglobin

        if donor_name_or_id is not None:
            if not isinstance(donor_name_or_id, str):
                raise ValueError("donor_name_or_id must be a string if provided.")
            self.donor_name_or_id = donor_name_or_id
        else:
            self.donor_name_or_id = None

        self.days_since_last_donation = None
        if last_donation_date is not None:
            self.days_since_last_donation = self._days_since_last_donation(last_donation_date)

        self.total_blood_volume_l = self._calculate_tbv(self.height_cm, self.weight_kg, self.gender)
        self.max_draw_volume_ml = self._calculate_max_draw_volume(self.total_blood_volume_l)

    def _convert_weight_to_kg(self, weight: float, unit: str) -> float:
        if not isinstance(unit, str):
            raise ValueError("Weight unit must be a string.")
        unit_norm = unit.strip().lower()
        if unit_norm == "kg":
            return float(weight)
        elif unit_norm == "lbs":
            return float(weight) * WEIGHT_LBS_TO_KG
        else:
            raise ValueError("Weight unit must be 'kg' or 'lbs' (case-insensitive).")

    def _convert_height_to_cm(self, height: float, unit: str) -> float:
        if not isinstance(unit, str):
            raise ValueError("Height unit must be a string.")
        unit_norm = unit.strip().lower()
        if unit_norm == "cm":
            return float(height)
        elif unit_norm == "inches":
            return float(height) * HEIGHT_IN_TO_CM
        else:
            raise ValueError("Height unit must be 'cm' or 'inches' (case-insensitive).")

    def _calculate_tbv(self, height_cm: float, weight_kg: float, gender: str) -> float:
        height_m = height_cm / 100.0
        gender_lower = gender.lower()
        if gender_lower == "male":
            tbv = 0.3669 * (height_m ** 3) + 0.03219 * weight_kg + 0.6041
        elif gender_lower == "female":
            tbv = 0.3561 * (height_m ** 3) + 0.03308 * weight_kg + 0.1833
        else:
            tbv_male = 0.3669 * (height_m ** 3) + 0.03219 * weight_kg + 0.6041
            tbv_female = 0.3561 * (height_m ** 3) + 0.03308 * weight_kg + 0.1833
            tbv = (tbv_male + tbv_female) / 2.0
        return round(tbv, 3)

    def _calculate_max_draw_volume(self, tbv_liters: float) -> int:
        max_draw_ml = int(round(tbv_liters * 1000 * 0.10))
        return max_draw_ml

    def _days_since_last_donation(self, last_donation_date: Optional[Union[str, date]]) -> Optional[int]:
        if last_donation_date is None:
            return None
        if isinstance(last_donation_date, date) and not isinstance(last_donation_date, datetime):
            donation_date = last_donation_date
        elif isinstance(last_donation_date, str):
            try:
                donation_date = datetime.strptime(last_donation_date.strip(), "%Y-%m-%d").date()
            except Exception:
                raise ValueError("last_donation_date string must be in ISO 8601 format YYYY-MM-DD.")
        else:
            raise ValueError("last_donation_date must be a string in ISO 8601 format or a datetime.date object.")
        today = date.today()
        if donation_date > today:
            raise ValueError("last_donation_date cannot be in the future.")
        delta = (today - donation_date).days
        return delta

    def evaluate(self) -> Dict[str, Optional[Union[bool, str, List[str], float, int]]]:
        reasons: List[str] = []
        if self.age < MIN_AGE:
            reasons.append("Age must be at least 16 years.")
        if self.weight_kg < MIN_WEIGHT_KG:
            reasons.append("Weight must be at least 50 kg.")
        if self.hemoglobin < MIN_HEMOGLOBIN:
            reasons.append("Hemoglobin must be at least 12.5 g/dL.")
        if self.days_since_last_donation is not None and self.days_since_last_donation < MIN_DAYS_SINCE_DONATION:
            reasons.append("Last donation must be at least 56 days ago.")
        eligible = len(reasons) == 0
        return {
            "eligible": eligible,
            "eligibility_status": "✅ Eligible" if eligible else "❌ Ineligible",
            "reasons": reasons,
            "total_blood_volume_l": self.total_blood_volume_l,
            "max_draw_volume_ml": self.max_draw_volume_ml,
            "days_since_last_donation": self.days_since_last_donation,
            "donor_name_or_id": self.donor_name_or_id
        }