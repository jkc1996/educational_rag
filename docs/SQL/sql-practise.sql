-- tabel description like - colums. constaints, type etc

describe HR.EMPLOYEES;

-- SELECT QUERY --

select * from HR.COUNTRIES WHERE ROWNUM <= 5;

SELECT
    STREET_ADDRESS
FROM
    HR.LOCATIONS;

select * from hr.EMPLOYEES;
select distinct job_id, salary from HR.EMPLOYEES

------------------------------------------------------------- WHERE clause --------------------------------------------------------------------------------------------------------

-- IN BELOW QUERY WE WILL SEE THAT WITH DEPARTMENT ID 60, NO ONE HAS SALARY >10000
SELECT FIRST_NAME, SALARY FROM HR.EMPLOYEES WHERE DEPARTMENT_ID = 60;

-- MEANING OF BELOW QUERY - WHERE (SALARY > 10000 AND DEPARTMENT_ID = 90) OR (DEPARTMENT_ID = 60).. SO IN THIS AND CONDITION HAS PRECEDENCE.. BUT OR CONDION WILL ALSO GETS EXECUTED WHO HAVE DEPT ID = 60(BUT SALARY NOT > 10000 !!),
SELECT FIRST_NAME, DEPARTMENT_ID
FROM HR.EMPLOYEES WHERE SALARY > 10000
AND DEPARTMENT_ID = 90
OR DEPARTMENT_ID = 60;

-- CORRECT WAY OF IMPLEMENTING ABOVE QUERY... USE ()

SELECT FIRST_NAME, DEPARTMENT_ID
FROM HR.EMPLOYEES WHERE SALARY > 10000
AND (DEPARTMENT_ID = 90 OR DEPARTMENT_ID = 60);

-- MORE BETTER WAY - Instead of multiple ORs USE IN... ITS LIKE - (DEPARTMENT_ID = 90 OR DEPARTMENT_ID = 60 OR DEPARTMENT_ID = 100)

SELECT FIRST_NAME, DEPARTMENT_ID
FROM HR.EMPLOYEES
WHERE DEPARTMENT_ID IN (60, 90, 100) AND SALARY > 10000;

-- NOT IN EXAMPLE -- EXCLUDE ROWS WHO IS HAVING DEPARTMANT ID AS 60 OR 90

SELECT FIRST_NAME, DEPARTMENT_ID
FROM HR.EMPLOYEES
WHERE DEPARTMENT_ID NOT IN (60, 90);

-- BETWEEN STATEMENT (5000 AND 10000 ARE INCLUSIVE)

SELECT FIRST_NAME, SALARY
FROM HR.EMPLOYEES
WHERE SALARY BETWEEN 5000 AND 10000;

-- EMPLOYEE HIRED BETWEEN DATES (BETWEEN WITH DATE EXAMPLE)

SELECT FIRST_NAME, HIRE_DATE
FROM HR.EMPLOYEES
WHERE HIRE_DATE BETWEEN
      DATE '2013-01-01' AND DATE '2015-12-31';

-- LIKE OPERATOR - '%' means any number of charecter, '_' means exact one charecter


-- EX -1: NAME STARTS WITH 'A' ... case sensitive
SELECT FIRST_NAME
FROM HR.EMPLOYEES
WHERE FIRST_NAME LIKE 'A%';


-- ex-2: ends with 'o' ... case sensitive
SELECT FIRST_NAME
FROM HR.EMPLOYEES
WHERE FIRST_NAME LIKE '%o';

-- ex-3 starts with "A" and ends with 'a'
SELECT FIRST_NAME
FROM HR.EMPLOYEES
WHERE FIRST_NAME LIKE 'A%a';

-- ex-4 contains 'er' anywhere

SELECT FIRST_NAME
FROM HR.EMPLOYEES
WHERE FIRST_NAME LIKE '%er%';

-- ex-5 second charecter is 'e'


SELECT FIRST_NAME
FROM HR.EMPLOYEES
WHERE FIRST_NAME LIKE '_e%';

-- since it is case sencitive, lets, do trick (use upper and lower)

SELECT FIRST_NAME
FROM HR.EMPLOYEES
WHERE lower(FIRST_NAME) LIKE 'a%';

--- where with NULL cases - important

SELECT FIRST_NAME
FROM HR.EMPLOYEES
WHERE commission_pct is null;

-- commission pct is not null and first name start with char D
SELECT FIRST_NAME
FROM HR.EMPLOYEES
WHERE commission_pct is not null and FIRST_NAME like 'D%';

--------------------------------------------------------------------------

-- ORDER BY AND DISTINCT EXAMPLE... REMEMBER THIS EXECUTION ORDER - FROM, WHERE, SELECT, ORDER BY .... ORDER BY ALWAYS LAST

-- ASC IS DEFAULT.. NO NEED TO  MENTION IT

SELECT FIRST_NAME, SALARY
FROM HR.EMPLOYEES
ORDER BY SALARY;

-- HIGH TO LOW -- DESC

SELECT FIRST_NAME, SALARY
FROM HR.EMPLOYEES
ORDER BY SALARY DESC;

-- ORDER BY MULTIPLE COLUMN... FIRST ORDER BY DEPT THEN IN THAT ORDER BY SALARY HIGH TO LOW

SELECT FIRST_NAME, DEPARTMENT_ID, SALARY
FROM HR.EMPLOYEES
ORDER BY DEPARTMENT_ID ASC, SALARY DESC;

--- ORDER BY WITH WHERE

SELECT FIRST_NAME, SALARY
FROM HR.EMPLOYEES
WHERE DEPARTMENT_ID = 90
ORDER BY SALARY DESC;

---- DISTINCT EXAMPLE


-- NULL DEPARTMENT ID WILL ALSO BE IN THIS ONE.. SO JUST ADDED IS NOT NULL
SELECT DISTINCT DEPARTMENT_ID
FROM HR.EMPLOYEES WHERE DEPARTMENT_ID IS NOT NULL;


-- DISTINCT WITH MULTIPLE COLUMNS.. IT APPLIES TO THE COMBINATION OF BOTH

SELECT DISTINCT DEPARTMENT_ID, JOB_ID
FROM HR.EMPLOYEES;

-- DISTINCT + ORDER BY --- null will be part of this

SELECT DISTINCT DEPARTMENT_ID
FROM HR.EMPLOYEES
ORDER BY DEPARTMENT_ID;

--------------------------------------------------------------------------------------------------------------------

-- GROUP BY & Aggregate Functions

-- ex-1: Total number of employees

SELECT COUNT(*) AS TOTAL_EMPLOYEES
FROM HR.EMPLOYEES;

-- ex-2: Highest salary in company

SELECT MAX(SALARY) AS MAX_SALARY
FROM HR.EMPLOYEES;


-- EX-3: Average salary

SELECT AVG(SALARY)
FROM HR.EMPLOYEES;

-- DEPARTMENT WISE MAX SALARY

SELECT MAX(SALARY) AS MAX_SALARY, DEPARTMENT_ID
FROM HR.EMPLOYEES GROUP BY DEPARTMENT_ID;


-- EX-4: Correct usage: GROUP BY - Average salary per department
-- (HERE WE CAN NOT WRITE SELECT DEPARTMENT_ID, AVG(SALARY) WITHOUT GROUPBY AT THE END, BECAUSE DEPARTMENT_ID IS MANY VALUES AND AVG(SALARY) IS JUST ONE VALUE SO WE NEED TO GROUP HERE)

-- Golden Rule (MEMORIZE) - Any column in SELECT that is NOT an aggregate MUST appear in GROUP BY

SELECT DEPARTMENT_ID, AVG(SALARY)
FROM HR.EMPLOYEES
GROUP BY DEPARTMENT_ID;

-- EX-5: Multiple aggregates together - Salary stats per department 

SELECT
  DEPARTMENT_ID,
  COUNT(*) AS EMP_COUNT,
  MIN(SALARY) AS MIN_SAL,
  MAX(SALARY) AS MAX_SAL,
  AVG(SALARY) AS AVG_SAL
FROM HR.EMPLOYEES
GROUP BY DEPARTMENT_ID;

-- EX-6: GROUP BY with WHERE (very common) - Avg salary per department (only dept 60 & 90)

-- GOLDEN RULE - WHERE filters rows BEFORE grouping

SELECT DEPARTMENT_ID, AVG(SALARY)
FROM HR.EMPLOYEES
WHERE DEPARTMENT_ID IN (60, 90)
GROUP BY DEPARTMENT_ID;

-- EX-7: HAVING — filtering groups (IMPORTANT) HAVING filters groups, not rows

-- Departments with avg salary > 5000 AND ALSO OMIT DEPARTMENT WITH NULL

SELECT DEPARTMENT_ID, AVG(SALARY) FROM HR.EMPLOYEES WHERE DEPARTMENT_ID IS NOT NULL
GROUP BY DEPARTMENT_ID HAVING AVG(SALARY) > 5000;

-- EX-8: GROUP BY with multiple columns - Avg salary by department & job - Grouping happens on unique combinations

SELECT DEPARTMENT_ID, JOB_ID, AVG(SALARY)
FROM HR.EMPLOYEES
GROUP BY DEPARTMENT_ID, JOB_ID;

-- BELOW ONE WILL COUNT NON NULL VALUES

SELECT COUNT(COMMISSION_PCT) FROM HR.EMPLOYEES; 

-- REGARDING COUNT(*) - THIS WILL GIVE ALL ROWS COUNT

-- SUM, AVG → ignore NULL values

------------------------------------------------------------------------------------------------------------------------

SELECT FIRST_NAME, LAST_NAME, JOB_ID FROM HR.EMPLOYEES;

SELECT DEPARTMENT_ID, SUM(SALARY) FROM HR.EMPLOYEES GROUP BY DEPARTMENT_ID HAVING SUM(SALARY) > 50000;

-- Employees earning more than company average salary
SELECT FIRST_NAME, LAST_NAME, SALARY FROM HR.EMPLOYEES WHERE SALARY > (SELECT AVG(SALARY) FROM HR.EMPLOYEES);

-- let say in above query we want to display the department name too which is from departments table, then we need to join these tables

SELECT e.FIRST_NAME, e.LAST_NAME, e.SALARY, d.DEPARTMENT_NAME
FROM HR.EMPLOYEES e
LEFT JOIN HR.DEPARTMENTS d
ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
WHERE SALARY > (
    SELECT AVG(SALARY)
    FROM HR.EMPLOYEES
);

-- department wise count

SELECT DEPARTMENT_ID, COUNT (*) AS EMP_COUNT FROM HR.EMPLOYEES GROUP BY DEPARTMENT_ID;

-- very advance: Find employees whose salary is greater than the AVERAGE salary of THEIR OWN department

-- Correlated Subquery.: means.. The inner query depends on the outer query. It runs once per row of the outer query

-- Here:

-- e.DEPARTMENT_ID comes from the outer query

-- So the subquery cannot run independently

-- How Oracle executes this (step-by-step)

-- For each employee row:

-- Take employee’s DEPARTMENT_ID
-- Run subquery to compute AVG salary of that department
-- Compare:

-- Employee Salary > Department Average?


-- If TRUE → include employee

SELECT FIRST_NAME, LAST_NAME, SALARY, DEPARTMENT_ID
FROM HR.EMPLOYEES e
WHERE SALARY > (
    SELECT AVG(SALARY)
    FROM HR.EMPLOYEES
    WHERE DEPARTMENT_ID = e.DEPARTMENT_ID
);

-----------------------------------------------------------------------------------------------------------------------------

-- JOINS

-- 1. Inner joins
-- Example 1: Employees with department names

-- What happens

-- Employee with department → shown

-- Employee without department (NULL) → NOT shown

-- Default JOIN is INNER JOIN

SELECT
  e.FIRST_NAME,
  d.DEPARTMENT_NAME
FROM HR.EMPLOYEES e
INNER JOIN HR.DEPARTMENTS d
ON e.DEPARTMENT_ID = d.DEPARTMENT_ID;
--------------------------------------------------------
-- 2. Left join (importnant)

-- Why LEFT JOIN is important

-- Shows departments with zero employees

-- INNER JOIN would hide them

-- Interviewers LOVE this use case.

-- here it gurrenties that from left table(department) all the entries will list at least once.. so even if there is no employee in that department, first_name against that department will be shown as null.. e.g for payroll department there is no employee.. so payroll - employee name as null wil be shown

SELECT
  d.DEPARTMENT_NAME,
  e.FIRST_NAME
FROM HR.DEPARTMENTS d
LEFT JOIN HR.EMPLOYEES e
ON d.DEPARTMENT_ID = e.DEPARTMENT_ID;
--------------------------------------------------------

-- 3. RIGHT JOIN (LESS COMMON)
-- What it does

-- Returns ALL rows from RIGHT table
-- Matching rows from LEFT table
-- No match → LEFT side columns are NULL

-- here all the name from right table(employee.. all 107 names) will be listed.. and if they dont have department(left table) then it will show as null in department column

-- Example 3: All employees, even if department missing

-- its like B Right A = A left B

SELECT
  e.FIRST_NAME,
  d.DEPARTMENT_NAME
FROM HR.DEPARTMENTS d
RIGHT JOIN HR.EMPLOYEES e
ON d.DEPARTMENT_ID = e.DEPARTMENT_ID;

-- since B Right A = A left B, same result as above query will be listed for below query too..

SELECT
  e.FIRST_NAME,
  d.DEPARTMENT_NAME
FROM HR.EMPLOYEES e
LEFT JOIN HR.DEPARTMENTS d
ON d.DEPARTMENT_ID = e.DEPARTMENT_ID;

-----------------------------------------------------

-- JOIN with multiple tables (REAL LIFE) - Joins are evaluated left to right

-- Employee → Department → City

SELECT
  e.FIRST_NAME,
  d.DEPARTMENT_NAME,
  l.CITY
FROM HR.EMPLOYEES e
LEFT JOIN HR.DEPARTMENTS d
ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
LEFT JOIN HR.LOCATIONS l
ON d.LOCATION_ID = l.LOCATION_ID; 
---------------------------------------------------------------------

-- LEFT JOIN + WHERE filter

-- Show ALL departments, and for each department, below is the meaning of this query:

-- Show employees only if their salary is greater than 5000

-- If a department has no employees with salary > 5000, still show the department, but employee columns will be NULL

select e.first_name, e.salary, d.department_name FROM HR.DEPARTMENTS d
LEFT JOIN HR.EMPLOYEES e
ON d.DEPARTMENT_ID = e.DEPARTMENT_ID
AND e.SALARY > 5000;


-- What this query ACTUALLY does

-- Show ONLY departments that have employees with salary > 5000,
-- and show ONLY those employees.

--     Even though you wrote LEFT JOIN,
--     this query behaves like an INNER JOIN.

-- Why? (Key Reason)
-- The WHERE clause filters the FINAL result

-- Departments with:

--     No employees

--     Only employees with salary ≤ 5000

-- → will be REMOVED, because:

select e.first_name, e.salary, d.department_name FROM HR.DEPARTMENTS d
LEFT JOIN HR.EMPLOYEES e
ON d.DEPARTMENT_ID = e.DEPARTMENT_ID where e.SALARY > 5000;

-------------------------------------------------------------------

-- Self JOIN (advanced but asked) on same table

-- Employees and their managers

SELECT
  e.FIRST_NAME AS EMPLOYEE,
  m.FIRST_NAME AS MANAGER
FROM HR.EMPLOYEES e
LEFT JOIN HR.EMPLOYEES m
ON e.MANAGER_ID = m.EMPLOYEE_ID;

-------------------------------------------------------------

-- JOIN + GROUP BY (classic interview query)

-- in each department how many employees are there

SELECT
  d.DEPARTMENT_NAME,
  COUNT(e.EMPLOYEE_ID) AS EMP_COUNT
FROM HR.DEPARTMENTS d
LEFT JOIN HR.EMPLOYEES e
ON d.DEPARTMENT_ID = e.DEPARTMENT_ID
GROUP BY d.DEPARTMENT_NAME;

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- INSERT, UPDATE, DELETE & TRANSACTIONS (Oracle SQL)

-- Changes are NOT permanent until COMMIT

-- 1. INSERT — Adding new rows - Order of values must match table column order.

INSERT INTO HR.DEPARTMENTS VALUES (280, 'AI_RESEARCH', 205, 1700);

-- 2. INSERT with column names (BEST PRACTICE)

INSERT INTO HR.DEPARTMENTS (DEPARTMENT_ID, DEPARTMENT_NAME, MANAGER_ID, LOCATION_ID) VALUES (281, 'DATA_SCIENCE', 205, 1700);

INSERT INTO HR.EMPLOYEES
(EMPLOYEE_ID, FIRST_NAME, LAST_NAME, EMAIL, HIRE_DATE, JOB_ID, SALARY)
VALUES
(300, 'Jay', 'Patel', 'JPATEL', SYSDATE, 'IT_PROG', 9000);

-- 3. UPDATE — Modifying existing data (WHERE is critical)

UPDATE HR.EMPLOYEES
SET SALARY = 12000
WHERE EMPLOYEE_ID = 300;

-- Dangerous UPDATE: UPDATE HR.EMPLOYEES SET SALARY = 5000; (this will update all rows)

-- 4. Update multiple columns

UPDATE HR.EMPLOYEES
SET SALARY = SALARY + 1000,
    JOB_ID = 'SA_MAN'
WHERE DEPARTMENT_ID = 60;

-- 5. DELETE — Removing rows (Delete a specific employee) where condition is super important.. with DELETE WE CAN REVERT IT USING ROLLBACK;

DELETE FROM HR.EMPLOYEES
WHERE EMPLOYEE_ID = 300;

-- Dangerous DELETE - DELETE FROM HR.EMPLOYEES; never do this.. this will delete all the rows

-- 6. TRUNCATE - tHIS WILL ALSO DELETE ROWS, BUT WE CAN NOT REVERT THIS USING ROLLBACK;

TRUNCATE TABLE HR.EMPLOYEES;


-- BELOW ONE IS TRANSACTION FLOW IN ORACLE SQL 

-- INSERT / UPDATE / DELETE
-- ↓
-- COMMIT  → permanent (Save changes permanently)
-- ROLLBACK → undo (ROLLBACK TO - Last COMMIT Or SAVEPOINT)


-- SAVEPOINT (bonus topic)

SAVEPOINT before_update;

ROLLBACK TO before_update;

------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Creating Tables in Oracle SQL + Data Types

-- Basic Syntax: CREATE TABLE

-- CREATE TABLE table_name (
--     column_name DATA_TYPE [CONSTRAINTS],
--     column_name DATA_TYPE [CONSTRAINTS]
-- );

-- Simple Example Table:

-- CREATE TABLE EMP_SIMPLE (
--     EMP_ID NUMBER,
--     NAME VARCHAR2(100),
--     SALARY NUMBER(10,2),
--     HIRE_DATE DATE
-- );


-- | Data Type                          | Category        | Meaning                                       | Example Use Case        |
-- | ---------------------------------- | --------------- | --------------------------------------------- | ----------------------- |
-- | **NUMBER(p,s)**                    | Numeric         | Exact numeric value with precision & scale    | Salary, Price           |
-- | **INTEGER**                        | Numeric         | Whole number (subtype of NUMBER)              | Age, Count              |
-- | **FLOAT**                          | Numeric         | Approximate numeric (scientific/real numbers) | Scientific calculations |
-- | **BINARY_FLOAT**                   | Numeric         | Single-precision floating point               | Sensor values           |
-- | **BINARY_DOUBLE**                  | Numeric         | Double-precision floating point               | High-precision metrics  |
-- | **VARCHAR2(n)**                    | Text            | Variable-length text                          | Names, Emails           |
-- | **CHAR(n)**                        | Text            | Fixed-length text                             | Gender, Country code    |
-- | **CLOB**                           | Large Text      | Large character data                          | Articles, JSON          |
-- | **DATE**                           | Date/Time       | Date + Time (to seconds)                      | Hire date               |
-- | **TIMESTAMP**                      | Date/Time       | Date + Time with fractional seconds           | Logs                    |
-- | **TIMESTAMP WITH TIME ZONE**       | Date/Time       | Timestamp with timezone                       | Global systems          |
-- | **TIMESTAMP WITH LOCAL TIME ZONE** | Date/Time       | Normalized timezone timestamp                 | Distributed apps        |
-- | **INTERVAL YEAR TO MONTH**         | Date/Time       | Duration in years & months                    | Membership period       |
-- | **INTERVAL DAY TO SECOND**         | Date/Time       | Duration in days/hours/minutes                | Time differences        |
-- | **RAW(n)**                         | Binary          | Raw binary bytes                              | Encryption keys         |
-- | **BLOB**                           | Binary          | Large binary data                             | Images, Videos          |
-- | **ROWID**                          | Special         | Physical row address                          | Internal row reference  |
-- | **XMLTYPE**                        | XML             | XML structured data                           | XML documents           |
-- | **JSON (CLOB/VARCHAR2)**           | Semi-Structured | JSON storage                                  | API responses           |
-- | **BOOLEAN (PL/SQL only)**          | Logical         | True/False value                              | Flags in PL/SQL         |


CREATE TABLE EMP_ADVANCED (
    EMP_ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    FIRST_NAME VARCHAR2(50) NOT NULL,
    LAST_NAME VARCHAR2(50),
    EMAIL VARCHAR2(100) UNIQUE NOT NULL,
    PHONE VARCHAR2(20),
    SALARY NUMBER(10,2) CHECK (SALARY > 0),
    BONUS NUMBER(8,2),
    HIRE_DATE DATE DEFAULT SYSDATE,
    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
    IS_ACTIVE CHAR(1) CHECK (IS_ACTIVE IN ('Y','N')),
    PROFILE_TEXT CLOB,
    PROFILE_PIC BLOB,
    DEPARTMENT_ID NUMBER REFERENCES HR.DEPARTMENTS(DEPARTMENT_ID)
);


-- GENERATED ALWAYS AS IDENTITY: THIS WILL GENERATE AUTO INCREMENT ID

-- REFERENCES: FOR FOREIGN KEY REFRENCE

-- UNIQUE: VALUE SHOULD BE UNIQUE

-- THERE IS NO BOOLEAN TYPE IN ORACLE SQL, THAT IS WHY - IS_ACTIVE CHAR(1) CHECK (IS_ACTIVE IN ('Y','N'))


-- INSERT QUERY FOR ABOVE TABLE:

INSERT INTO EMP_ADVANCED (
    FIRST_NAME,
    LAST_NAME,
    EMAIL,
    PHONE,
    SALARY,
    BONUS,
    IS_ACTIVE,
    PROFILE_TEXT,
    DEPARTMENT_ID
) VALUES (
    'Jaykumar',
    'Chaudhary',
    'jaykumar.chaudhary@example.com',
    '+91-9876543210',
    95000.50,
    5000,
    'Y',
    'Senior Software Engineer with strong UI and SQL skills.',
    60
);

-- WHAT HAPPNED IN ABOVE QUERY ?

-- | Column        | Behavior                   |
-- | ------------- | -------------------------- |
-- | `EMP_ID`      | Auto-generated (IDENTITY)  |
-- | `HIRE_DATE`   | Defaults to `SYSDATE`      |
-- | `CREATED_AT`  | Defaults to `SYSTIMESTAMP` |
-- | `PROFILE_PIC` | NULL (not provided)        |

-- If you want to include DATE explicitly ?

INSERT INTO EMP_ADVANCED (
    FIRST_NAME, LAST_NAME, EMAIL, SALARY, HIRE_DATE, IS_ACTIVE, DEPARTMENT_ID
) VALUES (
    'Amit',
    'Sharma',
    'amit.sharma@example.com',
    80000,
    DATE '2024-01-15',
    'Y',
    90
);


--------------------------------------------------------------------------------------------------------------------------------------------------
-- some practice question

-- 1. fetch last/latest 5 hired emplyess by hire date 

SELECT *
FROM HR.EMPLOYEES
ORDER BY HIRE_DATE DESC
FETCH FIRST 5 ROWS ONLY;

-- 1. Last 5 rows by highest EMPLOYEE_ID

SELECT * FROM HR.EMPLOYEES ORDER BY EMPLOYEE_ID DESC
FETCH FIRST 5 ROWS ONLY; 


-- IN CASE OF MYSQL WE USE LIMIT 5;

-- 2. List employee first name, last name, salary, and hire date for employees who:
        -- Earn more than 8,000
        -- Were hired after 2005
        -- Sort the result by salary (highest first).

SELECT
    FIRST_NAME, LAST_NAME, SALARY, HIRE_DATE
FROM
    HR.EMPLOYEES
WHERE 
    (SALARY > 8000 AND HIRE_DATE >= DATE '2006-01-01')
ORDER BY
    SALARY DESC;


-- 3. Find distinct job IDs for employees whose:

    -- Email contains the letter 'a'

    -- And commission is NOT NULL


SELECT
    DISTINCT JOB_ID
FROM
    HR.EMPLOYEES
WHERE
    (lower(EMAIL) LIKE '%a%' and COMMISSION_PCT is not null);


-- 4. Show department ID and average salary for departments where:

    -- The average salary is greater than 9,000

    -- And the department has at least 3 employees

select DEPARTMENT_ID, AVG(SALARY), COUNT (*) AS EMP_COUNT FROM HR.EMPLOYEES GROUP BY DEPARTMENT_ID HAVING (AVG(SALARY) > 8000 AND COUNT(*) >= 3);

-- 5. Display employee name, salary, and department name

    -- Only for employees who:

    -- Work in departments located in location_id = 1700
 
    SELECT e.FIRST_NAME, e.SALARY, d.DEPARTMENT_NAME
    FROM HR.EMPLOYEES e
    JOIN HR.DEPARTMENTS d
    ON e.DEPARTMENT_ID = d.DEPARTMENT_ID
    WHERE d.LOCATION_ID = 1700;

-- 6. Show department name and total salary paid
    -- Only include departments where the total salary exceeds 50,000
    -- Make sure departments with no employees are still handled correctly.

    SELECT
        d.DEPARTMENT_ID,
        d.DEPARTMENT_NAME,
        sum(e.salary)
    FROM
        HR.DEPARTMENTS d
        left join hr.employees e
    on d.DEPARTMENT_ID = e.DEPARTMENT_ID
    group by d.DEPARTMENT_ID, d.DEPARTMENT_NAME
    having sum(e.salary) > 50000;





