-- Create Database
CREATE DATABASE airline_db;
USE airline_db;

-- Tables in 3NF with PK/FK constraints
CREATE TABLE Airline (
    Name VARCHAR(50) PRIMARY KEY,
    Headquarters VARCHAR(100),
    Fleet_size INT,
    Contact_no VARCHAR(15)
);

CREATE TABLE Passenger (
    PNR VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(50),
    Age INT,
    Gender CHAR(1),
    Email VARCHAR(50),
    Phone_no VARCHAR(15),
    Address VARCHAR(100)
);

CREATE TABLE Flight (
    Flight_id VARCHAR(10) PRIMARY KEY,
    Scheduled_date DATE,
    Source VARCHAR(50),
    Destination VARCHAR(50),
    Departure_time TIME,
    Arrival_time TIME,
    Flight_status ENUM('Delayed', 'OnTime') DEFAULT 'OnTime',
    Capacity INT,
    Plane_type VARCHAR(50),
    Crew_count INT,
    Airline_name VARCHAR(50),
    FOREIGN KEY (Airline_name) REFERENCES Airline(Name) ON DELETE CASCADE
);

CREATE TABLE Ticket (
    Ticket_id VARCHAR(10) PRIMARY KEY,
    PNR VARCHAR(10),
    Flight_id VARCHAR(10),
    Seat_no VARCHAR(5),
    Booking_date DATE,
    Class ENUM('Economy', 'Business'),
    Price DECIMAL(10, 2),
    FOREIGN KEY (PNR) REFERENCES Passenger(PNR) ON DELETE CASCADE,
    FOREIGN KEY (Flight_id) REFERENCES Flight(Flight_id) ON DELETE CASCADE
);

CREATE TABLE Employees (
    Emp_id VARCHAR(10) PRIMARY KEY,
    Name VARCHAR(50),
    Role ENUM('Pilot', 'CoPilot', 'AirHostess', 'Marshall'),
    Email VARCHAR(50),
    Phone_no VARCHAR(15),
    Salary DECIMAL(10, 2),
    Airline_name VARCHAR(50),
    FOREIGN KEY (Airline_name) REFERENCES Airline(Name) ON DELETE CASCADE
);

CREATE TABLE Flight_crew (
    Flight_id VARCHAR(10),
    Emp_id VARCHAR(10),
    Role VARCHAR(20),
    Shift_hours INT,
    PRIMARY KEY (Flight_id, Emp_id),
    FOREIGN KEY (Flight_id) REFERENCES Flight(Flight_id) ON DELETE CASCADE,
    FOREIGN KEY (Emp_id) REFERENCES Employees(Emp_id) ON DELETE CASCADE
);

-- Users Table for Authentication
CREATE TABLE Users (
    Username VARCHAR(20) PRIMARY KEY,
    Password VARCHAR(20),
    Role ENUM('Admin', 'User') DEFAULT 'User'
);

-- Trigger: Update Crew_count in Flight table
DELIMITER //
CREATE TRIGGER update_crew_count
AFTER INSERT ON Flight_crew
FOR EACH ROW
BEGIN
    UPDATE Flight
    SET Crew_count = (SELECT COUNT(*) FROM Flight_crew WHERE Flight_id = NEW.Flight_id)
    WHERE Flight_id = NEW.Flight_id;
END//
DELIMITER ;

-- Procedure: Add Passenger and Ticket
DELIMITER //
CREATE PROCEDURE AddPassengerAndTicket(
    IN p_PNR VARCHAR(10), IN p_Name VARCHAR(50), IN p_Age INT, IN p_Gender CHAR(1),
    IN p_Email VARCHAR(50), IN p_Phone_no VARCHAR(15), IN p_Address VARCHAR(100),
    IN t_Ticket_id VARCHAR(10), IN t_Flight_id VARCHAR(10), IN t_Seat_no VARCHAR(5),
    IN t_Class ENUM('Economy', 'Business'), IN t_Price DECIMAL(10, 2)
)
BEGIN
    INSERT INTO Passenger (PNR, Name, Age, Gender, Email, Phone_no, Address)
    VALUES (p_PNR, p_Name, p_Age, p_Gender, p_Email, p_Phone_no, p_Address);
    
    INSERT INTO Ticket (Ticket_id, PNR, Flight_id, Seat_no, Booking_date, Class, Price)
    VALUES (t_Ticket_id, p_PNR, t_Flight_id, t_Seat_no, CURDATE(), t_Class, t_Price);
END//
DELIMITER ;

-- Sample Data
INSERT INTO Users VALUES ('admin', 'admin123', 'Admin'), ('user1', 'user123', 'User');
INSERT INTO Airline VALUES ('AirX', 'Mumbai', 50, '1234567890');