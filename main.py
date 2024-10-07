import os
import re
import pandas as pd


def process_files(inputfile):
    with open(f'./files/AccountingTransactionReport/{inputfile}', 'r') as file:
        # Skip the first 6 lines (metadata)
        data = []
        combined_data = []

        for _ in range(6):
            next(file)

        # Process the file line by line
        temp = None
        while True:
            if temp:
                line1 = temp
                temp = None
            else:
                line1 = file.readline().strip()  # First line of the transaction

            if not line1:
                continue

            if any(keyword in line1 for keyword in ["Transactions Accounting Report", "Page:", "Date:", "Time:"]):
                print(f"Skipping metadata line: {line1}")
                continue

            if "End of Report" in line1:
                # Stop processing if we reach end of file or 'End of Report'
                break

            line2 = file.readline().strip()  # Second line of the transaction

            # Skip headers if encountered
            if 'Effectiv' in line1 or 'Date' in line1 or '--------' in line1:
                continue

            pattern = re.compile(
                r'(\d{2}/\d{2}/\d{2})\s+'            # Date (MM/DD/YY)
                r'(\d+)\s+'                           # Transaction number
                # Optional third column (e.g., 'L115084') - can be None
                r'(\S+)?\s+'
                r'(\d+)\s+'                           # Item number
                r'(\S+)\s+'                           # GL Reference
                # Quantity @ Rate (with possible negatives)
                r'(-?[\d,]+\.\d+\s+@\s+-?[\d,]+\.\d+)\s+'
                r'(\d+)\s+'                           # DR Account
                r'(\d+)?\s+'
                # Amount (with possible negatives and commas)
                r'(-?[\d,]+\.\d+)'
            )

            match = pattern.search(line1)

            if match:
                combined_data.extend(match.groups())

            pattern2 = re.compile(
                r'(\w+-\w+)\s+(\S+)\s+(.*?)?\s+(\d+)\s+(-?\d+,?\d*\.\d+)'
            )

            match2 = pattern2.search(line2)

            if match2:
                combined_data.extend(match2.groups())

            pattern3 = re.compile(
                '(\d+)\s+(\S+)\s+(-?[\d,]+\.\d+\s+@\s+-?[\d,]+\.\d+)\s+(\d+)\s+(\d+)\s+(-?[\d,]+\.\d+)')

            line3 = file.readline().strip()
            match3 = pattern3.search(line3)

            if match3:
                line4 = file.readline().strip()
                pattern4 = pattern = re.compile(
                    r'(\d+)\s+'
                    r'(-?[\d,]+\.\d+)'
                )
                match4 = pattern4.search(line4)

                if match4:
                    combined_data.extend(match3.groups())
                    combined_data.extend(match4.groups())

                temp = None
            else:
                temp = line3

            if match and match2 and combined_data:
                if match3 and match4:
                    line5 = file.readline().strip()
                    match5 = pattern3.search(line5)

                    if match5:
                        combined_data.extend(match5.groups())

                        line6 = file.readline().strip()
                        match6 = pattern4.search(line6)

                        if match6:
                            combined_data.extend(match6.groups())

                        data.append(combined_data)
                        combined_data = []
                    else:
                        temp = line5
                        data.append(combined_data)

                else:
                    data.append(combined_data)
                combined_data = []
            else:
                if match:
                    try:
                        print(match.groups())
                        print(match2.groups())
                    except Exception as e:
                        print('Exception in finally bloack: ', e)
                    if match2:
                        print(match2.groups())
                combined_data = []

    # Create a pandas DataFrame and write to CSV
    df = pd.DataFrame(data)
    output_file = inputfile[:-3]
    output_file += 'csv'
    # Output as tab-delimited CSV
    df.to_csv(f'./output/{output_file}', index=False, header=False)

    print(f"CSV file generated: {output_file}")


def parse_files():

    directory = './files/AccountingTransactionReport'

    file_names = os.listdir(directory)

    file_names = [f for f in file_names if os.path.isfile(
        os.path.join(directory, f))]

    for file in file_names:
        process_files(file)


parse_files()
# process_files('Sept 2024_MW.txt')
