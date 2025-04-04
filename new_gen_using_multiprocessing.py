import pandas as pd
import numpy as np
import random, os, requests
from faker import Faker
from dotenv import load_dotenv
from datetime import datetime, time
from collections import defaultdict
import math
import multiprocessing as mp
from decimal import Decimal, ROUND_HALF_UP

fake = Faker()
load_dotenv()  # Để lấy GOOGLE_API_KEY từ file .env (nếu có)

GOOGLE_API_KEY = os.getenv("GOOGLE_CALENDAR_API_KEY")


# --------------------------------------------------
# 0. Hàm sinh phone number format XXX-XXXX-XXX
# --------------------------------------------------
def gen_formatted_phone_number() -> str:
    part1 = random.randint(0, 999)
    part2 = random.randint(0, 9999)
    part3 = random.randint(0, 999)
    return f"{part1:03d}-{part2:04d}-{part3:03d}"


# --------------------------------------------------
# 1. Lấy danh sách holidays từ Google Calendar API
# --------------------------------------------------
def get_holidays_from_google(start_year=2022, end_year=2024):
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables!")

    url = (
        "https://www.googleapis.com/calendar/v3/calendars/"
        "en.vietnamese%23holiday@group.v.calendar.google.com/events"
    )
    time_min = f"{start_year}-01-01T00:00:00Z"
    time_max = f"{end_year+1}-01-01T23:59:59Z"

    params = {
        "key": GOOGLE_API_KEY,
        "timeMin": time_min,
        "timeMax": time_max,
        "singleEvents": True,
        "orderBy": "startTime",
        "fields": "items(start,end,summary)",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    holidays = []
    for item in data.get("items", []):
        start_date = item["start"].get("date")
        summary = item["summary"]
        if start_date and summary:
            holidays.append((start_date, summary))

    return holidays


# --------------------------------------------------
# 2. Sinh bảng Date
# --------------------------------------------------
def convert_date_to_dateId(dt: datetime) -> str:
    return dt.strftime("%Y%m%d")


def convert_date_to_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def gen_date_with_holidays(start="2022-01-01", end="2024-12-31"):
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)

    start_y = start_date.year
    end_y = end_date.year
    holiday_data = get_holidays_from_google(start_y, end_y)
    holiday_map = {hd[0]: hd[1] for hd in holiday_data}

    date_range = pd.date_range(start=start_date, end=end_date)
    rows = []

    for dt in date_range:
        date_str = convert_date_to_str(dt)
        dateID = convert_date_to_dateId(dt)
        day_ = dt.day
        week_ = dt.isocalendar()[1]
        month_ = dt.month
        quarter_ = (dt.month - 1) // 3 + 1
        year_ = dt.year
        isWeekend = 1 if dt.weekday() >= 5 else 0

        if date_str in holiday_map:
            isHoliday = 1
            holidayName = holiday_map[date_str]
        else:
            isHoliday = 0
            holidayName = ""

        rows.append(
            (
                dateID,
                day_,
                week_,
                month_,
                quarter_,
                year_,
                isHoliday,
                isWeekend,
                holidayName,
            )
        )

    df = pd.DataFrame(
        rows,
        columns=[
            "dateID",
            "day",
            "week",
            "month",
            "quarter",
            "year",
            "isHoliday",
            "isWeekend",
            "holidayName",
        ],
    )
    return df


# --------------------------------------------------
# 3. Sinh bảng Department
# --------------------------------------------------
def gen_department(num_departments=3):
    data = []
    for i in range(1, num_departments + 1):
        data.append(
            (
                i,
                fake.company(),
                fake.city(),
                gen_formatted_phone_number(),
                fake.company_email(),
            )
        )
    df = pd.DataFrame(
        data, columns=["departmentId", "name", "location", "phone_number", "email"]
    )
    return df


# --------------------------------------------------
# 4. Sinh bảng Employee
# --------------------------------------------------
def gen_employee(department_df, min_emp=30, max_emp=50):
    rows = []
    emp_id = 1
    for _, dept_row in department_df.iterrows():
        dept_id = dept_row["departmentId"]
        n_emp = random.randint(min_emp, max_emp)
        for _ in range(n_emp):
            name_ = fake.name()
            hire_date_ = fake.date_between(start_date="-5y", end_date="today")
            position_ = random.choice(["Manager", "Barista", "Cashier", "Waiter"])
            if position_ == "Manager":
                salary_ = 5000000
            elif position_ == "Barista":
                salary_ = 3000000
            elif position_ == "Cashier":
                salary_ = 2500000
            else:
                salary_ = 2000000
            phone_ = gen_formatted_phone_number()
            rows.append(
                (emp_id, name_, dept_id, hire_date_, salary_, position_, phone_)
            )
            emp_id += 1
    df = pd.DataFrame(
        rows,
        columns=[
            "employeeId",
            "name",
            "departmentId",
            "hireDate",
            "salary",
            "position",
            "phone_number",
        ],
    )
    return df


# --------------------------------------------------
# 5. Sinh bảng Gift
# --------------------------------------------------
def gen_gift():
    gift_list = [
        "Keychain with store logo",
        "Document clip engraved with logo",
        "Handmade wooden coaster",
        "Luxury pen",
        "Branded helmet",
        "Tote bag with logo",
        "Branded t-shirt",
        "Scarf or winter beanie",
        "Daily planner board",
        "Fabric-covered notebook",
        "Luxury leather notebook",
        "Vintage wooden photo frame",
        "Coffee-style desk calendar",
        "Relaxing scented candle",
        "Small decorative menu board",
        "Neck pillow with cafe voucher",
        "Unique coffee tablecloth",
        "Decorative hanging plant bag",
        "Classic style table runner",
        "Branded back cushion",
        "Spill-proof coffee cup",
        "Limited edition sample drink set",
        "Phone case with logo",
        "Premium towel",
        "Office supplies set with logo",
        "Shockproof laptop bag",
        "Wooden lid jars for coffee beans",
        "Cafe-style desk lamp",
        "Specialty coffee gift set from various regions",
        "Glass coffee cup set",
        "Premium ceramic mug",
        "Neck pillow with cafe voucher",
        "Hourglass coffee timer",
        "Durable thermal bottle",
        "Handcrafted coffee filter",
        "Mini coffee maker",
        "Fashion handbag",
        "Cafe-style wall clock",
        "Premium coffee bean gift set",
        "Handheld coffee brewer",
    ]
    gift_id = range(1, len(gift_list) + 1)
    gift_point = [i * 10 for i in gift_id]
    df = pd.DataFrame(
        {
            "giftId": gift_id,
            "name": gift_list,
            "state": ["available"] * len(gift_list),
            "point": gift_point,
        }
    )
    return df


# --------------------------------------------------
# 6. Đọc bảng Product
# --------------------------------------------------
def gen_product_from_csv(csv_path: str):
    df_raw = pd.read_csv(csv_path)
    df = pd.DataFrame(
        {
            "productId": df_raw["product_id"],
            "name": df_raw["product_name"],
            "category": df_raw["product_category"],
            "description": df_raw["product_description"],
            "unit_price": df_raw["unit_price"],
            "state": df_raw["state"],
        }
    )
    df["rating"] = 0.0
    return df


# --------------------------------------------------
# 7. Sinh bảng Customer (phone unique format XXX-XXXX-XXX)
# --------------------------------------------------
def gen_customer(num_customers=100_000):
    used_phones = set()
    rows = []
    for i in range(1, num_customers + 1):
        name_ = fake.name()
        phone_ = gen_formatted_phone_number()
        while phone_ in used_phones:
            phone_ = gen_formatted_phone_number()
        used_phones.add(phone_)

        address_ = fake.address().replace("\n", " ")
        dob_ = fake.date_of_birth(minimum_age=16, maximum_age=80)
        c_since = fake.date_between(start_date="-5y", end_date="today")
        gender_ = random.choice(["M", "F"])
        # point=0 (all-time), remaining=0 ban đầu
        rows.append((i, name_, phone_, address_, dob_, c_since, gender_, 0, 0))
    df = pd.DataFrame(
        rows,
        columns=[
            "customerId",
            "name",
            "phone_number",
            "address",
            "DOB",
            "customer_since",
            "gender",
            "point",
            "remaining_point",
        ],
    )
    return df


# --------------------------------------------------
# 8. MULTIPROCESSING: Tạo Orders & OrderItems
# --------------------------------------------------
def _worker_generate_orders(
    proc_id: int,
    start_id: int,
    end_id: int,
    chunk_size: int,
    product_df: pd.DataFrame,
    date_df: pd.DataFrame,
    employee_df: pd.DataFrame,
    cust_id_list: list,
    output_dir: str,
):
    from math import ceil
    import numpy as np

    date_ids = date_df["dateID"].tolist()
    emp_ids = employee_df["employeeId"].tolist()
    num_products = len(product_df)

    local_points_map = defaultdict(int)
    total_orders = end_id - start_id + 1
    n_chunks = ceil(total_orders / chunk_size)

    order_path = os.path.join(output_dir, f"order_part_{proc_id}.csv")
    order_item_path = os.path.join(output_dir, f"order_item_part_{proc_id}.csv")

    # Ghi header 1 lần
    with open(order_path, "w", encoding="utf-8") as f:
        f.write(
            "orderId,customerId,orderDate,orderTime,total_quantity,total_price,employeeId\n"
        )
    with open(order_item_path, "w", encoding="utf-8") as f:
        f.write("orderId,productId,quantity,price,discount\n")

    current_order_id = start_id

    for ck in range(n_chunks):
        cstart = current_order_id
        cend = min(cstart + chunk_size - 1, end_id)
        sz = cend - cstart + 1
        if sz <= 0:
            break

        order_ids = range(cstart, cend + 1)
        random_cust = np.random.choice(cust_id_list, size=sz)
        random_date = np.random.choice(date_ids, size=sz)
        random_time = [
            time(
                random.randint(6, 21), random.randint(0, 59), random.randint(0, 59)
            ).strftime("%H:%M:%S")
            for _ in range(sz)
        ]
        random_emp = np.random.choice(emp_ids, size=sz)

        orders_df = pd.DataFrame(
            {
                "orderId": order_ids,
                "customerId": random_cust,
                "orderDate": random_date,
                "orderTime": random_time,
                "total_quantity": [0] * sz,
                "total_price": [0.0] * sz,
                "employeeId": random_emp,
            }
        )

        order_item_rows = []
        for i, row in orders_df.iterrows():
            o_id = row["orderId"]
            line_count = random.randint(1, 10)
            product_ids = random.sample(range(1, num_products + 1), k=line_count)
            quantities = np.random.randint(1, 6, size=line_count)

            tot_price_dec = Decimal("0.00")
            tot_qty = 0
            for pid, qty in zip(product_ids, quantities):
                unit_price = product_df.iloc[pid - 1]["unit_price"]
                unit_price_dec = Decimal(str(unit_price))
                qty_dec = Decimal(str(qty))

                line_price_dec = (unit_price_dec * qty_dec).quantize(
                    Decimal("0.00"), rounding=ROUND_HALF_UP
                )
                tot_price_dec += line_price_dec
                tot_qty += qty

                line_price = float(line_price_dec)
                order_item_rows.append((o_id, pid, qty, line_price, 0))

            orders_df.at[i, "total_quantity"] = tot_qty
            orders_df.at[i, "total_price"] = float(tot_price_dec)

        # Tính điểm
        for i, row in orders_df.iterrows():
            cid = row["customerId"]
            earned_points = int(row["total_price"] // 5)
            local_points_map[cid] += earned_points

        # Ghi CSV
        orders_df.to_csv(order_path, mode="a", header=False, index=False)
        order_item_df = pd.DataFrame(
            order_item_rows,
            columns=["orderId", "productId", "quantity", "price", "discount"],
        )
        order_item_df.to_csv(order_item_path, mode="a", header=False, index=False)

        current_order_id = cend + 1

    print(f"Process {proc_id} done: {total_orders} orders.")
    return dict(local_points_map)


def parallel_order_generation(
    total_orders: int,
    product_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    date_df: pd.DataFrame,
    employee_df: pd.DataFrame,
    n_process: int,
    chunk_size: int,
    output_dir: str,
):
    pool = mp.Pool(n_process)
    per_process = total_orders // n_process
    tasks = []
    start_id = 1
    cust_id_list = customer_df["customerId"].tolist()

    for pid in range(n_process):
        if pid < n_process - 1:
            end_id = start_id + per_process - 1
        else:
            end_id = total_orders
        tasks.append(
            (
                pid,
                start_id,
                end_id,
                chunk_size,
                product_df,
                date_df,
                employee_df,
                cust_id_list,
                output_dir,
            )
        )
        start_id = end_id + 1

    results = []
    for t in tasks:
        r = pool.apply_async(_worker_generate_orders, args=t)
        results.append(r)

    pool.close()
    pool.join()

    # Gộp points
    global_points_map = defaultdict(int)
    for r in results:
        local_dict = r.get()
        for cid, pts in local_dict.items():
            global_points_map[cid] += pts

    extra_points_df = pd.DataFrame(
        list(global_points_map.items()), columns=["customerId", "extra_point"]
    )

    # Merge
    customer_df = customer_df.merge(extra_points_df, on="customerId", how="left")
    customer_df["extra_point"] = customer_df["extra_point"].fillna(0)

    # Cộng vào point (all-time) và remaining_point (điểm khả dụng)
    customer_df["point"] = customer_df["point"] + customer_df["extra_point"]
    customer_df["remaining_point"] = (
        customer_df["remaining_point"] + customer_df["extra_point"]
    )

    # ÉP VỀ int: đảm bảo không có .0
    customer_df["point"] = customer_df["point"].astype(int)
    customer_df["remaining_point"] = customer_df["remaining_point"].astype(int)

    customer_df.drop(columns=["extra_point"], inplace=True)
    return customer_df


# --------------------------------------------------
# 9. Hàm gen_review
# --------------------------------------------------
def gen_review(num_reviews, num_customers, product_df, date_df):
    positive_comments = [
        "It was absolutely delicious and full of flavor!",
        "The presentation of the dish was stunning.",
        "It were refreshing and perfectly balanced.",
        "The service was excellent, and the staff was very friendly.",
        "It was heavenly and melted in my mouth.",
        "The portion sizes were generous and satisfying.",
        "The ambiance of the restaurant was cozy and inviting.",
        "The ingredients tasted fresh and high-quality.",
        "It was rich and aromatic, just perfect.",
        "The menu had a great variety of options to choose from.",
        "It was cooked to perfection, al dente!",
        "It was tender and cooked exactly as requested.",
        "It were creative and expertly crafted.",
        "It was warm and comforting, just what I needed.",
        "It was fresh and beautifully presented.",
        "The flavors were well-balanced and complemented each other.",
        "The staff went above and beyond to make our experience special.",
        "It was served hot and on time.",
        "The restaurant had a great vibe and atmosphere.",
        "It was juicy and packed with flavor.",
        "The service was quick and efficient.",
        "It was creamy and had a rich flavor.",
        "It was worth every penny, great value for money.",
        "The restaurant was clean and well-maintained.",
        "The staff was knowledgeable about the menu and made great recommendations.",
        "The flavors were authentic and reminded me of home.",
        "It were served at the perfect temperature.",
        "The restaurant had a unique and creative menu.",
        "The service was attentive without being intrusive.",
        "It was flavorful and left me wanting more.",
        "The ambiance was perfect for a romantic dinner.",
        "It was the best thing I’ve had in a long time.",
        "The staff was polite and made us feel welcome.",
        "The restaurant exceeded my expectations in every way.",
    ]
    neutral_comments = [
        "It was decent, but nothing extraordinary.",
        "The service was okay, but it could have been faster.",
        "It were fine, but a bit too sweet for my taste.",
        "The ambiance was nice, but the music was a bit loud.",
        "It was fine, but I’ve had better elsewhere.",
        "The menu had a decent variety, but nothing stood out.",
        "The coffee was okay, but not as strong as I like it.",
        "It was served warm, but not hot.",
        "It was good, but slightly overcooked.",
        "It was fine, but it could have been more tender.",
        "It were okay, but not very creative.",
        "It was fine, but it wasn’t very fresh.",
        "The flavors were okay, but they didn’t wow me.",
        "The staff was polite, but not very attentive.",
        "It was served on time, but the presentation was lacking.",
        "The restaurant was nice, but it felt a bit crowded.",
        "It was fine, but the dressing was too heavy.",
        "The service was fine, but it could have been more friendly.",
        "It was good, but it felt a bit overpriced.",
        "The chef did a decent job, but the dishes lacked creativity.",
        "The appetizers were fine, but they were a bit bland.",
        "The restaurant was clean, but the decor was outdated.",
        "The staff was okay, but they seemed a bit rushed.",
        "The flavors were fine, but they didn’t feel authentic.",
        "It were fine, but they took too long to arrive.",
        "It was cooked well, but it lacked seasoning.",
        "The restaurant had a decent menu, but it wasn’t very unique.",
        "The service was fine, but it wasn’t very memorable.",
        "It was okay, but it didn’t leave a lasting impression.",
        "The ambiance was fine, but it felt a bit generic.",
    ]
    negative_comments = [
        "It was bland and lacked flavor.",
        "The service was slow and unprofessional.",
        "It were watered down and disappointing.",
        "The ambiance was ruined by loud noise and poor lighting.",
        "The portion sizes were too small for the price.",
        "It was cold and unappetizing.",
        "It was overcooked and mushy.",
        "It was tough and hard to chew.",
        "It were poorly made and tasted bad.",
        "The staff was rude and inattentive.",
        "It took too long to arrive and wasn’t worth the wait.",
        "The restaurant was dirty and poorly maintained.",
        "It was wilted and unappealing.",
        "It tasted off and wasn’t fresh.",
        "It was overly sweet and artificial-tasting.",
        "The service was chaotic and disorganized.",
        "It was overpriced and not worth the money.",
        "The chef didn’t seem to put much effort into the dishes.",
        "The restaurant was cramped and uncomfortable.",
        "The staff was unhelpful and seemed annoyed.",
        "The flavors were unbalanced and unpleasant.",
        "It was too greasy and heavy.",
        "It were served at the wrong temperature.",
        "Its platter was disappointing and lacked creativity.",
        "It was undercooked and unsafe to have.",
        "The restaurant had a limited and uninspired menu.",
        "The service was inattentive and frustrating.",
        "It was forgettable and not worth recommending.",
        "The ambiance was dull and uninviting.",
        "It was poorly plated and unappetizing.",
        "The staff was unprofessional and unwelcoming.",
        "The restaurant failed to meet even basic expectations.",
        "It was a complete letdown and not enjoyable.",
    ]

    product_list = []
    customer_list = []
    rating_list = []
    comment_list = []
    date_list = []

    for i in range(num_reviews):
        productId = random.randint(1, len(product_df))
        customerId = random.randint(1, num_customers)
        rating = random.randint(1, 10)

        if rating <= 4:
            comment = random.choice(negative_comments)
        elif rating <= 7:
            comment = random.choice(neutral_comments)
        else:
            comment = random.choice(positive_comments)

        date_str = random.choice(date_df["dateID"].tolist())

        product_list.append(productId)
        customer_list.append(customerId)
        rating_list.append(rating)
        comment_list.append(comment)
        date_list.append(date_str)

    review_df = pd.DataFrame(
        {
            "productId": product_list,
            "customerId": customer_list,
            "rating": rating_list,
            "comment": comment_list,
            "date": date_list,
        }
    )

    # Tính rating trung bình
    rating_dict = defaultdict(list)
    for i in range(len(review_df)):
        pid = review_df.iloc[i]["productId"]
        rt = review_df.iloc[i]["rating"]
        rating_dict[pid].append(rt)

    for pid, lst in rating_dict.items():
        avg_rt = float(round(sum(lst) / len(lst), 2))
        product_df.loc[pid - 1, "rating"] = avg_rt

    return review_df


# --------------------------------------------------
# 11. Gift Exchange
# --------------------------------------------------
def gen_gift_exchange_chunked(
    total_exchanges: int,
    customer_df: pd.DataFrame,
    date_df: pd.DataFrame,
    gift_df: pd.DataFrame,
    chunk_size: int,
    output_gift_exchange_path: str,
):
    with open(output_gift_exchange_path, "w", encoding="utf-8") as f:
        f.write("giftId,customerId,date,quantity\n")

    date_ids = date_df["dateID"].tolist()
    gift_ids = gift_df["giftId"].tolist()
    cust_ids = customer_df["customerId"].tolist()
    num_chunks = math.ceil(total_exchanges / chunk_size)

    gift_use_points_map = defaultdict(int)
    exchange_count = 0

    for c in range(num_chunks):
        chunk_size_actual = min(chunk_size, total_exchanges - exchange_count)
        if chunk_size_actual <= 0:
            break

        rows = []
        for _ in range(chunk_size_actual):
            g_id = random.choice(gift_ids)
            qty = random.randint(1, 3)
            c_id = random.choice(cust_ids)
            d_ = random.choice(date_ids)
            cost_ = gift_df.loc[g_id - 1, "point"] * qty
            rows.append((g_id, c_id, d_, qty, cost_))

        tmp_df = pd.DataFrame(
            rows, columns=["giftId", "customerId", "date", "quantity", "cost"]
        )
        valid_rows = []
        for idx, r_ in tmp_df.iterrows():
            cid = r_["customerId"]
            cost_ = r_["cost"]
            original_rem = customer_df.loc[cid - 1, "remaining_point"]
            used_so_far = gift_use_points_map[cid]
            eff_rem = original_rem - used_so_far
            if cost_ <= eff_rem:
                valid_rows.append((r_["giftId"], cid, r_["date"], r_["quantity"]))
                gift_use_points_map[cid] += cost_

        if valid_rows:
            pd.DataFrame(
                valid_rows, columns=["giftId", "customerId", "date", "quantity"]
            ).to_csv(output_gift_exchange_path, mode="a", header=False, index=False)

        exchange_count += chunk_size_actual
        print(
            f"GiftExchange chunk {c+1}/{num_chunks}, tries={chunk_size_actual} => valid={len(valid_rows)}"
        )

    # Trừ remaining_point
    for cid, used_pts in gift_use_points_map.items():
        customer_df.loc[cid - 1, "remaining_point"] -= used_pts

    # EP VỀ int: tránh .0
    customer_df["remaining_point"] = customer_df["remaining_point"].astype(int)

    return customer_df


# --------------------------------------------------
# 12. MAIN DEMO
# --------------------------------------------------
def main_demo():
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    # 1) Date
    date_df = gen_date_with_holidays("2022-01-01", "2024-12-31")
    date_df.to_csv(f"{output_dir}/date.csv", index=False)

    # 2) Dept & Employee
    dept_df = gen_department(num_departments=3)
    dept_df.to_csv(f"{output_dir}/department.csv", index=False)

    emp_df = gen_employee(dept_df, min_emp=30, max_emp=50)
    emp_df.to_csv(f"{output_dir}/employee.csv", index=False)

    # 3) Gift
    gift_df = gen_gift()
    gift_df.to_csv(f"{output_dir}/gift.csv", index=False)

    # 4) Product
    product_csv_path = "./product.csv"
    prod_df = gen_product_from_csv(product_csv_path)
    prod_df.to_csv(f"{output_dir}/product_init.csv", index=False)

    # 5) Customer
    cust_df = gen_customer(num_customers=1_000_000)
    cust_df.to_csv(f"{output_dir}/customer_init.csv", index=False)

    # 6) Orders & OrderItems
    n_process = 4
    total_orders = 8_000_000
    chunk_size_orders = 100_000
    updated_cust_df = parallel_order_generation(
        total_orders,
        prod_df,
        cust_df,
        date_df,
        emp_df,
        n_process,
        chunk_size_orders,
        output_dir,
    )

    # Ở đây ta ép point, remaining_point về int (phòng hờ)
    updated_cust_df["point"] = updated_cust_df["point"].astype(int)
    updated_cust_df["remaining_point"] = updated_cust_df["remaining_point"].astype(int)

    updated_cust_df.to_csv(f"{output_dir}/customer_after_orders.csv", index=False)

    # 7) Review
    review_df = gen_review(
        num_reviews=1_000_000,
        num_customers=len(updated_cust_df),
        product_df=prod_df,
        date_df=date_df,
    )
    review_df.to_csv(f"{output_dir}/review.csv", index=False)
    prod_df.to_csv(f"{output_dir}/product_after_reviews.csv", index=False)

    # 8) GiftExchange
    gift_ex_csv = f"{output_dir}/gift_exchange.csv"
    final_cust_df = gen_gift_exchange_chunked(
        total_exchanges=100_000,
        customer_df=updated_cust_df,
        date_df=date_df,
        gift_df=gift_df,
        chunk_size=50_000,
        output_gift_exchange_path=gift_ex_csv,
    )
    # final_cust_df["point"] -> all-time, final_cust_df["remaining_point"] -> ep int
    final_cust_df["point"] = final_cust_df["point"].astype(int)
    final_cust_df["remaining_point"] = final_cust_df["remaining_point"].astype(int)

    final_cust_df.to_csv(f"{output_dir}/customer_final.csv", index=False)

    print("=== Data generation completed ===")
    print("Output CSV files are in:", output_dir)


if __name__ == "__main__":
    main_demo()
