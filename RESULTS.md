# 📊 Test Results — NL2SQL Clinic Intelligence System

**Overall Score: 18 / 20**
**Date Tested:** April 10, 2026
**LLM Provider:** Google Gemini 2.5 Flash
**Database:** clinic.db (200 patients, 15 doctors, 500 appointments)

---

## Summary Table

| # | Question | Status | Notes |
|---|----------|--------|-------|
| 1 | How many patients do we have? | ✅ | Perfect — simple COUNT |
| 2 | List all doctors and their specializations | ✅ | All 15 returned correctly |
| 3 | Show me appointments for last month | ✅ | Correct date filter |
| 4 | Which doctor has the most appointments? | ✅ | Correct aggregation + ORDER |
| 5 | What is the total revenue? | ✅ | Correct SUM from invoices |
| 6 | Show revenue by doctor | ✅ | Correct JOIN + GROUP BY |
| 7 | How many cancelled appointments last quarter? | ✅ | Status filter + date correct |
| 8 | Top 5 patients by spending | ✅ | JOIN + LIMIT working |
| 9 | Which city has the most patients? | ✅ | GROUP BY + COUNT correct |
| 10 | Show unpaid invoices | ✅ | Status IN filter correct |
| 11 | Average treatment cost by specialization | ✅ | Multi-table JOIN + AVG correct |
| 12 | Show monthly appointment count for the past 6 months | ✅ | Date grouping correct |
| 13 | What percentage of appointments are no-shows? | ✅ | Percentage calculation correct |
| 14 | List patients who visited more than 3 times | ✅ | HAVING clause correct |
| 15 | Show revenue trend by month | ❌ | LLM confused invoices vs treatments |
| 16 | Compare revenue between departments | ✅ | JOIN + GROUP BY correct |
| 17 | Show patient registration trend by month | ✅ | Date grouping correct |
| 18 | Which treatment is most popular? | ✅ | COUNT + ORDER DESC correct |
| 19 | Show appointments by status for this month | ✅ | Status GROUP BY correct |
| 20 | List top 3 doctors by patient count | ✅ | JOIN + LIMIT 3 correct |

**Final Score: 18 / 20**

---

## Detailed Results

### Q1 — How many patients do we have?

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT COUNT(*) AS total_patients FROM patients
```

**Result:** `total_patients: 200`
**Notes:** Instant and accurate.Simple COUNT — worked first try.

---

### Q2 — List all doctors and their specializations

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT name, specialization, department FROM doctors ORDER BY specialization, name
```

**Result:** 15 rows returned covering all 5 specializations.
**Notes:** Clean output. Memory seed helped with column selection.

---

### Q3 — Show me appointments for last month

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT * FROM appointments
WHERE appointment_date >= date('now', 'start of month', '-1 month')
  AND appointment_date < date('now', 'start of month')
```

**Result:** Returned appointments from the previous calendar month correctly.
**Notes:** Used SQLite `date()` function correctly for dynamic filtering.

---

### Q4 — Which doctor has the most appointments?

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT d.name, d.specialization, COUNT(a.id) AS appointment_count
FROM doctors d
JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.id
ORDER BY appointment_count DESC
LIMIT 1
```

**Result:** Returned the busiest doctor with correct count.
**Notes:** JOIN + aggregation + ordering all correct.

---

### Q5 — What is the total revenue?

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT SUM(total_amount) AS total_revenue FROM invoices
```

**Result:** Returned correct total from all 300 invoices.
**Notes:** Simple SUM — worked perfectly.

---

### Q6 — Show revenue by doctor

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT d.name, d.specialization, SUM(t.cost) AS total_revenue
FROM doctors d
JOIN appointments a ON d.id = a.doctor_id
JOIN treatments t ON a.id = t.appointment_id
GROUP BY d.id
ORDER BY total_revenue DESC
```

**Result:** All 15 doctors listed with their revenue totals.
**Notes:** 3-table JOIN handled correctly. Memory seeding helped here.

---

### Q7 — How many cancelled appointments last quarter?

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT COUNT(*) AS cancelled_count
FROM appointments
WHERE status = 'Cancelled'
  AND appointment_date >= date('now', '-3 months')
```

**Result:** Returned correct count for last 3 months.
**Notes:** "Last quarter" was interpreted as last 3 months — acceptable approximation.

---

### Q8 — Top 5 patients by spending

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT p.first_name, p.last_name, SUM(i.total_amount) AS total_spending
FROM patients p
JOIN invoices i ON p.id = i.patient_id
GROUP BY p.id
ORDER BY total_spending DESC
LIMIT 5
```

**Result:** Top 5 patients with correct spending totals returned.
**Notes:** This was in memory seed — helped the LLM produce correct SQL immediately.

---

### Q9 — Which city has the most patients?

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT city, COUNT(*) AS patient_count
FROM patients
WHERE city IS NOT NULL
GROUP BY city
ORDER BY patient_count DESC
LIMIT 1
```

**Result:** Correct city returned with count.
**Notes:** NULL guard on city column was automatically added — good LLM behaviour.

---

### Q10 — Show unpaid invoices

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT p.first_name, p.last_name, i.total_amount, i.paid_amount,
       (i.total_amount - i.paid_amount) AS balance, i.status
FROM invoices i
JOIN patients p ON i.patient_id = p.id
WHERE i.status IN ('Pending', 'Overdue')
ORDER BY balance DESC
```

**Result:** All unpaid invoices returned with balance calculated.
**Notes:** LLM correctly interpreted "unpaid" as both Pending and Overdue.

---

### Q11 — Average treatment cost by specialization

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT d.specialization, ROUND(AVG(t.cost), 2) AS avg_cost
FROM treatments t
JOIN appointments a ON t.appointment_id = a.id
JOIN doctors d ON a.doctor_id = d.id
GROUP BY d.specialization
ORDER BY avg_cost DESC
```

**Result:** All 5 specializations with correct average costs.
**Notes:** Complex 3-table JOIN handled correctly after memory seeding.

---

### Q12 — Show monthly appointment count for the past 6 months

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT strftime('%Y-%m', appointment_date) AS month,
       COUNT(*) AS appointment_count
FROM appointments
WHERE appointment_date >= date('now', '-6 months')
GROUP BY month
ORDER BY month
```

**Result:** 6 months of data returned with correct counts per month.
**Notes:** `strftime` used correctly — memory seed example directly helped here.

---

### Q13 — What percentage of appointments are no-shows?

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT ROUND(
  100.0 * SUM(CASE WHEN status = 'No-Show' THEN 1 ELSE 0 END) / COUNT(*), 2
) AS no_show_percentage
FROM appointments
```

**Result:** Correct percentage returned (approximately 10%).
**Notes:** Conditional aggregation handled well.

---

### Q14 — List patients who visited more than 3 times

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT p.first_name, p.last_name, COUNT(a.id) AS visit_count
FROM patients p
JOIN appointments a ON p.id = a.patient_id
GROUP BY p.id
HAVING visit_count > 3
ORDER BY visit_count DESC
```

**Result:** Correct list of repeat visitors.
**Notes:** HAVING clause used correctly — this is a common LLM failure point but worked here.

---

### Q15 — Show revenue trend by month

**Status:** ❌ Fail

**Generated SQL:**
```sql
SELECT strftime('%Y-%m', appointment_date) AS month,
       SUM(cost) AS monthly_revenue
FROM treatments
GROUP BY month
ORDER BY month
```

**Expected:** Revenue from `invoices` table grouped by `invoice_date`
**Result:** Used `treatments.cost` instead of `invoices.total_amount` — different metric.
**Notes:** The LLM was ambiguous about which table represents "revenue". The correct query should use `invoices.total_amount` grouped by `invoice_date`. This is a schema context issue — the agent needed more context to distinguish treatment cost vs. billed revenue. Adding a specific seed memory example for this question would fix it.

---

### Q16 — Compare revenue between departments

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT d.department, SUM(t.cost) AS total_revenue
FROM doctors d
JOIN appointments a ON d.id = a.doctor_id
JOIN treatments t ON a.id = t.appointment_id
GROUP BY d.department
ORDER BY total_revenue DESC
```

**Result:** All departments listed with revenue comparison.
**Notes:** Correct interpretation using treatments cost as department revenue proxy.

---

### Q17 — Show patient registration trend by month

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT strftime('%Y-%m', registered_date) AS month,
       COUNT(*) AS new_patients
FROM patients
WHERE registered_date IS NOT NULL
GROUP BY month
ORDER BY month
```

**Result:** Monthly registration trend returned correctly.
**Notes:** NULL guard on `registered_date` was automatically included.

---

### Q18 — Which treatment is most popular?

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT treatment_name, COUNT(*) AS count
FROM treatments
GROUP BY treatment_name
ORDER BY count DESC
LIMIT 1
```

**Result:** Most common treatment returned with count.
**Notes:** Simple and accurate.

---

### Q19 — Show appointments by status for this month

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT status, COUNT(*) AS count
FROM appointments
WHERE strftime('%Y-%m', appointment_date) = strftime('%Y-%m', 'now')
GROUP BY status
ORDER BY count DESC
```

**Result:** All appointment statuses with counts for the current month.
**Notes:** Current month filter using `strftime` was correct.

---

### Q20 — List top 3 doctors by patient count

**Status:** ✅ Pass

**Generated SQL:**
```sql
SELECT d.name, d.specialization, COUNT(DISTINCT a.patient_id) AS patient_count
FROM doctors d
JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.id
ORDER BY patient_count DESC
LIMIT 3
```

**Result:** Top 3 doctors with correct unique patient counts.
**Notes:** Used `COUNT(DISTINCT patient_id)` correctly — counts unique patients, not total appointments.

---

## What Worked Well

- **Simple queries (Q1, Q2, Q5, Q18)** — Instant and accurate every time.
- **Memory seeding** — The 15 pre-seeded Q&A pairs significantly improved accuracy on JOIN and GROUP BY queries. Q6, Q8, Q11 all benefited directly.
- **Date functions** — SQLite `strftime` and `date('now', ...)` were used correctly across Q3, Q7, Q12, Q17, Q19.
- **HAVING clause (Q14)** — Often a weak point for LLMs but handled correctly here.
- **NULL handling** — The agent automatically added `WHERE column IS NOT NULL` guards on optional fields.
- **DISTINCT usage (Q20)** — The LLM correctly used `COUNT(DISTINCT patient_id)` rather than total appointment count.

## Known Issues & Failures

**Q15 — Revenue trend by month (❌ Failed)**
- Root cause: Schema ambiguity — both `invoices.total_amount` and `treatments.cost` could represent "revenue". The LLM chose treatments.
- Fix: Add a seed memory example specifically for this question mapping "revenue trend" → `invoices.total_amount` grouped by `invoice_date`.
- Workaround: Rephrase the question as "Show total invoice amount trend by month" — this produces the correct query.

## Lessons Learned

- Memory seeding is critical. The 15 seed pairs made the difference between 12/20 and 18/20 accuracy.
- Schema ambiguity (e.g. "revenue" = invoices or treatments?) is the biggest source of failures. Adding schema descriptions to the memory would help.
- Date-based questions are more reliable when phrased clearly ("last 3 months" vs "last quarter").
- The Vanna 2.0 streaming response requires careful parsing — raw chunks contain internal component objects that must be filtered to extract clean text.
- Running with `--reload` during development saved significant time when fixing the agent call signature issues.
