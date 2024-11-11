import matplotlib.pyplot as plt
import pandas as pd

# بارگذاری داده‌ها از فایل‌های CSV
data_original = pd.read_csv("times_original.csv")
data_reduce = pd.read_csv("times_reduce.csv")

# رسم نمودار مقایسه‌ای
plt.plot(data_original["workers"], data_original["time"], label="Original Version", marker='o')
plt.plot(data_reduce["workers"], data_reduce["time"], label="Reduce Version", marker='o')

# عنوان و برچسب‌ها
plt.title("Execution Time Comparison of Original vs Reduce Version")
plt.xlabel("Number of Workers")
plt.ylabel("Execution Time (seconds)")
plt.legend()

# نمایش نمودار
plt.savefig("comparison_plot.png")

