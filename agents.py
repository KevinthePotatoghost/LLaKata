import pandas as pd
import re
from huggingface_hub import InferenceClient
import streamlit as st

api_key = st.text_input("Enter your Hugging Face API Key:", type="password")

if not api_key:
    st.warning("Please enter your Hugging Face API key.")
else:
    client = InferenceClient(api_key=api_key)

# Load the CSV data (adjust the path if necessary)
csv_file = 'merged_file.csv'  # Adjust the path if necessary
df = pd.read_csv(csv_file)

# Chatbot state management
history = []

# Functions to handle different tasks

def check_order_status(order_id):
    result = df[df['OrderID'] == order_id]
    if result.empty:
        return f"Order ID {order_id} not found."
    else:
        order_status = result['OrderStatus'].iloc[0]
        shipped_date = result['ShippingDate'].iloc[0]
        shipping_date = pd.to_datetime(shipped_date)
        shipping_date_str = shipping_date.strftime('%d/%m/%Y')
        return f"The status of your order with Order ID {order_id} is: {order_status}, it is shipped on {shipping_date_str}"

def handle_product_comparison(query):
    match = re.search(r"between\s*(.*?)\s*and\s*(.*)", query, re.IGNORECASE)
    if match:
        product_a_name = match.group(1).strip()
        product_b_name = match.group(2).strip()
        product_a = df[df['ProductName'].str.contains(product_a_name, case=False, na=False)]
        product_b = df[df['ProductName'].str.contains(product_b_name, case=False, na=False)]
        if product_a.empty:
            return f"Sorry, I couldn't find the product '{product_a_name}'."
        if product_b.empty:
            return f"Sorry, I couldn't find the product '{product_b_name}'."
        product_a_details = product_a.iloc[0]
        product_b_details = product_b.iloc[0]
        comparison = f"Here is the comparison between {product_a_name} and {product_b_name}:\n"
        comparison += f"1. Price: {product_a_details['Price']} vs {product_b_details['Price']}\n"
        comparison += f"2. Stock Quantity: {product_a_details['StockQuantity']} vs {product_b_details['StockQuantity']}\n"
        comparison += f"3. Description: {product_a_details['Description']} vs {product_b_details['Description']}\n"
        return comparison
    else:
        return "Sorry, I couldn't understand your comparison request. Please mention two products to compare."

def check_order_returnable(order_id):
    result = df[df['OrderID'] == order_id]
    if result.empty:
        return f"Order ID {order_id} not found."
    else:
        return_status = result['ReturnEligible'].iloc[0]
        return f"The eligibility for return of your order with Order ID {order_id} is: {return_status}"

def handle_previous_orders(query):
    match = re.search(r"is\s*(\d+)", query, re.IGNORECASE)
    if match:
        customer_id = int(match.group(1))
        customer_orders = df[df['CustomerID'] == customer_id]
        if customer_orders.empty:
            return f"No orders found for Customer ID {customer_id}."
        order_details = ""
        for _, row in customer_orders.iterrows():
            order_details += f"Order ID: {row[str('OrderID')]} - Product: {row['ProductName']} - Status: {row['OrderStatus']}\n"
        return f"Here are your previous orders:\n{order_details}"
    else:
        return "Sorry, I couldn't find a Customer ID in your request. Please try again."

def handle_order_status_check(query):
    match = re.search(r"order(?: ID)?\s*(\d+)", query, re.IGNORECASE)
    order_responses = []
    if match:
        order_id = int(match.group(1))
        if 'return' in query.lower():
            status_response = check_order_returnable(order_id)
            order_responses.append(status_response)
        if 'status' in query.lower():
            status_response = check_order_status(order_id)
            order_responses.append(status_response)
        if order_responses:
            return "\n\n".join(order_responses)
        else:
            return "Sorry, there are no relevant information"
    else:
        return "Sorry, I couldn't find an Order ID in your request. Please try again."

def query_huggingface_model(messages):
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct",  # Replace with your model
        messages=messages,
        max_tokens=500,
        stream=False
    )
    return response['choices'][0]['message']['content']

def run_agent(query, history):
    history.append({"role": "user", "content": query})
    model_response = query_huggingface_model(history)
    history.append({"role": "user", "content": model_response})
    return model_response, history

def regex_filter_products(query, df):
    query = query.lower()
    pattern = ".*" + ".*".join([re.escape(keyword) for keyword in query.split()]) + ".*"
    filtered_df = df[df['ProductName'].str.contains(pattern, case=False, na=False, regex=True)]
    return filtered_df

def search_csv(query):
    result = df[df['ProductName'].str.contains(query, case=False, na=False)]
    if result.empty:
        result = regex_filter_products(query, df)
    if result.empty:
        return "No products found matching your query."
    if len(result) > 2:
        top_10 = result.head(10)
        response = "I found multiple products. Here are the top 5:\n"
        for index, row in top_10.iterrows():
            response += f"{row['ProductName']} (ID: {row['Product ID']}) - {row['Price']}\n"
        response += "\nPlease be more specific to help narrow down the results."
        return response
    elif len(result) == 1:
        product_details = "\n".join([f"Product: {row['ProductName']} (ID: {row['Product ID']}) - Price: {row['Price']} - Stock: {row['StockQuantity']} - Description: {row['Description']}" for index, row in result.iterrows()])
        return product_details

# Streamlit UI
st.title("Chatbot - Product Information")

# User input for the query
user_query = st.text_input("Ask a question about products or orders:")

if user_query:
    # Check if the user query is asking for product comparison
    if 'between' in user_query.lower() and 'and' in user_query.lower():
        response = handle_product_comparison(user_query)
        st.write(f"**Chatbot:** {response}")
    # Check for product search queries
    elif 'product' in user_query.lower() or 'search' in user_query.lower():
        search_query = st.text_input("Please enter the product name or category to search:")
        if search_query:
            response = search_csv(search_query)
            st.write(f"**Chatbot:** {response}")
    # Check for order queries (status, return eligibility)
    elif 'order id' in user_query.lower():
        response = handle_order_status_check(user_query)
        st.write(f"**Chatbot:** {response}")
    # Handle customer ID queries
    elif 'customer id' in user_query.lower():
        response = handle_previous_orders(user_query)
        st.write(f"**Chatbot:** {response}")
    # General queries via the Hugging Face model
    else:
        response, history = run_agent(user_query, history)
        st.write(f"**Chatbot:** {response}")
