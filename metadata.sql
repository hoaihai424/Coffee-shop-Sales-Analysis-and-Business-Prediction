------------------------------------------------------------
-- 1. DIMENSION TABLES
------------------------------------------------------------

/* 
   Bảng dim_department: Lưu phòng ban
   - departmentID: Khoá chính (SERIAL)
   - name, location, phone_number, email
*/
CREATE TABLE dim_department (
    departmentID       SERIAL PRIMARY KEY,
    name               VARCHAR(50) NOT NULL,
    location           VARCHAR(255) NOT NULL,
    phone_number       CHAR(12) NOT NULL 
        CHECK (phone_number ~ '^\d{3}-\d{4}-\d{3}$'),
    email              VARCHAR(255) NOT NULL 
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

/* 
   Bảng dim_employee: Lưu nhân viên
   - employeeID: PK (SERIAL)
   - departmentID: FK -> dim_department(departmentID)
   - name, position, start_date, salary, phone_number
*/
CREATE TABLE dim_employee (
    employeeID   SERIAL PRIMARY KEY,
    departmentID INT NOT NULL,
    name         VARCHAR(50) NOT NULL,
    position     VARCHAR(25),
    start_date   DATE,
    salary       INT CHECK (salary > 0),
    phone_number CHAR(12) NOT NULL
        CHECK (phone_number ~ '^\d{3}-\d{4}-\d{3}$'),
    CONSTRAINT fk_employee_department
        FOREIGN KEY (departmentID) 
        REFERENCES dim_department (departmentID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

/* 
   Bảng dim_customers: Lưu thông tin khách hàng
   - customerID: PK (SERIAL)
   - name, phone_number unique, gender(M/F), DOB, 
     customer_since, point, remaining_point
*/
CREATE TABLE dim_customers (
    customerID       SERIAL PRIMARY KEY,
    name             VARCHAR(255) NOT NULL,
    address          VARCHAR(255),
    phone_number     CHAR(12) NOT NULL UNIQUE
        CHECK (phone_number ~ '^\d{3}-\d{4}-\d{3}$'),
    dob              DATE,
    gender           CHAR(1) CHECK (gender IN ('M','F')),
    customer_since   DATE DEFAULT CURRENT_DATE,
    point            INT  DEFAULT 0 CHECK (point >= 0),
    remaining_point  INT  DEFAULT 0 CHECK (remaining_point >= 0)
);

/* 
   Bảng dim_gift: Lưu quà tặng
   - giftID: PK (SERIAL)
   - point: số điểm cần để đổi, state: available/unavailable/deleted
*/
CREATE TABLE dim_gift (
    giftID SERIAL PRIMARY KEY,
    name   VARCHAR(255) NOT NULL,
    point  INT NOT NULL CHECK (point > 0),
    state  VARCHAR(15) 
        CHECK (state IN ('available','unavailable','deleted'))
        DEFAULT 'available'
);

/* 
   Bảng dim_product: Lưu sản phẩm
   - productID: PK (SERIAL)
   - name, category, description, unit_price, discount, rating, state
*/
CREATE TABLE dim_product (
    productID    SERIAL PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    category     VARCHAR(50),
    description  VARCHAR(255),
    unit_price   DECIMAL(10,2) NOT NULL 
        CHECK (unit_price > 0),
    rating       DECIMAL(3,2) 
        CHECK (rating BETWEEN 0 AND 10)
        DEFAULT 0,
    discount     SMALLINT 
        CHECK (discount BETWEEN 0 AND 100)
        DEFAULT 0,
    state        VARCHAR(15)
        CHECK (state IN ('available','unavailable','deleted'))
        DEFAULT 'available'
);

/* 
   Bảng dim_date: Lưu ngày tháng
   - dateID: PK (INT) theo định dạng YYYYMMDD
   - day, week, month, quarter, year, isHoliday, holidayName, isWeekend
   => tuỳ logic, có thể cho NOT NULL
*/
CREATE TABLE dim_date (
    dateID       INT PRIMARY KEY,  
    day          INT NOT NULL,
    week         INT NOT NULL,
    month        INT NOT NULL,
    quarter      INT NOT NULL,
    year         INT NOT NULL,
    isHoliday    BOOLEAN DEFAULT FALSE,
    holidayName  VARCHAR(255),
    isWeekend    BOOLEAN DEFAULT FALSE
);

------------------------------------------------------------
-- 2. FACT TABLES
------------------------------------------------------------

/* 
   Fact_Gift_exchange: Lưu giao dịch đổi quà
   - giftID + customerID + dateID -> PK
*/
CREATE TABLE fact_gift_exchange (
    giftID     INT NOT NULL,
    customerID INT NOT NULL,
    dateID     INT NOT NULL,  
    quantity   INT NOT NULL 
        CHECK (quantity > 0),

    CONSTRAINT pk_gift_exchange
        PRIMARY KEY (giftID, customerID, dateID),

    CONSTRAINT fk_gift_exchange_gift
        FOREIGN KEY (giftID) REFERENCES dim_gift (giftID)
        ON UPDATE CASCADE,

    CONSTRAINT fk_gift_exchange_customer
        FOREIGN KEY (customerID) REFERENCES dim_customers (customerID)
        ON UPDATE CASCADE,

    CONSTRAINT fk_gift_exchange_date
        FOREIGN KEY (dateID) REFERENCES dim_date (dateID)
        ON UPDATE CASCADE
);

/* 
   Fact_Orders: Lưu thông tin đơn hàng
   - orderID: PK
   - customerID, employeeID, dateID -> FK
   - transactionTime: chỉ lưu giờ/phút/giây
   - total_quantity, total_price
*/
CREATE TABLE fact_orders (
    orderID       SERIAL PRIMARY KEY,
    customerID    INT,
    employeeID    INT,
    dateID        INT,
    transactionTime TIME NOT NULL DEFAULT CURRENT_TIME,
    total_quantity  INT 
        CHECK (total_quantity >= 0)
        DEFAULT 0,
    total_price    DECIMAL(10,2)
        CHECK (total_price >= 0)
        DEFAULT 0,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customerID)
        REFERENCES dim_customers (customerID)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_orders_employee
        FOREIGN KEY (employeeID)
        REFERENCES dim_employee (employeeID)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_orders_date
        FOREIGN KEY (dateID)
        REFERENCES dim_date (dateID)
        ON UPDATE CASCADE
);

/* 
   Fact_Order_details: Lưu chi tiết từng món trong đơn
   - orderID + productID -> PK
   - quantity, price, discount
*/
CREATE TABLE fact_order_details (
    orderID   INT NOT NULL,
    productID INT NOT NULL,
    quantity  INT NOT NULL CHECK (quantity > 0),
    price     DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    discount  SMALLINT 
        CHECK (discount BETWEEN 0 AND 100)
        DEFAULT 0,

    CONSTRAINT pk_order_details
        PRIMARY KEY (orderID, productID),

    CONSTRAINT fk_order_details_order
        FOREIGN KEY (orderID) 
        REFERENCES fact_orders (orderID)
        ON DELETE CASCADE,

    CONSTRAINT fk_order_details_product
        FOREIGN KEY (productID)
        REFERENCES dim_product (productID)
        ON UPDATE CASCADE
);

/* 
   Fact_Review: Lưu đánh giá sản phẩm
   - productID + customerID + dateID -> PK
   - score, comment
*/
CREATE TABLE fact_review (
    productID  INT NOT NULL,
    customerID INT NOT NULL,
    dateID     INT NOT NULL,
    score      DECIMAL(3,1) 
        CHECK (score BETWEEN 0 AND 10)
        DEFAULT 10,
    comment    VARCHAR(255),

    CONSTRAINT pk_review
        PRIMARY KEY (productID, customerID, dateID),

    CONSTRAINT fk_review_product
        FOREIGN KEY (productID) 
        REFERENCES dim_product (productID)
        ON DELETE CASCADE,

    CONSTRAINT fk_review_customer
        FOREIGN KEY (customerID) 
        REFERENCES dim_customers (customerID)
        ON DELETE CASCADE,

    CONSTRAINT fk_review_date
        FOREIGN KEY (dateID)
        REFERENCES dim_date (dateID)
        ON UPDATE CASCADE
);

-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;
-- SET default_transaction_read_only = OFF;