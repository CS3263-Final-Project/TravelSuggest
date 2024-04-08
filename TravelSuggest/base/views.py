from django.shortcuts import render, redirect
from .models import QueryData, ResultData
from .forms import QueryForm
import google.generativeai as genai
import json


def home(request):
    queryForm = QueryForm()                                     # QueryForm(instance=queryData)

    if request.method == 'POST':
        form = QueryForm(request.POST)                          # form = QueryForm(request.POST, instance=queryData) to repplace existing query
        if form.is_valid():
            query = form.save()
            return redirect('result', pk=query.id)
    
    data = {'QueryForm': queryForm}
    return render(request, 'base/home.html', data)

def result(request, pk): 
    queryData = QueryData.objects.get(id=pk)
    query_prompt = {
        'location': queryData.location,
        'criteria': queryData.criteria,
        'days': queryData.duration,
        'budget': queryData.budget,
    }

    print(str(query_prompt))
    resultData = generate_travel_suggestions(str(query_prompt))

    print(resultData)
    
    data = {'QueryData': queryData, 
            'ResultsData': resultData,
            }
    return render(request, 'base/result.html', data)

def generate_travel_suggestions(travel_query):

    genai.configure(api_key="AIzaSyCmfBtuVVD88DVXwXlJfK6wxz7V1zHsVVg")

    generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                        generation_config=generation_config,
                        safety_settings=safety_settings)
    
    prompt_parts = [
        "Given a travel location, corresponding travel duration, travel budget in Singaporean dollars, and additional travel requirements/constraints (e.g. I prefer the outdoors.).\n" +
        "Generate travel suggestions for that location in a python List Dictionary format for use in Django. Consider including restaurants as part of the travel suggestions. \n" +

        "Here are the needed label keys for the dictionary: \n" +
        "day_of_travel, location, time, description, expected_spending, additional_details, image, coordinates\n" +

        "Here is a brief description of each label key: \n" +
        "day_of_travel: This is the day of travel. It should be stored as an integer. E.g. 1, 2, ... \n" +
        "location: The suggested location of travel.\n" +
        "time: This is time of travel during the day. E.g. Morning, Afternoon, Evening, Night, Breakfast, Lunch, Dinner.\n" +
        "description: This is a brief description of the suggested location. Minimum 3 lines.\n" +
        "expected_spending: This is the expected spending for that suggested location. It should be a range. So a string format would be fine. This should be in the local currency of the travel country and Singaporean dollar.  E.g Going Malaysia. \"expected_spending\": \"SGD20 - SGD50 . MYR 70 - MYR 175\" \n" +
        "additional_details: This is the additional details for the suggested location. E.g. Remember to bring sunscreen, not much shaded error.\n" +
        "image: This is an generated image of the location. It should be a valid absolute url with an image. You can check this by going to the url.\n" +
        "coordinates: This is the coordinates of the location. It should be callable by the google maps api.\n" +

        "Very Important things to take note of: \n" +
        "Travel suggestions should satisfy the travel requirements as much as possible .\n" +
        "Format return result so that passing response.text to json.loads returns a python list dictionary.\n" +
        "No use of ' or ' throughout what is returned. \n" +
        "There must be no use of \\n. For the return output. Meaning return output must be in a single line.\n" +
        "Returned Dictionary key and Dictionary values which are Strings must be in \"\" and thus there should be no use of ' or '.\n" +

        "Here is an example input, it will be a python dict: \n" +
        "{'location': 'Johor', 'criteria': 'I want to experience the night life.', 'days': 2, 'budget': Decimal('2000.00')}" +
        "Here is an example output: \n" + 
        '[{"day_of_travel": 1, "location": "Zenith Lifestyle Village", "time": "Night", "description": "Zenith Lifestyle Village is a popular night spot located in Johor Bahru. It is home to a variety of bars, clubs, and restaurants, and is a great place to experience the citys nightlife. There is something for everyone at Zenith Lifestyle Village, whether youre looking to dance the night away or just relax and have a few drinks.", "expected_spending": "SGD50 - SGD100 . MYR 175 - MYR 350", "additional_details": "The dress code is casual, and the atmosphere is relaxed and friendly.", "image": "https://media.timeout.com/images/103498/image.jpg", "coordinates": "-1.491485116179, 103.76226405110699"}, {"day_of_travel": 1, "location": "R&F Mall", "time": "Evening", "description": "R&F Mall is a large shopping mall located in Johor Bahru. It is home to a variety of shops, restaurants, and a cinema and is a popular place to hang out at in the evening. There is something for everyone at R&F Mall, whether youre looking to do some shopping, grab a bite to eat, or catch a movie.", "expected_spending": "SGD20 - SGD50 . MYR 70 - MYR 175", "additional_details": "The mall is air-conditioned and has a variety of amenities, including a food court, a cinema, and a playground.", "image": "https://www.johornow.com/wp-content/uploads/2020/06/RF-Mall-Johor-Bahru-795x450.jpg", "coordinates": "1.4854, 103.7692"}, {"day_of_travel": 2, "location": "Legoland Malaysia", "time": "Morning", "description": "Legoland Malaysia is a theme park located in Johor Bahru. It is the first Legoland theme park in Asia and is based on the popular Lego toys. Legoland Malaysia is a great place to visit for families with young children, as there are many rides and attractions that are suitable for all ages.", "expected_spending": "SGD50 - SGD100 . MYR 175 - MYR 350", "additional_details": "The park is open from 10am to 6pm daily.", "image": "https://www.legoland.com.my/explore-the-park/theme-park/miniland/", "coordinates": "1.4721, 103.634"}, {"day_of_travel": 2, "location": "Johor Premium Outlets", "time": "Afternoon", "description": "Johor Premium Outlets is a large outlet mall located in Johor Bahru. It is home to a variety of outlet stores, including brands such as Nike, Adidas, and Coach. Johor Premium Outlets is a great place to find bargains on designer goods.", "expected_spending": "SGD50 - SGD100 . MYR 175 - MYR 350", "additional_details": "The mall is open from 10am to 10pm daily.", "image": "https://www.premiumoutlets.com.my/wp-content/uploads/2020/11/hero-johor-premium-outlets-1920x600.jpg", "coordinates": "2.079, 103.322"}, {"day_of_travel": 2, "location": "Danga Bay", "time": "Evening", "description": "Danga Bay is a waterfront development located in Johor Bahru. It is home to a variety of restaurants, bars, and shops, and is a popular place to hang out at in the evening. Danga Bay is also home to the Danga Bay Park, which is a great place to relax and enjoy the views of the Johor Strait.", "expected_spending": "SGD20 - SGD50 . MYR 70 - MYR 175", "additional_details": "There are many seafood restaurants in Danga Bay, so it is a great place to try some of the local cuisine.", "image": "https://travel.syioknya.com/images/johor/danga-bay.jpg", "coordinates": "1.4366, 103.8395"}]' +
        "Here is the input: \n" + travel_query
    ]   

    response = model.generate_content(prompt_parts)
    print(str(response.text))
    return json.loads(response.text)