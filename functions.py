import re

# Mapping of restaurant names to their phone numbers and locations
restaurant_info = {
    "Alta Marea": {"phone": "+39302939202", "location": "https://maps.app.goo.gl/LwG4qztUhKkfgTJb9"},
    "L’Antico Carretto Siciliano": {"phone": "+3920492020", "location": "https://maps.app.goo.gl/yE1WUCEniPwcfpLU7"},
    "Ristorante Pizzeria Scirocco": {"phone": "+395039202", "location": "https://maps.app.goo.gl/46UB19uJCEGxNjpB8"}
}

# Mapping of brunch spots, cafes, and bars to their phone numbers and locations
breakfast_spot_info = {
    "Lido Hotel Bar": {"location": "https://maps.app.goo.gl/G1GGU1wS7dhZGL4y8"}
}

dessert_info = {
    "Pasticceria Dolce Barocco": {"location": "https://maps.app.goo.gl/RtT3M6sZSLBFPwSr6"},
    "Mangiafico": {"location": "https://maps.app.goo.gl/NusQ25eYyUNukqWaA"},
    "Candiano Noto": {"location": "https://maps.app.goo.gl/Snhnv4ksTL3VimqEA"},
}

street_food_info = {
    "Panineria Granata": {"location": "https://maps.app.goo.gl/kHJA89YtHCDRTXMZ7"},
    "Putia del Coppo": {"location": "https://maps.app.goo.gl/2auBJuMMZPcf9zpR9"}
}

# Mapping of tours with their descriptions and information links
winery_tours_info = {
    "Cantina Marillina": {"description": "Taste world-class wines and discover the winemaking process in Noto's wine country", "info": "https://www.cantinamarilina.com/"},
    "Feudo Maccari": {"description": "Venture into this up-and-coming wine region and visit boutique wineries offering unique varietals", "info": "https://www.callmewine.com/cantina/feudo-maccari-B696.htm"}
}

activities_info = {
    "Surf": {"info": "https://prowaveschool.it/en/corsi-noleggi-tour/"},
    "Windsurf": {"info": "https://prowaveschool.it/en/corsi-noleggi-tour/"},
    "Sup": {"info": "https://prowaveschool.it/en/corsi-noleggi-tour/"}
}

excursions_info = {
    "Baroque tour: Ragusa, Modica and Noto": {"description": "Discover the splendor of Sicilian Baroque architecture in a guided tour through Ragusa, Modica, and Noto.", "info": "https://www.viator.com/it-IT/tours/Aeolian-Islands/Private-Baroque-Tour-Ragusa-Modica-and-Noto/d30631-218384P1"},
    "Private tour of Syracuse, Ortigia and Noto": {"description": "Experience the rich history and beauty of Syracuse and Ortigia, followed by a visit to the Baroque city of Noto.", "info": "https://www.viator.com/tours/Catania/Private-Tour-of-Syracuse-and-Noto-from-Catania-or-Taormina/d22664-7736P18"},
    "Boat tour from Avola to Portopalo with a stop in Marzamemi": {"description": "Enjoy a scenic boat journey from Avola to Portopalo, including a delightful stop in the picturesque fishing village of Marzamemi.", "info": "https://www.viator.com/en-GB/tours/Sicily/Boat-tour-from-Avola-to-Portopalo-with-a-stop-in-Marzamemi/d205-215946P13"}
}

nearby_cities_info = {
    "Noto": {"description": "A Baroque masterpiece, known for its stunning architecture and historical charm. Located approximately 15 km away, the most convenient ways to reach it are by car or bus. Popular attractions include the Noto Cathedral, Palazzo Ducezio, and the Church of San Domenico.", "location": "https://maps.app.goo.gl/c7avy1L72phsnYGT9", "info": "https://youtu.be/Gptg_cKn8x8"},
    "Catania": {"description": "Bustling with lively markets and rich in historical and cultural heritage. Located approximately 97 km away, the most convenient ways to reach it are by car or bus. Popular attractions include Piazza del Duomo, the Castello Ursino, and the Teatro Romano.", "location": "https://maps.app.goo.gl/cU9ZhRUa1VRowydN9", "info": "https://youtu.be/YYN7gGlpLHk"},
    "Syracuse": {"description": "Ancient city famous for its Greek ruins and beautiful coastal scenery. Located approximately 36 km away, the most convenient ways to reach it are by car or bus. Popular attractions include the Greek Theatre, the Ear of Dionysius, and the Island of Ortigia.", "location": "https://maps.app.goo.gl/5bMgo7iHzm4GBGjv7", "info": "https://youtu.be/Yuuo12rUQvI"},
    "Ragusa": {"description": "A hilltop city with a picturesque old town and Baroque buildings. Located approximately 70 km away, the most convenient ways to reach it are by car or bus. Popular attractions include Ragusa Ibla, the Cathedral of San Giovanni Battista, and the Giardino Ibleo.", "location": "https://maps.app.goo.gl/BZUnixMSwKUaQAHB6", "info": "https://youtu.be/yqgcUEADJo0"},
    "Messina": {"description": "A port city offering panoramic views and historical landmarks. Located approximately 195 km away, the most convenient way to reach it is by train. Popular attractions include the Messina Cathedral, the Fountain of Orion, and the Sanctuary of Montalto.", "location": "https://maps.app.goo.gl/Nkh3eEVfTZs4xWTy7", "info": "https://youtu.be/R8kMjds2lTQ"},
    "Taormina": {"description": "Known for its ancient theatre and breathtaking views of the Ionian Sea. Located approximately 150 km away, the most convenient way to reach it is by train. Popular attractions include the Ancient Theatre of Taormina, Isola Bella, and the Corso Umberto.", "location": "https://maps.app.goo.gl/P3LsemieKFLREXmY9", "info": "https://youtu.be/kr-CF4uWpLQ"}
}

synonym_map = {'villa': 'property', 'Giardino Tropicale': 'property'}

def preprocess_query(query):
    for word in synonym_map:
        query = query.replace(word, synonym_map[word])
    return query

def handle_property_location_info(query, response):
    correct_address = "Via Gaetano Martino 12, 96017, Noto Marina, SR"
    incorrect_address = "55 Erskine Ave, Toronto, Canada"
    incorrect_link = "https://maps.app.goo.gl/uDtaQcNc7qTpZWZH6"
    maps_link = "https://maps.app.goo.gl/4jPot9eNtGfAU1Td9"
    location_related_phrases = ["property location", "property's location", "location of the property"]

    # Check if the query asks about the property's location
    if any(phrase in query.lower() for phrase in location_related_phrases):
      return f"The property is located at {correct_address}\nGoogle Maps Link: {maps_link}"

    # Replace incorrect link with correct link
    if incorrect_link in response:
        response = response.replace(incorrect_link, maps_link)

    # Correct the address if incorrect one is mentioned
    if incorrect_address in response:
        response = response.replace(incorrect_address, correct_address)

    # Append correct address if "The property is located" is mentioned but no address is provided
    elif "The property is located" in response and correct_address not in response:
        response += "\nThe property is located at " + correct_address

    # Append Google Maps link if not already present
    if 'Via Gaetano Martino 12' in response and maps_link not in response:
        response += "\nGoogle Maps Link: " + maps_link

    return response

def hospital_related_info(response):
    hospital_maps_link = "https://maps.app.goo.gl/gSyDVuqDdSyPCrQ36"
    if 'hospital' in response and hospital_maps_link not in response:
        response += "\nHospital's Location: " + hospital_maps_link
    return response

def format_medical_services_response(query, response):
    medical_maps_link = "https://maps.app.goo.gl/x4vg2miXTLmMqiR86"
    query_lower = query.lower()
    if 'medical' in query_lower and ('nearby' in query_lower or 'property' in query_lower or 'near' in query_lower):
      return "The medical services near the property are located at via Gaetano Martino 10, 96017, Noto, SR. Check this Google Maps link for the location: " + medical_maps_link
    else:
        return response

def atm_related_info(query, response):
    atm_maps_link = "https://maps.app.goo.gl/h6qHPD4mUujqtbSk8"
    query_lower = query.lower()
    if 'atm' in query_lower and 'property' in query_lower:
        return "Check this Google Maps link if you are looking for a ATM near the property: " + atm_maps_link
    else:
        return response

def grocery_related_info(query, response):
    grocery_maps_link = "https://maps.app.goo.gl/HFWxzzgjSufAtxdM6"
    query_lower = query.lower()

    # Check if the query is about a grocery store near the property
    if ('grocery store' in query_lower or 'minimarket' in query_lower or 'mini market' in query_lower) and 'property' in query_lower:
        # Add information about Summerhill Market only if it's not already in the response
        if 'La Bottega Minimarket' not in response and grocery_maps_link not in response:
            return "La Bottega Minimarket, open Mon-Sun, 8:30 to 13:45. Check this Google Maps link for the location: " + grocery_maps_link
    return response

def pharmacy_related_info(query, response):
    pharmacy_maps_link = "https://maps.app.goo.gl/LNHCZ12JrNSqAnVa8"
    query_lower = query.lower()

    # Check if the query is about a grocery store near the property
    if ('pharmacy' in query_lower or 'drugstore' in query_lower) and 'property' in query_lower:
           return "Check this Google Maps link for directions to the pharmacy near the property: " + pharmacy_maps_link
    return response

def post_related_info(query, response):
    post_maps_link = "https://maps.app.goo.gl/JuzQGnB6Sar2FCEdA"
    query_lower = query.lower()

    # Check if the query is about a grocery store near the property
    if ('post office' in query_lower or 'postal service' in query_lower) and 'property' in query_lower:

        if 'via Zanardelli 2, 96017, Noto, SR' not in response and post_maps_link not in response:
           return "Check this Google Maps link for directions to the post office near the property: " + post_maps_link
    return response

def police_related_info(query, response):
    police_maps_link = "https://maps.app.goo.gl/uCgsNambhaKc6PDm7"
    query_lower = query.lower()

    # Check if the query is about a grocery store near the property
    if ('police station' in query_lower or 'Police Department' in query_lower) and 'property' in query_lower:

        if 'SP, 96017, Noto, SR' not in response and police_maps_link not in response:
            return "Check this Google Maps link for directions to the police station near the property: " + police_maps_link
    return response

def kitchen_amenities_info(query, response):
    query_lower = query.lower()
    if 'amenities' in query_lower and 'kitchen' in query_lower:
        return "Stovetop, oven, kitchenware, microwave, refrigerator with freezer integrated, dishwasher, electric kettle, toaster, rice cooker, drip coffee maker, bowls, chopsticks, plates, cups"
    else:
        return response

def format_restaurant_response(query, response):
    # Lowercase the query for case-insensitive comparison
    query_lower = query.lower()

    # Determine the introductory text based on the query
    # Check if the query is related to restaurants
    restaurant_related_queries = ["near the property", "eat close the property", "nearby the property", "vegan", "takeout", "italian", "delivery", "seafood", "plant-based", "vegetarian", "take away", "takeaway", "to-go", "pasta", "pizza", "online order", "fish cuisine", "oceanic dishes", "close by dining", "restaurants nearby", "walking distance", "restaurant nearby"]
    if any(phrase in query_lower for phrase in restaurant_related_queries):
        intro_text = ""
        if "near the property" in query_lower or "nearby the property" in query_lower or "close by dining" in query_lower or "restaurants nearby" in query_lower or "walking distance" or "eat close the property" in query_lower or "restaurant nearby" in query_lower:
          intro_text = "Looking for a meal close to your stay? Here is a fantastic dining option just a stone's throw away:\n"
        elif "vegan" in query_lower or "plant-based" in query_lower or "vegetarian" in query_lower:
          intro_text = "This suggested restaurant has a selection of delightful vegan and vegetarian eateries:\n"
        elif "takeout" in query_lower or "take away" in query_lower or "takeaway" in query_lower or "to-go" in query_lower or "delivery" in query_lower or "online order" in query_lower:
          intro_text = "Check our suggested choice that offers both takeaway and delivery options:\n"
        elif "italian" in query_lower or "pasta" in query_lower or "pizza" in query_lower or "pasta alla norma" in query_lower or "peperonata" in query_lower:
          intro_text = "Experience the essence of Sicily with our handpicked Sicilian restaurants, from authentic pizzerias to gourmet pasta houses:\n"
        elif "seafood" in query_lower or "fish cuisine" in query_lower or "mediterranean dishes" in query_lower:
          intro_text = "Dive into a sea of flavors with our selection of the finest seafood restaurants, featuring fresh catches and exquisite oceanic dishes:\n"
        else:
          intro_text = "Embark on a gastronomic journey with these highly recommended restaurants:\n"  # Generic intro for other queries

        formatted_response = [intro_text]
        for restaurant, details in restaurant_info.items():
            if restaurant in response:
               # Replace "Phone" with "📞" and "Location" with "📍" for each restaurant
               formatted_response.append(f"• {restaurant}\n  📞: {details['phone']}\n  📍: {details['location']}\n")

        # Return formatted response if there are restaurant details
        if len(formatted_response) > 1:
            return '\n'.join(formatted_response)

    # If no restaurant details are found or the query is not restaurant-related, return the original response
    return response

def format_lifestyle_response(query, response):
    query_lower = query.lower()

    # Using regular expressions for more accurate keyword matching
    if re.search(r'\bbreakfast\b|\bmorning meal\b|\bbreakfast spots\b', query_lower):
        category_info = breakfast_spot_info
        intro_text = "Ready to kickstart your day? Check this breakfast spot near the property:\n"
    elif re.search(r'\bcafe\b|\bcoffee\b|\bespresso\b|\bcannolo\b|\bcannoli siciliani\b|\bcassata\b|\bdessert\b', query_lower):
        category_info = dessert_info
        intro_text = "Check out these places if you are looking for delicious Sicilian desserts and coffee:\n"
    elif re.search(r'\barancino\b|\barancine\b|\barancini\b|\bmeusa\b|\bfocacce\b|\bstreet food\b', query_lower):
            category_info = street_food_info
            intro_text = "If you are looking for the amazing Sicilian street food, check these places:\n"

    else:
        return response  # Return the original response if query is not related

    formatted_response = [intro_text]
    for place, details in category_info.items():
        formatted_response.append(f"• {place}\n  📍: {details['location']}\n")

    return '\n'.join(formatted_response)

def format_tour_response(query, response):
    query_lower = query.lower()

    if "winery tour" in query_lower or "wine tasting" in query_lower:
        category_info = winery_tours_info
        intro_text = "Check out these amazing winery tours:\n"
    else:
        return response  # Return the original response if the query is not related

    formatted_response = [intro_text]
    for tour, details in category_info.items():
        if tour in response:
            description = details["description"]
            info_link = f"Info: {details['info']}"
            formatted_response.append(f"• {tour}\n{description}\n{info_link}\n")

    return '\n'.join(formatted_response) if formatted_response else response

def format_activities_response(query, response):
    query_lower = query.lower()

    # Specific keywords for activity-related queries
    activity_keywords = ["activity", "activities", "outdoor fun", "surf", "sport", "sup", "windsurf"]
    # Keywords that indicate the query is not about activities
    non_activity_keywords = ["transportation", "airport", "reach", "travel", "bus", "train", "drive", "taxi", "shuttle"]

    # Check if the query is about activities and not about transportation
    if any(keyword in query_lower for keyword in activity_keywords) and not any(keyword in query_lower for keyword in non_activity_keywords):
        formatted_response = ["Check out these thrilling water sports in Noto Marina:\n"]
        for activity, details in activities_info.items():
            formatted_response.append(f"• {activity}\n  Info: {details['info']}\n")

        return '\n'.join(formatted_response)

    return response

def format_excursions_response(query, response):
    query_lower = query.lower()

    if "excursion" in query_lower or "exploration" in query_lower or "guided tour" in query_lower or "organized tours" in query_lower or "day trip" in query_lower:
        formatted_response = ["Embark on unforgettable excursions and explore the beauty around Toronto:\n"]
        for excursion, details in excursions_info.items():
            formatted_response.append(f"• {excursion}\n  {details['description']}\n  Info: {details['info']}\n")

        return '\n'.join(formatted_response)

    return response

def format_nearby_cities_response(query, response):
    query_lower = query.lower()

    if "nearby cities" in query_lower or "cities near the property" in query_lower or "nearby towns" in query_lower:
        formatted_response = ["Explore the rich Sicilian history and culture visiting these cities:\n"]
        for site, details in nearby_cities_info.items():
            formatted_response.append(f"• {site}\n  {details['description']}\n  📍: {details['location']}\n  Discover the city: {details['info']}\n")

        return '\n'.join(formatted_response)

    return response