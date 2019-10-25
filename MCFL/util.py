import csv

def write_into_csv(path, result_list, headline):
    f = open(path, 'w')
    csv_writer = csv.DictWriter(f, headline)
    csv_writer.writeheader()
    for row in result_list:
        result_dict = {}
        for item in headline:
            # note that: the item may not own the key.
            result_dict[item] = row.get(item, None)
        csv_writer.writerow(result_dict)

