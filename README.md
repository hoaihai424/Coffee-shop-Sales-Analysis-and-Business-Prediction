# Coffee Shop Data Generation Project

## Overview
This project generates synthetic data for a coffee shop chain management system. It creates realistic datasets for various aspects of coffee shop operations including customers, orders, products, employees, departments, and a loyalty reward system. The data is intended for use in data warehousing and decision support systems.

## Contributors
Phạm Lê Hoài Hải
Nguyễn Trường Giang
Phan Lương Hưng

## Generated Datasets

The project creates the following interconnected datasets:

1. **Customers**: Customer profiles with personal information and loyalty points
2. **Products**: Coffee and food items with pricing and descriptions
3. **Orders & Order Items**: Customer purchases with detailed order lines
4. **Employees**: Staff data organized by roles and departments
5. **Departments**: Different shop locations with contact information
6. **Gift Exchange**: Loyalty points redemption system
7. **Reviews**: Customer ratings and comments about products
8. **Calendar/Date**: Date dimension with holiday information

## Technical Features

- **Realistic Data Generation**: Uses Faker library to create authentic names, addresses, and other attributes
- **Data Relationships**: Maintains referential integrity between entities
- **Date Intelligence**: Incorporates real Vietnamese holidays via Google Calendar API
- **Business Logic**: Implements coffee shop-specific data patterns
  - Customer loyalty points system
  - Gift redemption with point deductions
  - Product rating system
  - Department and employee hierarchies

## Usage

### Prerequisites
```
pip install pandas numpy faker python-dotenv requests
```

### API Configuration
Create a `.env` file in the project root containing:
```
GOOGLE_CALENDAR_API_KEY="your_google_api_key"
```

### Running the Generator
```python
import extract

# Generate core entities
date_df = extract.gen_date()
department_df = extract.gen_department(3)
employee_df = extract.gen_employee(3)
customer_df = extract.gen_customer(1000)
product_df = extract.gen_product()
gift_df = extract.gen_gift()

# Generate transaction data
order_df = extract.gen_order_data(100000, len(customer_df), date_df['dateID'].tolist(), employee_df['employeeId'].tolist())
order_item_df = extract.gen_order_item(order_df, product_df, customer_df)
review_df = extract.gen_review(100, len(customer_df), product_df, date_df)
gift_exchange_df = extract.gen_gift_exchange(100, customer_df, date_df, gift_df)

# Export to CSV
product_df.to_csv("dataset/product.csv", index=False)
customer_df.to_csv("dataset/customer.csv", index=False)
date_df.to_csv("dataset/date.csv", index=False)
# Additional exports...
```

### Command-line Interface
The script also supports command-line arguments:
```bash
python extract.py <num_orders> <custom_message>
```

## Dataset Descriptions

### Customer
- `customerId`: Unique identifier
- `name`: Full name
- `phone_number`: Contact number
- `address`: Physical address
- `DOB`: Date of birth
- `customer_since`: Registration date
- `gender`: M/F
- `point`: Total loyalty points earned
- `remaining_point`: Points available for redemption

### Order & Order Items
- Order header with total price, date, customer info
- Line items with quantities, prices, discounts
- Auto-updates customer loyalty points

### Products
- Coffee and food items with categories
- Pricing information
- Description and availability status
- Average rating

## License
This project is licensed under the MIT License.