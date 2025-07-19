-- Project Title: Streamlined Healthcare Management System (SHMS)
-- Team Name: Group 4
-- Group members:
-- 		Shaun Figueiro (sfiguei@iu.edu) (Team Lead)
-- 		Jayanth Budigini (jbudigin@iu.edu)
-- 		Syam Mungi (smungi@iu.edu)



-- Data Base Creation

-- CREATE DATABASE "PatientData"					-- jbudigin
--     WITH
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'en_US.UTF-8'
--     LC_CTYPE = 'en_US.UTF-8'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1
--     IS_TEMPLATE = False;


-- Rawdata / Master Table 

CREATE TABLE PatientRecords (					-- jbudigin
    Record_ID INT PRIMARY KEY,
    Patient_First_Name VARCHAR(25),
    Patient_Last_Name VARCHAR(25),
    Age INT,
    Gender CHAR(2),
    Height DECIMAL(5,2),
    Weight DECIMAL(5,2),
    Allergies VARCHAR(250),
    Address VARCHAR(250),
    Admission_Type VARCHAR(10),
    Visit_Date DATE,
    Doctor_Name VARCHAR(50),
    Doctor_Specialty VARCHAR(50),
    Doctor_Department VARCHAR(25),
    Symptoms VARCHAR(100),
    Tests VARCHAR(100),
    Diagnosis_Notes VARCHAR(300),
    Prescription VARCHAR(100),
    Payment_Amount DECIMAL(10,2),
    Payment_Method VARCHAR(20),
    Payment_Invoice_Number VARCHAR(50),
    Room_Number VARCHAR(10),
    Insurance_Provider VARCHAR(20)
);


copy PatientRecords FROM '/healthcare_data.csv' WITH (FORMAT CSV, HEADER);		-- smungi


-- Normalized schema creation

CREATE TABLE Patients (							-- smungi
    Patient_ID SERIAL PRIMARY KEY,
    Patient_First_Name VARCHAR(25) NOT NULL,
    Patient_Last_Name VARCHAR(25) NOT NULL,
    Age INT,
    Gender CHAR(2),
    Height DECIMAL(5,2),
    Weight DECIMAL(5,2),
    Allergies VARCHAR(250),
    Address VARCHAR(250) NOT NULL,
    Insurance_Provider VARCHAR(20),
    Unique(Patient_First_Name, Patient_Last_Name)
);


CREATE TABLE Doctors (							-- smungi
    Doctor_ID SERIAL PRIMARY KEY,
    Doctor_Name VARCHAR(50) NOT NULL Unique,
    Doctor_Specialty VARCHAR(50) NOT NULL,
    Doctor_Department VARCHAR(25) NOT NULL
);

CREATE TABLE Visits (							-- jbudigin
    Visit_ID SERIAL PRIMARY KEY,
    Patient_ID INT,
    Record_ID SERIAL,     --- change
    Admission_Type VARCHAR(10),
    Visit_Date DATE,
    Room_Number VARCHAR(10),
    Doctor_ID INT,
    Symptoms VARCHAR(100),
    Tests VARCHAR(100),
    Diagnosis_Notes VARCHAR(300),
    Prescription VARCHAR(100),
    Payment_Amount DECIMAL(10,2),
    Payment_Method VARCHAR(20),
    Payment_Invoice_Number VARCHAR(50),
    FOREIGN KEY (Patient_ID) REFERENCES Patients(Patient_ID),
    FOREIGN KEY (Doctor_ID) REFERENCES Doctors(Doctor_ID)
);



-- Data insertion

INSERT INTO Patients (Patient_First_Name, Patient_Last_Name, Age, Gender, Height, Weight, Allergies, Address, Insurance_Provider)		-- sfiguei
SELECT DISTINCT
    Patient_First_Name,
    Patient_Last_Name,
    Age,
    Gender,
    Height,
    Weight,
    Allergies,
    Address,
    Insurance_Provider

FROM PatientRecords;



INSERT INTO Doctors (Doctor_Name, Doctor_Specialty, Doctor_Department)				-- sfiguei
SELECT DISTINCT
    Doctor_Name,
    Doctor_Specialty,
    Doctor_Department
FROM PatientRecords;



-- sfiguei
INSERT INTO Visits (Patient_ID, Record_ID, Admission_Type, Visit_Date, Room_Number, Doctor_ID, Symptoms, Tests, Diagnosis_Notes, Prescription, Payment_Amount, Payment_Method, Payment_Invoice_Number)
SELECT
    p.Patient_ID,
    pr.Record_ID,
    pr.Admission_Type,
    pr.Visit_Date,
    pr.Room_Number,
    d.Doctor_ID,
    pr.Symptoms,
    pr.Tests,
    pr.Diagnosis_Notes,
    pr.Prescription,
    pr.Payment_Amount,
    pr.Payment_Method,
    pr.Payment_Invoice_Number
FROM PatientRecords pr
JOIN Patients p ON pr.Patient_First_Name = p.Patient_First_Name
    AND pr.Patient_Last_Name = p.Patient_Last_Name
JOIN Doctors d ON pr.Doctor_Name = d.Doctor_Name
    AND pr.Doctor_Specialty = d.Doctor_Specialty
    AND pr.Doctor_Department = d.Doctor_Department;


-- Table functionality check
select * from patients; 
select * from doctors;
select * from visits;


-- Patients along with their visit count.
SELECT p.Patient_ID, p.Patient_First_Name, p.Patient_Last_Name, p.Age, p.Gender, COUNT(v.Visit_ID) AS Visit_Count	-- sfiguei
FROM Patients p LEFT JOIN Visits v ON p.Patient_ID = v.Patient_ID
GROUP BY p.Patient_ID, p.Patient_First_Name, p.Patient_Last_Name, p.Age, p.Gender
Order By Visit_Count DESC;

-- Patients along with their total payment value.
SELECT p.Patient_ID, p.Patient_First_Name, p.Patient_Last_Name, SUM(v.Payment_Amount) AS Total_Payment, COUNT(v.Visit_ID) AS Visit_Count	-- jbudigin
FROM Patients p INNER JOIN Visits v ON p.Patient_ID = v.Patient_ID
GROUP BY p.Patient_ID, p.Patient_First_Name, p.Patient_Last_Name
HAVING SUM(v.Payment_Amount) > 500;

-- Doctors along with their total billing amount.
SELECT d.Doctor_ID, d.Doctor_Name, SUM(v.Payment_Amount) AS Total_Billing_Amount	-- smungi
FROM Doctors d INNER JOIN Visits v ON d.Doctor_ID = v.Doctor_ID
GROUP BY d.Doctor_ID, d.Doctor_Name
ORDER BY Total_Billing_Amount DESC;

-- Highest billing department of hospital
SELECT d.Doctor_Department, SUM(v.Payment_Amount) AS Total_Billing_Amount		--smungi
FROM Doctors d INNER JOIN Visits v ON d.Doctor_ID = v.Doctor_ID
GROUP BY d.Doctor_Department
ORDER BY Total_Billing_Amount DESC LIMIT 1;



