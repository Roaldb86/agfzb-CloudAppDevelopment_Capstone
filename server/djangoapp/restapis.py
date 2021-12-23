
import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth



# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        if 'api_key' in kwargs:
            response = requests.get(
                url,
                headers={'Content-Type': 'application/json'},
                params=kwargs,
                auth=HTTPBasicAuth('apikey', kwargs.api_key)
            )
        else:
            response = requests.get(
                url,
                headers={'Content-Type': 'application/json'},
                params=kwargs,
            )

    except Exception as e:
        # If any error occurs
        print("Network exception occurred")

    else:
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data

def post_request(url, json_payload, **kwargs):
    json_obj = json_payload["review"]
    print(kwargs)
    try:
        response = requests.post(url, json=json_obj, params=kwargs)
    except:
        print("Error")

    print(response)
    return response

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, **kwargs)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            print(dealer_obj)
            results.append(dealer_obj)

    return results

def analyze_review_sentiments(dealerreview):

    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/db5d92f1-d49d-4cef-9a8d-510cfa7e33f7"

    params = dict()
    params['text'] = dealerreview
    params['version'] = "2020-08-01"
    params['feature'] = "sentiment"
    params['return_analyzed_text'] = True
    params['api_key'] = "AesUBkcuNAgUciOUxyjZ_QfTzy8HUunhNnnXoMjthC56"

    response = get_request(url, **params)
    return response

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    json_result = get_request(url, id=dealerId)
    if json_result:
        reviews = json_result['docs']
        for review in reviews:
            try:
                review_obj = DealerReview(
                    name=review["name"],
                    dealership=review["dealership"],
                    review=review["review"],
                    purchase=review["purchase"],
                    purchase_date=review["purchase_date"],
                    car_make=review['car_make'],
                    car_model=review['car_model'],
                    car_year=review['car_year'],
                    sentiment="none",
                    )
            except Exception:
                print('error')
                review_obj = None

            else:
                review_obj.sentiment = analyze_review_sentiments(review_obj.review)
                if review_obj.sentiment == None:
                    review_obj.sentiment = 'neutral'

            results.append(review_obj)

    return results






