import pandas as pd
import random, os, requests
from faker import Faker
from dotenv import load_dotenv
from datetime import datetime, time

# declare and load environment variables
load_dotenv()
fake = Faker()

GOOGLE_API_KEY = os.getenv('GOOGLE_CALENDAR_API_KEY')

# order: oderId, customerId, orderDate, orderTime, total_quantity, total_price, employeeId
def gen_order_data(num_orders, numCustomer, date_df, employeeList):
    id_list = range(1, num_orders + 1)
    quantity_list = [0] * num_orders
    price_list = [0] * num_orders
    cusId, date_list, time_list, employeeId_list = [], [], [], []

    for i in range(num_orders):
        cusId.append(random.randint(1, numCustomer))
        date_list.append(random.choice(date_df['dateID'].tolist()))
        time_list.append(time(random.randint(6, 21), random.randint(0, 59), random.randint(0, 59)).strftime("%H:%M:%S"))
        employeeId_list.append(random.choice(employeeList['employeeId']))

    df = pd.DataFrame({
        'orderId': id_list,
        'customerId': cusId,
        'orderDate': date_list,
        'orderTime': time_list,
        'total_quantity': quantity_list,
        'total_price': price_list,
        'employeeId': employeeId_list
    })

    return df

# order_item: orderId, productId, quantity, price, discount
def gen_order_item(order_df, product_df, customer_df):
    id_list = []
    product_list = []
    quantity_list = []
    price_list = []
    discount_list = []

    for i in range(len(order_df)):
        id = i + 1
        quantity = random.randint(1, 10)
        total_price = 0
        prod_set = set()

        for j in range(quantity):
            productId = random.randint(1, len(product_df))
            while productId in prod_set:
                productId = random.randint(1, len(product_df))
            prod_set.add(productId)
            quant = random.randint(1, 5)
            total = round(product_df.iloc[productId - 1]["unit_price"] * quant, 2)

            id_list.append(id)
            product_list.append(productId)
            price_list.append(total)
            quantity_list.append(quant)
            discount_list.append(0)

            total_price += total

        order_df.loc[i, 'total_quantity'] = quantity
        order_df.loc[i, 'total_price'] = total_price
        customer_df.loc[order_df.iloc[i]['customerId'] - 1, 'remaining_point'] += total_price // 5

        customer_df.loc[order_df.iloc[i]['customerId'] - 1, 'point'] = customer_df.loc[order_df.iloc[i]['customerId'] - 1, 'remaining_point']

    df = pd.DataFrame({
        "id": id_list,
        "productId": product_list,
        "quantity": quantity_list,
        "price": price_list,
        "discount": discount_list
    })

    return df

# review: productId, customerId, rating, comment, date
def gen_review(num_reviews, num_customers, product_df, date_df):
    positive_comments = [
        # Positive Comments
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
        "The restaurant exceeded my expectations in every way."
    ]
    neutral_comments = [
        # Neutral Comments
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
        "The ambiance was fine, but it felt a bit generic."
    ]    
    negative_comments = [
        # Negative Comments
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
        "It was a complete letdown and not enjoyable."
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
        date = random.choice(date_df['dateID'].tolist())
        product_list.append(productId)
        customer_list.append(customerId)
        rating_list.append(rating)
        comment_list.append(comment)
        date_list.append(date)

    df = pd.DataFrame({
        'productId': product_list,
        'customerId': customer_list,
        'rating': rating_list,
        'comment': comment_list,
        'date': date_list
    })

    rating_dict = {}

    for i in range(len(df)):
        productId = df.iloc[i]['productId']
        rating = df.iloc[i]['rating']
        if productId in rating_dict:
            rating_dict[productId].append(rating)
        else:
            rating_dict[productId] = [rating]

    for x,y in rating_dict.items():
        product_df.loc[x-1, 'rating'] = round(sum(y) / len(y), 2)
    
    return df

# gift_exchange: giftId, customerId, date, quantity
def gen_gift_exchange(num_gift_exchanges, customer_df, date_df, gift_df):
    gift_list = []
    customer_list = []
    date_list = []
    quantity_list = []

    for i in range(num_gift_exchanges):
        giftId = random.randint(1, len(gift_df))
        quantity = random.randint(1, 3)
        customerId = random.randint(1, len(customer_df))
        cnt = 0

        # Ensure the customer has enough points
        while customer_df.loc[customerId - 1, 'remaining_point'] < giftId * 10 * quantity and cnt < 10:
            cnt += 1
            customerId = random.randint(1, len(customer_df))
        
        if cnt == 10:
            # Skip this gift exchange if the customer doesn't have enough points
            continue

        # Append to all lists
        gift_list.append(giftId)
        quantity_list.append(quantity)
        customer_list.append(customerId)
        date_list.append(random.choice(date_df['dateID'].tolist()))

        # Deduct points from the customer
        customer_df.loc[customerId - 1, 'remaining_point'] -= giftId * 10 * quantity

    # Create the DataFrame
    df = pd.DataFrame({
        'giftId': gift_list,
        'customerId': customer_list,
        'date': date_list,
        'quantity': quantity_list
    })

    return df

# gift: giftId, name, state, point
def gen_gift():
    gift_list = [
        "Keychain with store logo", "Document clip engraved with logo", "Handmade wooden coaster", "Luxury pen",
        "Branded helmet", "Tote bag with logo", "Branded t-shirt", "Scarf or winter beanie",
        "Daily planner board", "Fabric-covered notebook", "Luxury leather notebook", "Vintage wooden photo frame",
        "Coffee-style desk calendar", "Relaxing scented candle", "Small decorative menu board", "Neck pillow with cafe voucher",
        "Unique coffee tablecloth", "Decorative hanging plant bag", "Classic style table runner", "Branded back cushion",
        "Spill-proof coffee cup", "Limited edition sample drink set", "Phone case with logo", "Premium towel",
        "Office supplies set with logo", "Shockproof laptop bag", "Wooden lid jars for coffee beans", "Cafe-style desk lamp",
        "Specialty coffee gift set from various regions", "Glass coffee cup set", "Premium ceramic mug", "Neck pillow with cafe voucher",
        "Hourglass coffee timer", "Durable thermal bottle", "Handcrafted coffee filter", "Mini coffee maker",
        "Fashion handbag", "Cafe-style wall clock", "Premium coffee bean gift set", "Handheld coffee brewer"
    ]
    gift_id = range(1, len(gift_list) + 1)
    gift_name = gift_list
    gift_state = ["available"] * len(gift_list)
    gift_point = [x*10 for x in range(1, len(gift_list) + 1)]

    gift_df = pd.DataFrame({
        'giftId': gift_id,
        'name': gift_name,
        'state': gift_state,
        'point': gift_point
    })

    return gift_df
    
# customer: customerId, name, phone_number, address, DOB, customer_since, gender, point
def gen_fake_phone_number():
    num1, num2, num3 = random.randint(0, 999), random.randint(0, 9999), random.randint(0, 999)
    return f"{num1:03d}-{num2:04d}-{num3:03d}"

def gen_customer(num_customers):
    customerId = range(1, num_customers + 1)
    name = [fake.name() for _ in range(num_customers)]
    phone_number = [gen_fake_phone_number() for _ in range(num_customers)]
    address = [fake.address().replace('\n', ' ') for _ in range(num_customers)]
    DOB = [fake.date_of_birth(minimum_age=16, maximum_age=80) for _ in range(num_customers)]
    customer_since = [fake.date_between(start_date='-5y', end_date='today') for _ in range(num_customers)]
    gender = ['M' if random.randint(0, 1) == 0 else 'F' for _ in range(num_customers)]
    point = [0] * num_customers
    remaining_point = [0] * num_customers

    df = pd.DataFrame({
        'customerId': customerId,
        'name': name,
        'phone_number': phone_number,
        'address': address,
        'DOB': DOB,
        'customer_since': customer_since,
        'gender' : gender,
        'point': point,
        'remaining_point': remaining_point
    })

    return df

# date: dateId, day, week, month, quarter, year, isHoliday, isWeekend, holidayName
def convert_date_to_dateId(year, month, day):
    if month < 10:
        month = f'0{month}'
    if day < 10:
        day = f'0{day}'
    return f'{year}{month}{day}'

def convert_date(year, month, day):
    if month < 10:
        month = f'0{month}'
    if day < 10:
        day = f'0{day}'
    return f'{year}-{month}-{day}'

def get_holidays():
    url = "https://www.googleapis.com/calendar/v3/calendars/en.vietnamese%23holiday@group.v.calendar.google.com/events"
    params = {
                "key": GOOGLE_API_KEY,
                "timeMin" : "2022-01-01T00:00:00Z",
                "timeMax" : "2025-01-01T23:59:59Z",
                "singleEvents" : True,
                "orderBy" : "startTime",
                "fields" : "items(start,end,summary)"
            }
    
    response = requests.get(url, params=params)
    return response.json()

def gen_date():
    start_date = pd.to_datetime('2022-01-01')
    end_date = pd.to_datetime('2024-12-31')
    date_range = pd.date_range(start=start_date, end=end_date)
    holidays = [(x["start"]["date"], x["summary"]) for x in get_holidays()["items"]]
    
    dateID, day, week, month, quarter, year, isHoliday, isWeekend, holidayName = [], [], [], [], [], [], [], [], []

    for date in date_range:
        dateID.append(convert_date_to_dateId(date.year, date.month, date.day))
        day.append(date.day)
        week.append(date.isocalendar()[1])
        month.append(date.month)
        quarter.append((date.month - 1) // 3 + 1)
        year.append(date.year)
        if convert_date(date.year, date.month, date.day) in [x[0] for x in holidays]:
            isHoliday.append(1)
            holidayName.append([x[1] for x in holidays if x[0] == convert_date(date.year, date.month, date.day)][0])
        else:
            isHoliday.append(0)
            holidayName.append("")
        isWeekend.append(1 if date.weekday() >= 5 else 0)

    df = pd.DataFrame({
        "dateID": dateID,
        "day": day,
        "week": week,
        "month": month,
        "quarter": quarter,
        "year": year,
        "isHoliday": isHoliday,
        "isWeekend": isWeekend,
        "holidayName": holidayName
    })    

    return df

# department: departmentId, name, location, phone_number, email
def gen_department(num_departments):
    departmentId = range(1, num_departments + 1)
    name, location, phone_number, email = [], [], [], []

    for _ in range(num_departments):
        phone_number.append(gen_fake_phone_number())
        location.append(fake.address().replace('\n', ' '))
        email.append(fake.company_email())
        name.append(fake.company())

    df = pd.DataFrame({
        'departmentId': departmentId,
        'name': name,
        'location': location,
        'phone_number': phone_number,
        'email': email
    })

    return df

# employee: employeeId, name, departmentId, hireDate, salary, position, phone_number
def gen_employee(num_departments):
    employeeId = []
    name = []
    departmentId = []
    hireDate = []
    position = []
    salary = []
    phone_number = []
    cnt = 1

    for i in range(num_departments):
        num_employees = random.randint(1,3) * 20

        departmentId.extend([i+1] * num_employees)
        employeeId.extend(range(cnt, cnt + num_employees))
        cnt += num_employees
        name.extend([fake.name() for _ in range(num_employees)])
        hireDate.extend([fake.date_between(start_date='-5y', end_date='today') for _ in range(num_employees)])
        position.extend(["Manager"] * (2 * num_employees // 20) + ["Barista"] * (4 * num_employees // 20) + ["Cashier"] * (4 * num_employees // 20) + ["Waiter"] * (10 * num_employees // 20))
        salary.extend(['5000000' if position[i] == 'Manager' else '3000000' if position[i] == 'Barista' else '2000000' for i in range(num_employees)])
        phone_number.extend([gen_fake_phone_number() for _ in range(num_employees)])

    df = pd.DataFrame({
        'employeeId': employeeId,
        'name': name,
        'departmentId': departmentId,
        'hireDate': hireDate,
        'salary': salary,
        'position': position,
        'phone_number': phone_number
    })

    return df

# product: productId, name, category, description, unit_price, state, rating
def gen_product():
    product_df = pd.read_csv('product.csv')

    productId = range(1, len(product_df) + 1)
    name = product_df['product_name'].tolist()
    category = product_df['product_category'].tolist()
    description = product_df['product_description'].tolist()
    unit_price = product_df['unit_price'].tolist()
    state = product_df['state'].tolist()
    rating = [0] * len(product_df)

    df = pd.DataFrame({
        'productId': productId,
        'name': name,
        'category': category,
        'description': description,
        'unit_price': unit_price,
        'state': state,
        'rating': rating
    })

    return df
