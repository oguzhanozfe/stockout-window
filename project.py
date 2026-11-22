"""Project daily stock under lost sales and start-of-day receipts."""
from datetime import date

TITLE = "Stockout Window"
DESCRIPTION = "Project daily inventory and identify consecutive shortage days under a demand and delivery schedule."
PROMPT = ("Identify the first unserved unit, quantify shortages and distinguish zero closing stock "
          "from unmet demand. Explain sensitivity to scheduled deliveries without assuming they will arrive.")


def analyze(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Input must be an object.")
    sku, stock, days = (data.get(k) for k in ("sku", "opening_units", "days"))
    if not isinstance(sku, str) or not sku.strip() or type(stock) is not int or stock < 0:
        raise ValueError("Provide a SKU and nonnegative integer opening_units.")
    if not isinstance(days, list) or not days:
        raise ValueError("Provide at least one day of demand and expected receipts.")
    rows, first, previous = [], None, None
    unmet_total, run, longest, windows = 0, 0, 0, 0
    for entry in days:
        if not isinstance(entry, dict) or not isinstance(entry.get("date"), str):
            raise ValueError("Each day must have a date in YYYY-MM-DD format.")
        current = date.fromisoformat(entry["date"])
        if current.isoformat() != entry["date"] or (previous and (current - previous).days != 1):
            raise ValueError("Use consecutive YYYY-MM-DD days in chronological order.")
        receipts, demand = entry.get("receipts", 0), entry.get("demand")
        if any(type(n) is not int or n < 0 for n in (receipts, demand)):
            raise ValueError("Receipts and demand must be nonnegative integer quantities.")
        available = stock + receipts
        served = min(available, demand)
        unmet = demand - served
        if unmet:
            if run == 0:
                windows += 1
            run += 1
            longest = max(longest, run)
            if first is None:
                first = entry["date"]
        else:
            run = 0
        rows.append({"Date": entry["date"], "Opening units": stock, "Receipts": receipts,
                     "Demand": demand, "Fulfilled": served, "Unmet demand": unmet,
                     "Closing units": available - served})
        stock = available - served
        unmet_total += unmet
        previous = current
    summary = (f"{sku} first leaves demand unfilled on {first}; the longest shortage lasts {longest} days."
               if first else f"{sku} fulfills all scheduled demand across {len(days)} days.")
    return {"summary": summary, "metrics": {"Shortage windows": windows, "Unmet units": unmet_total,
            "Longest shortage (days)": longest, "Final stock": stock}, "rows": rows}
