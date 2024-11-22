import streamlit as st
import category
import compare
history=[]

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("ShopWise 1.0 SimpleBot")

st.markdown("""
    <style>
        h1 {
            color: #FF6347;  /* Tomato color */
            font-family: 'Courier New', Courier, monospace;
        }
    </style>
""", unsafe_allow_html=True)
# User input query
query = st.text_input("Welcome to Shopwise!! Ask me anything regarding products!!:")

fridge_keywords = ['fridge', 'fridges', 'freezer']
microwave_keywords = ['microwave', 'microwaves']
phone_keywords = ['phone', 'phones' 'handphone', 'smart phone', 'android']
tvs_keywords = ['tv', 'television']
dishwasher_keywords = ['dishwasher', 'dish washer','dishwashers', 'dish washers']
cpus_keywords = ['cpu', 'cpus', 'amd', 'intel']
washing_machine_keywords = ['washingmachine', 'washing machine']
camera_keywords = ['camera', 'cameras']
if query:
    st.session_state.history.append({"role": "user", "content": query})

    if 'between' in query.lower() and 'and' in query.lower():
        # Handle the product comparison
        response = compare.handle_product_comparison(query)
        if 'other' in query.lower() or 'others' in query.lower() or 'or' in query.lower() and not 'tvs' in query.lower():
            prompt = f"""You can compare with any related phones in \n{category.phones}\n.
                            Use 'vs' between two products instead of lines of each product if possible. 
                            Use USD as the price for both.
                            """
            response, history = compare.run_agent(prompt, st.session_state.history)

            # Display the model's response to the user
            st.write(f"**Chatbot:** \n{response}")

    elif 'tell' in query.lower() or 'looking' in query.lower():
        response = compare.handle_product_query(query)
        st.write(f"**Chatbot:** {response}")


    elif 'order id' in query.lower():
        # Handle the order status check
        response = compare.handle_order_status_check(query)

    elif 'customer id' in query.lower():
        response = compare.handle_previous_orders(query)
        
    elif any(keyword in query.lower() for keyword in phone_keywords):
        prompt = f"""You are a chatbot answering any questions about the camera in \n {category.phones}\n. 
                You have to stick to the list and try to list down.
                You can recommend the best one. Do ask if they have a phone brand.
                Show in USD"""

        response, history = compare.run_agent(prompt, st.session_state.history)
        st.write(f"**Chatbot:** {response}")
    elif any(keyword in query.lower() for keyword in fridge_keywords):
        prompt = f"""You are a chatbot answering any questions about the fridge and freezer in \n {category.fridge, 
        category.fridge_freezer, category.freezer}\n. 
                You have to stick to the list and try to list down.
                You can recommend the best one. Show in USD"""

        response, history = compare.run_agent(prompt, st.session_state.history)
        st.write(f"**Chatbot:** {response}")
    elif any(keyword in query.lower() for keyword in camera_keywords):
        prompt = f"""You are a chatbot answering any questions about the camera in \n {category.camera}\n. 
                You have to stick to the list and try to list down.
                You can recommend the best one. Show in USD"""

        response, history = compare.run_agent(prompt, st.session_state.history)
        st.write(f"**Chatbot:** {response}")
    elif any(keyword in query.lower() for keyword in washing_machine_keywords):
        prompt = f"""You are a chatbot answering any questions about the washing machine in \n {category.washing_machine}\n. 
                You have to stick to the list and try to list down.
                You can recommend the best one. Show in USD"""

    elif any(keyword in query.lower() for keyword in dishwasher_keywords):
        prompt = f"""You are a chatbot answering any questions about the dish washer in \n {category.dish_washer}\n. 
                    You have to stick to the list and try to list down.
                    You can recommend the best one. Show in USD"""

        response, history = compare.run_agent(prompt, st.session_state.history)
        st.write(f"**Chatbot:** {response}")
    elif any(keyword in query.lower() for keyword in microwave_keywords):
        prompt = f"""You are a chatbot answering any questions about the microwave in \n {category.microwave}\n. 
                    You have to stick to the list and try to list down.
                    You can recommend the best one. Show in USD"""
        response, history = compare.run_agent(prompt, st.session_state.history)
        st.write(f"**Chatbot:** {response}")
        
    elif any(keyword in query.lower() for keyword in cpus_keywords):
        prompt = f"""You are a chatbot answering any questions about the cpus in \n {category.cpus}\n. 
                    You have to stick to the list and try to list down.
                    You can recommend the best one. Show in USD"""

        response, history = compare.run_agent(prompt, st.session_state.history)
        st.write(f"**Chatbot:** {response}")
        
    elif any(keyword in query.lower() for keyword in tvs_keywords):
        prompt = f"""You are a chatbot answering any questions about the TVs in \n {category.tvs}\n. 
                    You have to stick to the list and try to list down.\
                    You can recommend the best one. Show in USD"""

        response, history = compare.run_agent(prompt, st.session_state.history)
        st.write(f"**Chatbot:** {response}")

    else:
        # Use the model to generate a response for general queries
        prompt = f"""You are a chatbot for a e-commerce company with various items. Your main categories are in \n {category.product_categories}\n. 
        if user query are not asking about anything relate to the main categories, you must tell users to ask about the products.
        you can do simple chatting if user greet you. Only compare what is query, do not compare tv and phone for example."""

        response, history = compare.run_agent(prompt, st.session_state.history)
        st.write(f"**Chatbot:** {response}")


# Add a reset conversation button
if st.button("Reset Conversation"):
    st.session_state.history = []
    st.rerun()
