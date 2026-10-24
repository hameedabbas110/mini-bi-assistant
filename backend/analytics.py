
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "sales.db"


def run_query(sql, params=()):
    """Run a read-only analytics query."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


def total_revenue():
    sql = """
        SELECT
            ROUND(SUM(Quantity * Unit_price - Discount_amount), 2)
                AS total_revenue,
            COUNT(*) AS transaction_count
        FROM sales
        WHERE Status = 'Completed'
    """
    result = run_query(sql)[0]
    result["total_revenue"] = result["total_revenue"] or 0
    return result


def top_product():
    sql = """
        SELECT
            Product AS product,
            ROUND(SUM(Quantity * Unit_price - Discount_amount), 2)
                AS revenue
        FROM sales
        WHERE Status = 'Completed'
        GROUP BY Product
        ORDER BY revenue DESC, Product ASC
        LIMIT 1
    """
    result = run_query(sql)
    return result[0] if result else None


def monthly_revenue():
    sql = """
        SELECT
            strftime('%Y-%m', Order_date) AS month,
            ROUND(SUM(Quantity * Unit_price - Discount_amount), 2)
                AS revenue
        FROM sales
        WHERE Status = 'Completed'
        GROUP BY strftime('%Y-%m', Order_date)
        ORDER BY month
    """
    return run_query(sql)


def top_region():
    sql = """
        SELECT
            Region AS region,
            ROUND(SUM(Quantity * Unit_price - Discount_amount), 2)
                AS revenue
        FROM sales
        WHERE Status = 'Completed'
        GROUP BY Region
        ORDER BY revenue DESC, Region ASC
        LIMIT 1
    """
    result = run_query(sql)
    return result[0] if result else None


def compare_months(month1, month2):
    """Compare months supplied in YYYY-MM format."""
    for month in (month1, month2):
        if (
            len(month) != 7
            or month[4] != "-"
            or not month[:4].isdigit()
            or not month[5:].isdigit()
            or not 1 <= int(month[5:]) <= 12
            or int(month[:4]) < 1
        ):
            raise ValueError("Months must use YYYY-MM format.")

    sql = """
        SELECT
            COALESCE(
                ROUND(SUM(Quantity * Unit_price - Discount_amount), 2),
                0
            ) AS revenue
        FROM sales
        WHERE Status = 'Completed'
          AND strftime('%Y-%m', Order_date) = ?
    """

    revenue1 = run_query(sql, (month1,))[0]["revenue"]
    revenue2 = run_query(sql, (month2,))[0]["revenue"]

    revenue1 = revenue1 or 0
    revenue2 = revenue2 or 0
    change = round(revenue2 - revenue1, 2)

    percentage_change = (
        round(change / revenue1 * 100, 2)
        if revenue1 != 0
        else None
    )

    return {
        "month1": month1,
        "revenue1": revenue1,
        "month2": month2,
        "revenue2": revenue2,
        "change": change,
        "percentage_change": percentage_change,
    }


if __name__ == "__main__":
    print("Total revenue:", total_revenue())
    print("Top product:", top_product())
    print("Monthly revenue:", monthly_revenue())
    print("Top region:", top_region())
    print("January vs February:", compare_months("2026-01", "2026-02"))
