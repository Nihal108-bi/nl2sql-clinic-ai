# 📊 Test Results — NL2SQL Clinic Intelligence System

---

## Test Questions (20 Total)

Fill in each question by running it through the API and documenting the result.

| # | Question | Status | Notes |
|---|----------|--------|-------|
| 1 | How many patients do we have? | ✅/❌ |✅ |
| 2 | List all doctors and their specializations | ✅/❌ |✅ |
| 3 | Show me appointments for last month | ✅/❌ |✅ |
| 4 | Which doctor has the most appointments? | ✅/❌ |✅|
| 5 | What is the total revenue? | ✅/❌ | ✅|
| 6 | Show revenue by doctor | ✅/❌ |✅ |
| 7 | How many cancelled appointments last quarter? | ✅/❌ |✅ |
| 8 | Top 5 patients by spending | ✅/❌ |✅ |
| 9 | Which city has the most patients? | ✅/❌ |✅ |
| 10 | Show unpaid invoices | ✅/❌ |✅ |
| 11 | Average treatment cost by specialization | ✅/❌ |✅ |
| 12 | Show monthly appointment count for the past 6 months | ✅/❌ |✅ |
| 13 | What percentage of appointments are no-shows? | ✅/❌ |✅ |
| 14 | List patients who visited more than 3 times | ✅/❌ |✅ |
| 15 | Show revenue trend by month | ✅/❌ |❌ |
| 16 | Compare revenue between departments | ✅/❌ | |
| 17 | Show patient registration trend by month | ✅/❌ |✅ |
| 18 | Which treatment is most popular? | ✅/❌ |✅ |
| 19 | Show appointments by status for this month | ✅/❌ |✅ |
| 20 | List top 3 doctors by patient count | ✅/❌ |✅ |

---

## Detailed Test Results

### Q1 — How many patients do we have?

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
SELECT COUNT(*) AS total_patients FROM patients
```

**Expected:** Returns patient count  
**Result:** `200 patients`  
**Notes:** _Your observations here_

---

### Q2 — List all doctors and their specializations

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
SELECT name, specialization FROM doctors ORDER BY specialization
```

**Expected:** Returns doctor list with specializations  
**Result:** `15 rows returned`  
**Notes:**

---

### Q3 — Show me appointments for last month

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** Filters appointments by date range  
**Result:**  
**Notes:**

---

### Q4 — Which doctor has the most appointments?

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** Aggregation + ordering  
**Result:**  
**Notes:**

---

### Q5 — What is the total revenue?

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** SUM of invoice amounts  
**Result:**  
**Notes:**

---

### Q6 — Show revenue by doctor

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** JOIN + GROUP BY  
**Result:**  
**Notes:**

---

### Q7 — How many cancelled appointments last quarter?

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** Status filter + date range  
**Result:**  
**Notes:**

---

### Q8 — Top 5 patients by spending

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** JOIN + ORDER + LIMIT  
**Result:**  
**Notes:**

---

### Q9 — Which city has the most patients?

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** GROUP BY city + ORDER BY count  
**Result:**  
**Notes:**

---

### Q10 — Show unpaid invoices

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** Filters by invoice status  
**Result:**  
**Notes:**

---

### Q11 — Average treatment cost by specialization

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** JOIN + GROUP BY + AVG  
**Result:**  
**Notes:**

---

### Q12 — Show monthly appointment count for the past 6 months

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** Date grouping + aggregation  
**Result:**  
**Notes:**

---

### Q13 — What percentage of appointments are no-shows?

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** Conditional count + calculation  
**Result:**  
**Notes:**

---

### Q14 — List patients who visited more than 3 times

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** JOIN + GROUP BY + HAVING  
**Result:**  
**Notes:**

---

### Q15 — Show revenue trend by month

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** Date grouping + SUM + ORDER  
**Result:**  
**Notes:**

---

### Q16 — Compare revenue between departments

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** GROUP BY department + aggregation  
**Result:**  
**Notes:**

---

### Q17 — Show patient registration trend by month

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** Date grouping + COUNT  
**Result:**  
**Notes:**

---

### Q18 — Which treatment is most popular?

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** GROUP BY + ORDER BY count DESC  
**Result:**  
**Notes:**

---

### Q19 — Show appointments by status for this month

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** Filter by month + GROUP BY status  
**Result:**  
**Notes:**

---

### Q20 — List top 3 doctors by patient count

**Status:** ✅ Pass / ❌ Fail

**Generated SQL:**
```sql
-- Generated SQL here
```

**Expected:** JOIN + COUNT + ORDER + LIMIT 3  
**Result:**  
**Notes:**

---

## Summary & Notes

### What Worked Well
- _List your successes here_
- System successfully handles X types of queries

### Known Issues & Failures
- _Document any failures honestly_
- Question X failed because...

### Lessons Learned
- _What did you learn from this assignment?_

**Result:**  
**Notes:**

---

### Q6 — Show revenue by doctor

**Expected:** JOIN + GROUP BY  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q7 — How many cancelled appointments last quarter?

**Expected:** Status filter + date  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q8 — Top 5 patients by spending

**Expected:** JOIN + ORDER + LIMIT  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q9 — Average treatment cost by specialization

**Expected:** Multi-table JOIN + AVG  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q10 — Show monthly appointment count for the past 6 months

**Expected:** Date grouping  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q11 — Which city has the most patients?

**Expected:** GROUP BY + COUNT  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q12 — List patients who visited more than 3 times

**Expected:** HAVING clause  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q13 — Show unpaid invoices

**Expected:** Status filter  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q14 — What percentage of appointments are no-shows?

**Expected:** Percentage calculation  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q15 — Show the busiest day of the week for appointments

**Expected:** Date function  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q16 — Revenue trend by month

**Expected:** Time series  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q17 — Average appointment duration by doctor

**Expected:** AVG + GROUP BY  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q18 — List patients with overdue invoices

**Expected:** JOIN + filter  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q19 — Compare revenue between departments

**Expected:** JOIN + GROUP BY  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

### Q20 — Show patient registration trend by month

**Expected:** Date grouping  
**Status:** ✅ Pass / ❌ Fail  

**Generated SQL:**
```sql
-- paste SQL here
```

**Result:**  
**Notes:**

---

## Summary Table

| # | Question | Status | Notes |
|---|---------|--------|-------|
| 1 | How many patients do we have? | ✅ | |
| 2 | List all doctors and their specializations | ✅ | |
| 3 | Show me appointments for last month | | |
| 4 | Which doctor has the most appointments? | | |
| 5 | What is the total revenue? | | |
| 6 | Show revenue by doctor | | |
| 7 | How many cancelled appointments last quarter? | | |
| 8 | Top 5 patients by spending | | |
| 9 | Average treatment cost by specialization | | |
| 10 | Show monthly appointment count for the past 6 months | | |
| 11 | Which city has the most patients? | | |
| 12 | List patients who visited more than 3 times | | |
| 13 | Show unpaid invoices | | |
| 14 | What percentage of appointments are no-shows? | | |
| 15 | Show the busiest day of the week for appointments | | |
| 16 | Revenue trend by month | | |
| 17 | Average appointment duration by doctor | | |
| 18 | List patients with overdue invoices | | |
| 19 | Compare revenue between departments | | |
| 20 | Show patient registration trend by month | | |

**Final Score: __ / 20**

---

## Known Issues & Failures

_(Document any questions that failed and explain why.)_

**Example:**
- Q7 — "last quarter" date calculation: The LLM used a fixed date instead of a dynamic date function. Fixed by adding a seed memory example with `strftime`.

---

## Observations

- Memory seeding significantly improved accuracy on aggregation queries.
- Date-based questions required more context in the prompt.
- Complex multi-table JOINs (Q9, Q19) worked reliably after memory seeding.
