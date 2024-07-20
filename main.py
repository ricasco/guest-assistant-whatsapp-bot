import re
import os
import requests
import openai
import logging
from flask import Flask, request, jsonify
from langchain_community.vectorstores import Qdrant
from langchain_openai.embeddings import OpenAIEmbeddings
import qdrant_client
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_openai.llms import OpenAI
from functions import preprocess_query, handle_property_location_info, hospital_related_info, format_medical_services_response, atm_related_info, kitchen_amenities_info, format_restaurant_response, format_lifestyle_response, format_tour_response, format_activities_response, format_excursions_response, format_nearby_cities_response, grocery_related_info, pharmacy_related_info, post_related_info, police_related_info

# Flask app for handling HTTP requests
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

# Set environment variables for the Qdrant service
os.environ['QDRANT_HOST'] = os.getenv("QDRANT_HOST")
os.environ['QDRANT_API_KEY'] = os.getenv("QDRANT_API_KEY")
os.environ['QDRANT_COLLECTION'] = os.getenv("QDRANT_COLLECTION")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# WhatsApp bot environment variables
token = os.environ['VERIFY_TOKEN']
whatsapp_token = os.environ['WHATSAPP_TOKEN']
whatsapp_url = os.environ['WHATSAPP_URL']
whatsapp_phone_number_id = os.environ['WHATSAPP_PHONE_NUMBER_ID']

interacted_users = {}  # Keep track of users who have interacted

DATABASE = None

# Create Qdrant client and collection
client = qdrant_client.QdrantClient(
    os.getenv("QDRANT_HOST"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_config = qdrant_client.http.models.VectorParams(
    size=1536,  # 768 for instructor-xl, 1536 for OpenAI
    distance=qdrant_client.http.models.Distance.COSINE
)

client.recreate_collection(
    collection_name=os.getenv("QDRANT_COLLECTION"),
    vectors_config=collection_config
)

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = Qdrant(
    client=client,
    collection_name=os.getenv("QDRANT_COLLECTION"),
    embeddings=embeddings
)

# Function to split text into chunks
def get_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=600,
        chunk_overlap=150,
        length_function=len
    )
    return text_splitter.split_text(text)

# Read and process the text file
with open("giardinonew.txt") as f:
    raw_text = f.read()
texts = get_chunks(raw_text)
vectorstore.add_texts(texts)

# Set up the retrieval-based QA chain
qa = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",  # Specify the appropriate chain type
    retriever=vectorstore.as_retriever()
)

# Define function to handle queries
def handle_query(query):
    # Invoke the QA model
    response = qa.invoke(query)

    # Debug: Print the response format
    print(f"Raw response from qa.invoke: {response}")

    # Extract the text part from the response
    # Update this part based on the actual format of `response`
    response_text = response.get('result', '') if isinstance(response, dict) else response

    # Process the response text with your custom functions
    processed_query = preprocess_query(query)
    response_text = atm_related_info(processed_query, response_text)
    response_text = grocery_related_info(processed_query, response_text)
    response_text = pharmacy_related_info(processed_query, response_text)
    response_text = post_related_info(processed_query, response_text)
    response_text = police_related_info(processed_query, response_text)
    response_text = format_restaurant_response(processed_query, response_text)
    response_text = format_lifestyle_response(processed_query, response_text)
    response_text = format_tour_response(processed_query, response_text)
    response_text = format_activities_response(processed_query, response_text)
    response_text = format_excursions_response(processed_query, response_text)
    response_text = format_nearby_cities_response(processed_query, response_text)

    response_text = handle_property_location_info(processed_query, response_text)
    response_text = hospital_related_info(response_text)
    response_text = format_medical_services_response(processed_query, response_text)
    response_text = kitchen_amenities_info(processed_query, response_text)

    return response_text

# Function to send WhatsApp messages
def send_whatsapp_message(sender_id, message_type, content):
    print(f"Sending message to {sender_id}: {content}")
    headers = {
        "Authorization": f"Bearer {whatsapp_token}"
    }

    # Extract only the result from the content if it's a dictionary
    if isinstance(content, dict):
        message_body = content.get('result', '')
    else:
        message_body = content

    if message_type == "text":
        data = {
            "recipient_type": "individual",
            "to": sender_id,
            "type": "text",
            "messaging_product": "whatsapp",
            "text": {
                "body": message_body
            }
        }
    elif message_type == "interactive":
         data = {
            "recipient_type": "individual",
            "to": sender_id,
            "type": "interactive",
            "messaging_product": "whatsapp",
            "interactive": content
        }
    response = requests.post(whatsapp_url, headers=headers, json=data)
    print(response.json())  # To debug and see the response from the WhatsApp API
    if sender_id in interacted_users:
      interacted_users[sender_id]['processing'] = False

@app.route('/')
def index():
      return "Welcome to the WhatsApp Bot Knowledge Base!"

def ensure_response(func):
  def wrapper(*args, **kwargs):
    result = func(*args, **kwargs)
    if result is None:
        return jsonify(status='success'), 200
    return result
  return wrapper

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Facebook webhook verification
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if verify_token == os.environ['VERIFY_TOKEN']:
            return challenge, 200
        return 'Verification token mismatch', 403

    try:
        body = request.json
        logging.info(f"Received request: {body}")  # Log incoming request

        # Ensure the webhook body has the expected structure
        if not body or 'entry' not in body or not body['entry'] or 'changes' not in body['entry'][0] or not body['entry'][0]['changes']:
            logging.info("Unexpected webhook structure. Ignoring.")
            return jsonify(status='success'), 200

        # Check if it's a status update instead of a message
        if 'statuses' in body['entry'][0]['changes'][0]['value']:
            logging.info("Received a status update. Ignoring.")
            return jsonify(status='success'), 200

        if 'messages' in body['entry'][0]['changes'][0]['value']:
            sender_id = body['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
            messages = body['entry'][0]['changes'][0]['value']['messages']

            if messages and 'type' in messages[0]:
                message_id = messages[0].get('id')
                message_type = messages[0]['type']

                user_state = interacted_users.setdefault(sender_id, {'processing': False, 'greeted': False, 'last_msg_id': None})
                logging.info(f"User {sender_id} - Last Msg ID: {user_state['last_msg_id']}, Current Msg ID: {message_id}")

                if user_state['last_msg_id'] == message_id:
                    logging.info("Duplicate message detected, ignoring.")
                    return jsonify(status='success'), 200

                user_state['last_msg_id'] = message_id  # Update the last message ID


                # Handle text messages
                if message_type == 'text':
                    user_message = messages[0]['text']['body']


                    if not user_state['greeted']:    
                        send_whatsapp_message(sender_id, "text", '''Hello! 👋
I'm Leo, your virtual guide during your stay in Giardino Tropicale! 🌴

I'm here to assist you with any inquiries about the property and to recommend local spots for tasty food and fun activities. Looking for info? Just click on "Ask me Anything"! 🍽️ 🚴

For emergencies or specific requests, you can reach out to the owner directly by clicking the dedicated button or by typing something like "I want to talk to the owner", and I'll connect you promptly 🆘

Feel free to explore all my features and ask me anything! 
I'm here to make your stay as enjoyable as possible! 😃''')
                            

                        # Interactive Message
                        interactive_content = {
                            "type": "button",
                            "header": {
                                "type": "image",
                                "image": {
                                    "link": "https://i.ibb.co/DD1sJTb/giardino-tropicale-copia.jpg"
                                }
                            },
                            "body": {
                                "text": "How may I assist you today?"
                            },
                            "action": {
                                "buttons": [
                                    {
                                        "type": "reply",
                                        "reply": {
                                            "id": "text_1",
                                            "title": "Ask Me Anything"
                                        }
                                    },
                                    {
                                        "type": "reply",
                                        "reply": {
                                            "id": "text_2",
                                            "title": "Contact the Owner"
                                        }
                                    }
                                ]
                            }
                        }
                        send_whatsapp_message(sender_id, "interactive", interactive_content)
                        user_state['greeted'] = True
                        user_state['processing'] = False
                        return jsonify(status='success'), 200

                    else:
                        # Process and respond to user's query
                        response = handle_query(user_message)

                        send_whatsapp_message(sender_id, "text", response)
                        user_state['processing'] = False
                        return jsonify(status='success'), 200

                # Handle button clicks (interactive messages)
                elif message_type == 'interactive':
                    button_id = messages[0]['interactive']['button_reply']['id']

                    if button_id == "text_1":
                        send_whatsapp_message(sender_id, "text", '''I'm here for you!
Feel free to ask me any questions regarding Giardino Tropicale, essential services nearby or recommend local spots for tasty food and fun activities! 

Fire away!''')
                        return jsonify(status='success'), 200
                    elif button_id == "text_2":
                        # New interactive message content for button_id "text_2"
                        interactive_content_text_2 = {
                            "type": "button",
                            "body": {
                                "text": '''Should you need to get in touch directly, you can reach Gioacchino, the owner, at +3934343434. Alternatively, feel free to send him a message on WhatsApp: https://wa.me/393270656565.

If you are in a real emergency don't forget this number:
Ambulance: 118
Police: 113
Fire Department: 115 
EU Emergency number: 112'''
                            },
                            "action": {
                                "buttons": [
                                    {
                                        "type": "reply",
                                        "reply": {
                                            "id": "text_1",
                                            "title": "Ask Me Anything"
                                        }
                                    }
                                ]
                            }
                        }
                        send_whatsapp_message(sender_id, "interactive", interactive_content_text_2)
                        return jsonify(status='success'), 200
                    else:
                        logging.info("Message type not found.")
                        return jsonify(status='success'), 200
                else:
                    logging.info("Received a non-message webhook event. Ignoring.")

                user_state['processing'] = False
                interacted_users[sender_id] = user_state  # Update the user state in the dictionary

                return jsonify(status='success'), 200
            else:
                logging.info("No valid message type found.")
                return jsonify(status='success'), 200

    except Exception as e:
        logging.error(f"Error: {e}")  # Log errors
        return jsonify(status='error'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

