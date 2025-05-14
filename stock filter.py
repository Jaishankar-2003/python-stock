import csv
# Function to filter and save stock names
def filter_stock_names(input_file, output_file):
    with open(input_file, mode='r') as infile, open(output_file, mode='w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write the header for the output CSV
        writer.writerow(['Stock Name'])

        # Skip the header row of the input file
        next(reader)

        # Loop through the rows and extract the stock name (first column)
        for row in reader:
            stock_name = row[0]
            writer.writerow([stock_name])


# Example usage
input_file = 'nse_symbols.csv'  # Replace with your input CSV file path
output_file = 'filtered_stock_names.csv'  # Output file to store stock names
filter_stock_names(input_file, output_file)
