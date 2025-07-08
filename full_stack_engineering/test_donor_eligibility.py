import unittest
from datetime import date, timedelta, datetime
from donor_eligibility import DonorEvaluator

class TestDonorEvaluator(unittest.TestCase):
    def setUp(self):
        self.valid_params = {
            "donor_name_or_id": "donor1",
            "age": 30,
            "gender": "Male",
            "weight": 70,
            "weight_unit": "kg",
            "height": 175,
            "height_unit": "cm",
            "hemoglobin": 14.0,
            "last_donation_date": (date.today() - timedelta(days=60)).isoformat()
        }

    def test_valid_initialization(self):
        evaluator = DonorEvaluator(**self.valid_params)
        self.assertEqual(evaluator.age, 30)
        self.assertEqual(evaluator.gender, "male")
        self.assertAlmostEqual(evaluator.weight_kg, 70)
        self.assertAlmostEqual(evaluator.height_cm, 175)
        self.assertEqual(evaluator.hemoglobin, 14.0)
        self.assertIsInstance(evaluator.days_since_last_donation, int)
        self.assertEqual(evaluator.donor_name_or_id, "donor1")

    def test_missing_required_parameters(self):
        params = self.valid_params.copy()
        for required_field in ["age", "gender", "weight", "weight_unit", "height", "height_unit", "hemoglobin"]:
            params_copy = params.copy()
            params_copy[required_field] = None
            with self.assertRaises(ValueError):
                DonorEvaluator(**params_copy)

    def test_invalid_age(self):
        params = self.valid_params.copy()
        params["age"] = -1
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)
        params["age"] = "30"
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

    def test_invalid_gender_value(self):
        params = self.valid_params.copy()
        params["gender"] = "InvalidGender"
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

    def test_invalid_gender_type(self):
        params = self.valid_params.copy()
        params["gender"] = 123
        with self.assertRaises(AttributeError):
            DonorEvaluator(**params)

    def test_invalid_weight(self):
        params = self.valid_params.copy()
        params["weight"] = -10
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)
        params["weight"] = "seventy"
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

    def test_invalid_weight_unit(self):
        params = self.valid_params.copy()
        params["weight_unit"] = "stones"
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)
        params["weight_unit"] = 5
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

    def test_weight_conversion_lbs(self):
        params = self.valid_params.copy()
        params["weight_unit"] = "lbs"
        params["weight"] = 100
        evaluator = DonorEvaluator(**params)
        self.assertAlmostEqual(evaluator.weight_kg, 100 * 0.453592, places=5)

    def test_invalid_height(self):
        params = self.valid_params.copy()
        params["height"] = -170
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)
        params["height"] = "one seventy"
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

    def test_invalid_height_unit(self):
        params = self.valid_params.copy()
        params["height_unit"] = "feet"
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)
        params["height_unit"] = 10
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

    def test_height_conversion_inches(self):
        params = self.valid_params.copy()
        params["height_unit"] = "inches"
        params["height"] = 70
        evaluator = DonorEvaluator(**params)
        self.assertAlmostEqual(evaluator.height_cm, 70 * 2.54, places=5)

    def test_invalid_hemoglobin(self):
        params = self.valid_params.copy()
        params["hemoglobin"] = -12.5
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)
        params["hemoglobin"] = "12.5"
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

    def test_invalid_donor_name_or_id(self):
        params = self.valid_params.copy()
        params["donor_name_or_id"] = 12345
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

    def test_days_since_last_donation_string_and_date(self):
        params = self.valid_params.copy()
        past_date_str = (date.today() - timedelta(days=30)).isoformat()
        params["last_donation_date"] = past_date_str
        evaluator_str = DonorEvaluator(**params)
        self.assertEqual(evaluator_str.days_since_last_donation, 30)

        params["last_donation_date"] = date.today() - timedelta(days=30)
        evaluator_date = DonorEvaluator(**params)
        self.assertEqual(evaluator_date.days_since_last_donation, 30)

    def test_days_since_last_donation_none_and_future_date(self):
        params = self.valid_params.copy()
        params["last_donation_date"] = None
        evaluator = DonorEvaluator(**params)
        self.assertIsNone(evaluator.days_since_last_donation)

        params["last_donation_date"] = (date.today() + timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

        params["last_donation_date"] = datetime.today()
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

        params["last_donation_date"] = "invalid-date"
        with self.assertRaises(ValueError):
            DonorEvaluator(**params)

    def test_evaluate_all_criteria_met(self):
        evaluator = DonorEvaluator(**self.valid_params)
        result = evaluator.evaluate()
        self.assertTrue(result["eligible"])
        self.assertEqual(result["eligibility_status"], "✅ Eligible")
        self.assertEqual(result["reasons"], [])
        self.assertEqual(result["donor_name_or_id"], "donor1")
        self.assertIsInstance(result["total_blood_volume_l"], float)
        self.assertIsInstance(result["max_draw_volume_ml"], int)
        self.assertIsInstance(result["days_since_last_donation"], int)

    def test_evaluate_age_below_min(self):
        params = self.valid_params.copy()
        params["age"] = 15
        evaluator = DonorEvaluator(**params)
        result = evaluator.evaluate()
        self.assertFalse(result["eligible"])
        self.assertIn("Age must be at least 16 years.", result["reasons"])

    def test_evaluate_weight_below_min(self):
        params = self.valid_params.copy()
        params["weight"] = 49
        params["weight_unit"] = "kg"
        evaluator = DonorEvaluator(**params)
        result = evaluator.evaluate()
        self.assertFalse(result["eligible"])
        self.assertIn("Weight must be at least 50 kg.", result["reasons"])

    def test_evaluate_hemoglobin_below_min(self):
        params = self.valid_params.copy()
        params["hemoglobin"] = 12.4
        evaluator = DonorEvaluator(**params)
        result = evaluator.evaluate()
        self.assertFalse(result["eligible"])
        self.assertIn("Hemoglobin must be at least 12.5 g/dL.", result["reasons"])

    def test_evaluate_last_donation_recent(self):
        params = self.valid_params.copy()
        params["last_donation_date"] = (date.today() - timedelta(days=30)).isoformat()
        evaluator = DonorEvaluator(**params)
        result = evaluator.evaluate()
        self.assertFalse(result["eligible"])
        self.assertIn("Last donation must be at least 56 days ago.", result["reasons"])

    def test_evaluate_multiple_reasons(self):
        params = self.valid_params.copy()
        params["age"] = 15
        params["weight"] = 40
        params["weight_unit"] = "kg"
        params["hemoglobin"] = 10
        params["last_donation_date"] = (date.today() - timedelta(days=10)).isoformat()
        evaluator = DonorEvaluator(**params)
        result = evaluator.evaluate()
        self.assertFalse(result["eligible"])
        self.assertEqual(len(result["reasons"]), 4)

if __name__ == '__main__':
    unittest.main()