import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, ForeignKey
from sqlalchemy.sql import func, text

# مسیر فایل CSV
csv_file_path = '/data/datasets/Programming/FSIS-Recall-Summary-2014.csv'

# خواندن داده‌های فایل CSV
df = pd.read_csv(csv_file_path, skiprows=1)
df.columns = ["recall_date", "recall_number", "recall_class", "product_description", "reason_for_recall", "pounds_recalled"]

# تبدیل مقادیر خالی در ستون pounds_recalled به صفر و تبدیل به نوع string
df['pounds_recalled'] = df['pounds_recalled'].fillna(0).astype(str)

# جایگزینی مقادیر NaN در ستون‌های product_description و reason_for_recall با مقادیر پیش‌فرض و تبدیل به نوع string
df['product_description'] = df['product_description'].fillna("Unknown").astype(str)
df['reason_for_recall'] = df['reason_for_recall'].fillna("Unknown Reason").astype(str)

# اتصال به پایگاه داده SQLite
engine = create_engine('sqlite:///recall_summary_normalized.db')
connection = engine.connect()
metadata = MetaData()

# تعریف جداول
recalls = Table('recalls', metadata,
    Column('recall_id', Integer, primary_key=True),
    Column('recall_date', String),  # اگر نیاز به تاریخ دقیق نیست می‌توان از String استفاده کرد
    Column('recall_number', String),
    Column('recall_class', String),
    Column('pounds_recalled', Integer)
)

products = Table('products', metadata,
    Column('product_id', Integer, primary_key=True),
    Column('product_description', String, unique=True)
)

reasons = Table('reasons', metadata,
    Column('reason_id', Integer, primary_key=True),
    Column('reason_description', String, unique=True)
)

recall_products = Table('recall_products', metadata,
    Column('recall_id', Integer, ForeignKey('recalls.recall_id')),
    Column('product_id', Integer, ForeignKey('products.product_id')),
    Column('reason_id', Integer, ForeignKey('reasons.reason_id'))
)

# ایجاد جداول در پایگاه داده
metadata.create_all(engine)

# مرحله 3: وارد کردن داده‌ها از DataFrame به جداول نرمال‌شده
for index, row in df.iterrows():
    # اضافه کردن به جدول recalls
    pounds_recalled = int(row['pounds_recalled'].replace(',', '')) if row['pounds_recalled'] != '0' else 0

    recall_insert = recalls.insert().values(
        recall_date=row['recall_date'],
        recall_number=row['recall_number'],
        recall_class=row['recall_class'],
        pounds_recalled=pounds_recalled
    )
    recall_result = connection.execute(recall_insert)
    recall_id = recall_result.inserted_primary_key[0]

    # اضافه کردن به جدول products (اگر محصول موجود نیست)
    product_insert = products.insert().prefix_with("OR IGNORE").values(
        product_description=row['product_description']
    )
    connection.execute(product_insert)
    product_result = connection.execute(text(
        "SELECT product_id FROM products WHERE product_description = :desc"
    ), {"desc": row['product_description']}).fetchone()

    if product_result is not None:
        product_id = product_result[0]
    else:
        print(f"Warning: Product '{row['product_description']}' not found in products table.")
        continue  # ادامه به رکورد بعدی، چون محصول پیدا نشد

    # اضافه کردن به جدول reasons (اگر دلیل موجود نیست)
    reason_insert = reasons.insert().prefix_with("OR IGNORE").values(
        reason_description=row['reason_for_recall']
    )
    connection.execute(reason_insert)
    reason_result = connection.execute(text(
        "SELECT reason_id FROM reasons WHERE reason_description = :desc"
    ), {"desc": row['reason_for_recall']}).fetchone()

    if reason_result is not None:
        reason_id = reason_result[0]
    else:
        print(f"Warning: Reason '{row['reason_for_recall']}' not found in reasons table.")
        continue  # ادامه به رکورد بعدی، چون دلیل پیدا نشد

    # اضافه کردن به جدول recall_products
    recall_products_insert = recall_products.insert().values(
        recall_id=recall_id,
        product_id=product_id,
        reason_id=reason_id
    )
    connection.execute(recall_products_insert)

# مرحله 4: پیدا کردن حداکثر وزن یک محصول با کوئری SQL
max_weight_query = text("SELECT MAX(pounds_recalled) FROM recalls")
max_weight = connection.execute(max_weight_query).scalar()
print(f"Maximum weight of a recalled product: {max_weight} pounds")

# بستن اتصال به پایگاه داده
connection.close()
