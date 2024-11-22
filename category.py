from compare import df
fridge = df[df['Category'] == 'Fridges']
fridge_freezer = df[df['Category'] == 'Fridge Freezers']
freezer = df[df['Category'] == 'Freezers']
cpus = df[df['Category'] == 'CPUs']
camera = df[df['Category'] == 'Digital Cameras']
dish_washer = df[df['Category'] == 'Dishwashers']
microwave = df[df['Category'] == 'Microwaves']
phones = df[df['Category'] == 'Mobile Phones']
tvs = df[df['Category'] == 'TVs']
washing_machine = df[df['Category'] == 'Washing Machines']

fridge = (fridge[['ProductName', ' Cluster Label', 'Price', 'Description']])
fridge_freezer = (fridge_freezer[['ProductName', ' Cluster Label', 'Price', 'Description']])
freezer = (freezer[['ProductName', ' Cluster Label', 'Price', 'Description']])
cpus = (cpus[['ProductName', ' Cluster Label', 'Price', 'Description']])
camera = (camera[['ProductName', ' Cluster Label', 'Price', 'Description']])
dish_washer = (dish_washer[['ProductName', ' Cluster Label', 'Price', 'Description']])
microwave = (microwave[['ProductName', ' Cluster Label', 'Price', 'Description']])
phones = (phones[['ProductName', ' Cluster Label', 'Price', 'Description']])
tvs = (tvs[['ProductName', ' Cluster Label', 'Price', 'Description']])
washing_machine = (washing_machine[['ProductName',' Cluster Label', 'Price', 'Description']])

unique_category = df.drop_duplicates(subset=['Category'])
product_categories = "\n".join([
    f"Category:{row['Category']}"
    for index, row in unique_category.iterrows()
])

unique_brand = df[' Cluster Label'].str.split().str[0].str.strip()
