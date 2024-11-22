# LLaKata

LLamaKata is a chatbot for shopwise. It uses LLama 3.2 by huggingface.

Using Pandas as a DataFrame to get infomation from the CSV, merge before hand.

We uses Streamlit for the chatbot to place our chatbot to the webside 
# https://llakata-aikata2024.streamlit.app/

We use various keywords to have the chatbot seek different item such as phone, tvs.
# Example

- ProductName Search:
We use key phrases like 'i'm looking for' or 'tell me about' in query to seek out the product name. If the product name for example, 'iphone' which is too vague, a list with 'iphone' will return

- Category Search:
We use keywords in the 10 category such that when the query contains category related keyword 'cpu', 'dishwasher' or other, all the related products will be in the prompt of the chatbot.
This affects the token limit, however, it gave the best information from the csv to the customer.

- Order ID Search:
Use the keywords 'return' or 'status in query and have 'order id' followed by the number for example 'check order id 1122 for return' will reply you with your product details.

- Customer ID Search
Use the key phrase 'customer ID is' followed by number, for example, 'customer ID is 32' will return all the customer's orders.  

# What and Why

We choose LLama as a open source API as my team agreed that the chatbot is still a new to the shop. 
It is unwise to use a close source API for the shop because the customers might not even like the chatbot to begin with.
Moreover customers details are privacy, it is safer to use a open source over a close source.
We tried to keep the data to be as close as possible.

# Please do refresh the page as some time query history might reach the token limit.

# Archtecture

![Screenshot 2024-11-22 173018](https://github.com/user-attachments/assets/a1834a61-1856-4d2b-bc0d-8767c9b50e68)

# image of chatbot
![image](https://github.com/user-attachments/assets/effcd7d3-5631-4190-a64d-aaa69534f2e2)


