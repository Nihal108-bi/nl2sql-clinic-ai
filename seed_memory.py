"""
seed_memory.py
────────────────────────────────────────────────────────────────────────────────
Seeds the Vanna 2.0 Agent Memory with 15 high-quality question → SQL pairs.

This improves the agent's accuracy on common clinic queries from the first run.

Run:  python seed_memory.py
"""

import asyncio
from app.core.logger import logger

# ── 15 Seed Pairs ────────────────────────────────────────────────────────────
SEED_EXAMPLES = [
    (
        "How many patients do we have?",
        "SELECT COUNT(*) AS total_patients FROM patients",
    ),
    (
        "List all doctors and their specializations",
        "SELECT name, specialization, department FROM doctors ORDER BY specialization, name",
    ),
    (
        "What is the total revenue from all invoices?",
        "SELECT SUM(total_amount) AS total_revenue FROM invoices",
    ),
    (
        "Which doctor has the most appointments?",
        """SELECT d.name, d.specialization, COUNT(a.id) AS appointment_count
           FROM doctors d
           JOIN appointments a ON d.id = a.doctor_id
           GROUP BY d.id
           ORDER BY appointment_count DESC
           LIMIT 1""",
    ),
    (
        "Show the top 5 patients by total spending",
        """SELECT p.first_name, p.last_name, SUM(i.total_amount) AS total_spending
           FROM patients p
           JOIN invoices i ON p.id = i.patient_id
           GROUP BY p.id
           ORDER BY total_spending DESC
           LIMIT 5""",
    ),
    (
        "Show revenue by doctor",
        """SELECT d.name, d.specialization, SUM(t.cost) AS total_revenue
           FROM doctors d
           JOIN appointments a ON d.id = a.doctor_id
           JOIN treatments t ON a.id = t.appointment_id
           GROUP BY d.id
           ORDER BY total_revenue DESC""",
    ),
    (
        "How many cancelled appointments are there?",
        "SELECT COUNT(*) AS cancelled_count FROM appointments WHERE status = 'Cancelled'",
    ),
    (
        "Show unpaid invoices",
        """SELECT p.first_name, p.last_name, i.total_amount, i.paid_amount,
                  (i.total_amount - i.paid_amount) AS balance, i.status
           FROM invoices i
           JOIN patients p ON i.patient_id = p.id
           WHERE i.status IN ('Pending', 'Overdue')
           ORDER BY i.status, balance DESC""",
    ),
    (
        "Which city has the most patients?",
        """SELECT city, COUNT(*) AS patient_count
           FROM patients
           WHERE city IS NOT NULL
           GROUP BY city
           ORDER BY patient_count DESC
           LIMIT 1""",
    ),
    (
        "List patients who visited more than 3 times",
        """SELECT p.first_name, p.last_name, COUNT(a.id) AS visit_count
           FROM patients p
           JOIN appointments a ON p.id = a.patient_id
           GROUP BY p.id
           HAVING visit_count > 3
           ORDER BY visit_count DESC""",
    ),
    (
        "Average treatment cost by specialization",
        """SELECT d.specialization, ROUND(AVG(t.cost), 2) AS avg_cost
           FROM treatments t
           JOIN appointments a ON t.appointment_id = a.id
           JOIN doctors d ON a.doctor_id = d.id
           GROUP BY d.specialization
           ORDER BY avg_cost DESC""",
    ),
    (
        "Show monthly appointment count for the past 6 months",
        """SELECT strftime('%Y-%m', appointment_date) AS month,
                  COUNT(*) AS appointment_count
           FROM appointments
           WHERE appointment_date >= date('now', '-6 months')
           GROUP BY month
           ORDER BY month""",
    ),
    (
        "What percentage of appointments are no-shows?",
        """SELECT
             ROUND(
               100.0 * SUM(CASE WHEN status = 'No-Show' THEN 1 ELSE 0 END) / COUNT(*),
               2
             ) AS no_show_percentage
           FROM appointments""",
    ),
    (
        "Show the busiest day of the week for appointments",
        """SELECT
             CASE strftime('%w', appointment_date)
               WHEN '0' THEN 'Sunday'   WHEN '1' THEN 'Monday'
               WHEN '2' THEN 'Tuesday'  WHEN '3' THEN 'Wednesday'
               WHEN '4' THEN 'Thursday' WHEN '5' THEN 'Friday'
               ELSE 'Saturday'
             END AS day_of_week,
             COUNT(*) AS appointment_count
           FROM appointments
           GROUP BY strftime('%w', appointment_date)
           ORDER BY appointment_count DESC
           LIMIT 1""",
    ),
    (
        "Show patient registration trend by month",
        """SELECT strftime('%Y-%m', registered_date) AS month,
                  COUNT(*) AS new_patients
           FROM patients
           WHERE registered_date IS NOT NULL
           GROUP BY month
           ORDER BY month""",
    ),
]


async def seed_memory():
    """Write all seed examples into the Vanna 2.0 agent memory."""
    try:
        from app.core.vanna_setup import get_agent, get_memory, VANNA_AVAILABLE

        if not VANNA_AVAILABLE:
            logger.warning(
                "Vanna 2.0 is not installed — skipping memory seeding.\n"
                "Install it with:  pip install 'vanna[fastapi,gemini,sqlite]>=2.0.0'"
            )
            return

        # Initialise agent (also initialises memory)
        get_agent()
        memory = get_memory()

        if memory is None:
            logger.error("Could not access agent memory.")
            return

        logger.info(f"Seeding {len(SEED_EXAMPLES)} Q&A pairs into agent memory…")

        for i, (question, sql) in enumerate(SEED_EXAMPLES, 1):
            try:
                await memory.save_tool_usage(
                    question=question,
                    tool_name="run_sql",
                    args={"sql": sql},
                    context=None,
                    success=True,
                )
                logger.info(f"  [{i:02d}/{len(SEED_EXAMPLES)}] Seeded: {question[:60]}")
            except Exception as e:
                logger.warning(f"  [{i:02d}] Failed to seed: {question[:60]} — {e}")

        logger.info(f"✅ Memory seeding complete. {len(SEED_EXAMPLES)} pairs loaded.")

    except Exception as e:
        logger.error(f"Memory seeding failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_memory())
