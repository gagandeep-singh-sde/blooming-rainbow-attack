import multiprocessing
import time

total_numbers = 5000000
batch_size = 1000
num_cores = 10


def print_odd_numbers(start, end):
    for i in range(start, end + 1):
        if i % 2 != 0:
            print(i)


def main():
    start_time = time.time()

    with multiprocessing.Pool(processes=num_cores) as pool:
        tasks = []
        for i in range(0, total_numbers, batch_size):
            end = i + batch_size - 1
            if end > total_numbers:
                end = total_numbers
            tasks.append(pool.apply_async(print_odd_numbers, (i, end)))

        # Wait for all tasks to complete
        for task in tasks:
            task.wait()

    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
