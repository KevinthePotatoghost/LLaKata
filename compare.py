import pandas as pd
from huggingface_hub import InferenceClient
import re
import streamlit as st

df = pd.read_csv('merged_file.csv')
hf_token = st.secrets["HF_TOKEN"]
client = InferenceClient(api_key=hf_token)

def check_order_status(order_id):
    result = df[df['OrderID'] == order_id]
    if result.empty:
        return f"Order ID {order_id} not found."
    else:
        order_status = result['OrderStatus'].iloc[0]
        shipped_date = result['ShippingDate'].iloc[0]
        shipping_date = pd.to_datetime(shipped_date)
        shipping_date_str = shipping_date.strftime('%d/%m/%Y')

def check_order_returnable(order_id):
    result = df[df['OrderID'] == order_id]
    if result.empty:
        return f"Order ID {order_id} not found."
    else:
        return_status = result['ReturnEligible'].iloc[0]
        response_return = f"The eligibility for return of your order with Order ID {order_id} is: {return_status}"
    return response_return

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

        prompt = f"""Here is all the items by the customer information:\n{order_details}\n
        Provide a clear list of item for the user."""

        # Use the model to generate a response for the order status
        response, st.session_state.history = run_agent(prompt, st.session_state.history)
        st.write(f"**Chatbot:** \n{response}")

    else:
        return "Sorry, I couldn't find a Customer ID in your request. Please try again."


def handle_order_status_check(query):
    match = re.search(r"order(?: ID)?\s*(\d+)", query, re.IGNORECASE)
    if match:
        order_id = int(match.group(1))  # Extract Order ID from the query
        order_responses = []

        # If the query asks about returns, check if the order is returnable
        if 'return' in query.lower():
            status_response = check_order_returnable(order_id)
            order_responses.append(status_response)

            # Prepare the prompt to pass to the model
            prompt = f"""You have to understand this:\n{status_response}\n
                        Tell the user if the product is returnable or not."""

            # Use the model to generate a response
            response, st.session_state.history = run_agent(prompt, st.session_state.history)
            st.write(f"**Chatbot:** \n{response}")
        if 'status' in query.lower():
            status_response = check_order_status(order_id)
            order_responses.append(status_response)

            # Prepare the prompt for order status
            prompt = f"""Here is the order status information:\n{status_response}\n
                                    Provide a clear and concise explanation of the status for the user."""

            # Use the model to generate a response for the order status
            response, st.session_state.history = run_agent(prompt, st.session_state.history)
            st.write(f"**Chatbot:** \n{response}")

        else:
            return "Sorry, there are no relevant information"
    else:
        return "Sorry, I couldn't find an Order ID in your request. Please try again."

def handle_product_query(query):
    colour_match = re.search(r"in\s*(.*)", query, re.IGNORECASE)
    # Define some common phrases to look for and remove from the query
    phrases_to_remove = [
        "i'm looking for",
        "tell me about"
    ]
    # Normalize query by making it lowercase and removing the phrases
    query_lower = query.lower()
    for phrase in phrases_to_remove:
        if phrase in query_lower:
            query_lower = query_lower.replace(phrase, "").strip()

    # The remaining part should be the product name or search term
    product_name = query_lower.strip()

    if not product_name:
        return "Sorry, I couldn't understand the product you're asking about. Please try again."

    # Search for the product in the DataFrame (exact match)
    result = df[df['ProductName'].str.contains(product_name, case=False, na=False)]

    # If no result from the basic search, apply regex matching
    if result.empty:
        result = regex_filter_products(product_name, df)

    # If still no results after regex matching
    if result.empty:
        return f"Sorry, I couldn't find the product '{product_name}' using both search and regex."

    # If there's only 1 result or a small number of results, return detailed info
    if len(result) == 1:
        product_details = "\n".join([
                                        f"\nProduct: {row['ProductName']} - Price: {row['Price']} - Stock: {row['StockQuantity']} - Description: {row['Description']}"
                                        f" - Rating: {row['Rating']} - Category: {row['Category']} - Cluster: {['Cluster Label']}"
                                        for index, row in result.iterrows()])
        prompt = f"""Here are the product details:\n{product_details}\n
        You are to give more details. You also need to give the rating of the product upon 5.
        Try to give the product name and its colour from the list. 
        If the product name is too long, you may use category and cluster label to descript the product.
        Please put it in a paragraph."""

        response, history = run_agent(prompt, st.session_state.history)

        # Display the model's response to the user
        st.write(f"**Chatbot:** \n{response}")
        # return response, prompt

    # If there are multiple results, show the top N results
    if len(result) > 1:
        # Handle multiple results scenario
        num_results = len(result)
        response = f"I found {num_results} product{'s' if num_results > 1 else ''} matching your query. Here are the top {num_results}:\n"
        for index, row in result.iterrows():
            response += f"\n{row['ProductName']} (ID: {row['Product ID']}) - {row['Price']}\n"
        response += "\nPlease be more specific to help narrow down the results."
        return response

def query_huggingface_model(messages):
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct",  # Replace with your model
        messages=messages,
        max_tokens=500,
        stream=False  # Not using streaming in this case for simplicity
    )
    return response['choices'][0]['message']['content']


def run_agent(query, history):
    history.append({"role": "user", "content": query})
    model_response = query_huggingface_model(history)
    history.append({"role": "assistant", "content": model_response})
    return model_response, history


def regex_filter_products(query, df):

    # Create a regex pattern from the user's query (convert to lowercase and add word boundaries)
    query = query.lower()
    pattern = ".*" + ".*".join([re.escape(keyword) for keyword in query.split()]) + ".*"

    filtered_df = df[df['ProductName'].str.contains(pattern, case=False, na=False, regex=True)]
    return filtered_df
def run_agent(query, history):
    history.append({"role": "user", "content": query})
    model_response = query_huggingface_model(history)
    history.append({"role": "assistant", "content": model_response})
    return model_response, history
def query_huggingface_model(messages):
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct",  # Replace with your model
        messages=messages,
        max_tokens=500,
        stream=False  # Not using streaming in this case for simplicity
    )
    return response['choices'][0]['message']['content']

def regex_filter_products(query, df):

    # Create a regex pattern from the user's query (convert to lowercase and add word boundaries)
    query = query.lower()
    pattern = ".*" + ".*".join([re.escape(keyword) for keyword in query.split()]) + ".*"

    filtered_df = df[df['ProductName'].str.contains(pattern, case=False, na=False, regex=True)]
    return filtered_df

def handle_product_comparison(query):
    match = re.search(r"between\s*(.*?)\s*and\s*(.*)", query, re.IGNORECASE)
    if match:
        product_a_name = match.group(1).strip()
        product_b_name = match.group(2).strip()

        product_a = df[df['ProductName'].str.contains(product_a_name, case=False, na=False)]

        # If product A is not found, try regex filter
        if product_a.empty:
            product_a = regex_filter_products(product_a_name, df)
            if product_a.empty:
                return f"Sorry, I couldn't find the product '{product_a_name}' using both search and regex."

        # Basic search for product B
        product_b = df[df['ProductName'].str.contains(product_b_name, case=False, na=False)]

        # If product B is not found, try regex filter
        if product_b.empty:
            product_b = regex_filter_products(product_b_name, df)
            if product_b.empty:
                return f"Sorry, I couldn't find the product '{product_b_name}' using both search and regex."

        product_a_details = ([
                                        f"\nProduct: {['ProductName']} - Price: {['Price']} - Stock: {['StockQuantity']} - Description: {['Description']}"
                                        f" - Rating: {['Rating']}"])
        print(product_a_details)
        product_b_details = ([
                                        f"\nProduct: {['ProductName']} - Price: {['Price']} - Stock: {['StockQuantity']} - Description: {['Description']}"
                                        f" - Rating: {['Rating']}"])
        print(product_b_details)

        prompt = f"""Here are the product a and b:\n{product_a_details}\n {product_b_details}\n
                You are to give more details but keep it short. You also need to give the rating of the product upon 5.
                Use 'vs' between two products instead of lines of each product if possible. 
                Use USD as the price for both.
                """
        response, history = run_agent(prompt, st.session_state.history)

        # Display the model's response to the user
        st.write(f"**Chatbot:** \n{response}")

    else:
        return "Sorry, I couldn't understand your comparison request. Please mention two products to compare."
