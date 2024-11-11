#!/bin/bash

# فایل‌های خروجی برای ذخیره زمان‌ها
output_file_original="times_original.csv"
output_file_reduce="times_reduce.csv"

# ایجاد سرآیند برای فایل‌های خروجی
echo "workers,time" > $output_file_original
echo "workers,time" > $output_file_reduce

# پارامترهای انتگرال‌گیری
a=0
b=1.57
n=1000000

# اجرای حلقه با تعداد کارگرهای مختلف (از 2 تا 8)
for workers in {2..8}; do
    echo "Running original version with $workers workers"
    /usr/bin/time -f "$workers,%e" mpirun -np $workers python3 /homes/mesmaeili/Documents/Prog5/assignment2.py -a $a -b $b -n $n 2>> $output_file_original

    echo "Running Reduce version with $workers workers"
    /usr/bin/time -f "$workers,%e" mpirun -np $workers python3 open_MPI.py -a $a -b $b -n $n 2>> $output_file_reduce
done
