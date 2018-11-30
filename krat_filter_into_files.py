import csv

with open('/home/insane-krazed/Documents/Python Code/Data_Analysis/krat_raw_beeps.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)

    with open('/home/insane-krazed/Documents/Python Code/Data_Analysis/filtered_data_x.csv', 'w') as new_file:
        fieldNames = ['node', 'parent', 'when', 'radio_id', 'tag', 'frequency', 'rssi', 'longitude', 'latitude',  ]
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldNames, delimiter=',')

        csv_writer.writeheader()
        i = 0
        for line in csv_reader:
            i+=1
            if i<=10:
                csv_writer.writerow(line)
            else:
                break
    with open('/home/insane-krazed/Documents/Python Code/Data_Analysis/unique_values.csv', 'w') as uvf: #unique value file
        uvf_writer = csv.writer(uvf, delimiter=',')
        t = 0
        unique_tags = []
        for line in csv_reader:
            if line['tag'] not in unique_tags:
                uvf.write(line['tag'] + '\n')
                unique_tags.append(line['tag'])
            """
            t+=1
            if t<=10:
                mylist =
                uvf.write(line['tag'] + '\n')
                #uvf_writer.writerow(line['tag'])
            else:
                break
            """
        """
        uvf_writer = csv.DictWriter(uvf,fieldnames=fieldNames, delimiter=',')
        t = 0
        for line in csv_reader:
            t+=1
            if t<=10:
                uvf_writer.writerow(line)
            else:
                break
        """
"""
    i = 0
    for line in csv_reader:
        i+=1
        if i<=10:
            print(line)
        else:
            break
"""
