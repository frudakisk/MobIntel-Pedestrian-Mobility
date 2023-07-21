import csv, json

def csvTojson(csvFilePath, jsonPath):
    data = []

    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            del rows[""]
            for key, value in rows.items():
                if key == "mode_RSSI":
                    rows[key] = int(value)
                elif key == "best_RSSI":
                    rows[key] = int(value)
                elif key == "is_emitter":
                    if value == "False":
                        rows[key] = False
                    elif value == "True":
                        rows[key] = True

            data.append(rows)


    with open(jsonPath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))


csvFile = "datasets/GridLibDriverGrid.csv"
jsonPath = "webDevelopmentFiles/interactiveGrid/grid_json.json"

csvTojson(csvFile, jsonPath)