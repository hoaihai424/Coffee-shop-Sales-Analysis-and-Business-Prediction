import sys
from extract import *
# python gen.py <num_departments> <num_customers> <num_gift_exchanges> <num_reviews>

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python gen.py <num_departments> <num_customers> <num_gift_exchanges> <num_reviews>")
        sys.exit(1)

    # get args
    args = sys.argv[1:]

    # load args
    num_departments = args[0]
    num_customers = args[1]
    num_gift_exchanges = args[2]
    num_gift_exchanges = args[3]
    num_reviews = args[4]

    # generate data
    product_df = gen_product()
    gift_df = gen_gift()
    date_df = gen_date()

    department_df = gen_department(3)
    employee_df = gen_employee(3)
    customer_df = gen_customer(1000000)

    review_df = gen_review(1000000, len(customer_df), product_df, date_df)
    order_df = gen_order_data(10000000, len(customer_df), date_df, employee_df)
    order_item_df = gen_order_item(order_df, product_df, customer_df)
    gift_exchange_df = gen_gift_exchange(10000, customer_df, date_df, gift_df)
    