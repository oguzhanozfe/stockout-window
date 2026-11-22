import unittest
from project import analyze


def check(stock, values):
    return analyze({"sku": "fixture", "opening_units": stock,
                    "days": [{"date": f"2026-01-{i:02d}", "receipts": r, "demand": d}
                             for i, (r, d) in enumerate(values, 1)]})


class InventoryTests(unittest.TestCase):
    def test_zero_closing_inventory_can_fulfill_all_demand(self):
        r = check(3, [(0, 3), (0, 0)])
        self.assertEqual(r["metrics"]["Shortage windows"], 0)
        self.assertEqual(r["metrics"]["Unmet units"], 0)

    def test_receipts_arrive_before_demand_and_lost_sales_do_not_carry(self):
        r = check(0, [(0, 4), (3, 2)])
        self.assertEqual(r["metrics"]["Final stock"], 1)
        self.assertEqual(r["rows"][1]["Fulfilled"], 2)

    def test_two_shortages_and_conservation(self):
        r = check(0, [(0, 1), (0, 3), (2, 1), (0, 4)])
        self.assertEqual((r["metrics"]["Shortage windows"], r["metrics"]["Longest shortage (days)"]), (2, 2))
        for day in r["rows"]:
            self.assertEqual(day["Opening units"] + day["Receipts"], day["Closing units"] + day["Fulfilled"])

    def test_discontinuous_days_fail(self):
        with self.assertRaises(ValueError):
            analyze({"sku": "x", "opening_units": 0, "days": [{"date": "2026-02-01", "demand": 1},
                                                               {"date": "2026-02-03", "demand": 1}]})
