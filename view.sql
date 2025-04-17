--
-- Quản lý doanh thu theo thời gian --> trả về doanh thu theo từng dateID (ngày, tháng, năm)
--
CREATE OR REPLACE VIEW v_finance_revenue_by_date AS
SELECT 
    d.dateID,
    d.year,
    d.month,
    d.day,
    -- Doanh thu (tổng) 
    SUM(o.total_price) AS total_revenue
FROM fact_orders o
JOIN dim_date d ON o.dateID = d.dateID
GROUP BY d.dateID, d.year, d.month, d.day
ORDER BY d.dateID;

select * from v_finance_revenue_by_date;

--
-- Quản lý doanh thu theo chi nhánh --> trả về các chi nhanh hiện có cùng với doanh thu tương ứng của từng chi nhánh 
--
CREATE OR REPLACE VIEW v_finance_revenue_by_department AS
SELECT 
    dep.departmentID,
    dep.name AS department_name,
    SUM(o.total_price) AS total_revenue,
    COUNT(o.orderID)    AS total_orders
FROM fact_orders o
JOIN dim_employee e ON o.employeeID = e.employeeID
JOIN dim_department dep ON e.departmentID = dep.departmentID
GROUP BY dep.departmentID, dep.name
ORDER BY total_revenue DESC;

select * from v_finance_revenue_by_department;

--
-- Quản lý hành vi khách hàng --> trả về lịch sử mua sắm của từng khách hàng theo từng thời điểm
--

CREATE OR REPLACE VIEW v_customer_behavior AS
SELECT 
    c.customerID,
    c.name           AS customer_name,
    p.productID,
    p.name           AS product_name,
    o.transactionTime,
    od.quantity,
	od.price
FROM fact_orders o
JOIN fact_order_details od ON o.orderID = od.orderID
JOIN dim_product p ON od.productID = p.productID
JOIN dim_customers c ON o.customerID = c.customerID
ORDER BY c.customerID, o.transactionTime
;

select * from v_customer_behavior where customerID = 1;


--
-- Quản lý khách hàng trung thành --> trả về dữ liệu khách hàng cùng với điểm tích lũy và số lần đổi quà
--

CREATE OR REPLACE VIEW v_loyal_customers AS
SELECT 
    c.customerID,
    c.name AS customer_name,
    c.phone_number,
    c.point         AS total_point,       -- all-time
    c.remaining_point AS remaining_point, 
    COUNT(g.giftID) AS total_gift_exchanged  -- nếu muốn
FROM dim_customers c
LEFT JOIN fact_gift_exchange g 
    ON c.customerID = g.customerID
GROUP BY c.customerID, c.name, c.phone_number, c.point, c.remaining_point
HAVING c.point > 100  -- ngưỡng điểm để được coi là khách hàng "trung thành"
ORDER BY c.point DESC;

--
-- Quản lý sản phẩm bán chạy --> trả về doanh thu và lượt bán của từng sản phẩm
--

CREATE OR REPLACE VIEW v_product_top_sellers AS
SELECT
    p.productID,
    p.name            AS product_name,
    p.category,
    SUM(od.quantity)  AS total_quantity,
    SUM(od.price)  AS total_revenue
FROM fact_order_details od
JOIN dim_product p ON od.productID = p.productID
GROUP BY p.productID, p.name, p.category
ORDER BY total_revenue DESC;

--
-- Quản lý chất lượng dịch vụ --> trả về điểm đánh giá và lượt đánh giá của từng sản phẩm
--
CREATE OR REPLACE VIEW v_service_quality AS


