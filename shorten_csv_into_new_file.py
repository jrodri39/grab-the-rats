import csv

with open('/home/insane-krazed/Documents/Python Code/Data_Analysis/krat_raw_beeps.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)

    with open('/home/insane-krazed/Documents/Python Code/Data_Analysis/sample_data.csv', 'w') as new_file:
        fieldNames = ['node', 'parent', 'when', 'radio_id', 'tag', 'frequency', 'rssi', 'longitude', 'latitude',  ]
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldNames, delimiter=',')

        csv_writer.writeheader()
        i = 0
        for line in csv_reader:
            i+=1
            if i<=1000:
                csv_writer.writerow(line)
            else:
                break
