import requests
import time
import json


# 1) Insert your Helpshift Domain:
domain = "YOUR_DOMAIN"

# 2) Update the number of pages - max is 50 when pagesize is 1000
pages = 50
i = 1
pagesize = 1000

f = open("bot-human-stats.csv", "w")
while i <= pages:
    url = 'https://api.helpshift.com/v1/' + domain + '/issues'
    
    querystring = {
    "page-size":"%s"%(pagesize),
    "page":"%s"%(i),"state":"resolved,rejected",
    "includes":"[\"meta\",\"custom_fields\"]",
    "sort-by": "creation-time",
    # 3) Optional Paramaters for your query
    #"app-ids":"[\"YOUR APP ID\"]",
    #"created_since": 1583020800000,
    #"created_until": 1583020800000
    #"platform-types":"[\"web\"]"
    }

    payload = ""

    headers = {
        # 4) Insert your Baisc Auth Key - Use https://apidocs.helpshift.com/ to run a test call 
        # and get your BASIC Key from the sample CURL Request 
        'Authorization': "Basic YOUR AUTH KEY ",
        'cache-control': "no-cache",
        }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

    print(response.text[0:500],"...")
    print("------------------ Page %s compelete------------------"%(i))
    
    #Write each line to a file
    x = json.loads(response.text)

    currentPage = 0
    if i == 1:
        f.write(f"issue_id,ttfr_human(mins),bot_to_human_hold_time(mins),reopens,human_outbound_messages,number_of_customer_messages,number_of_bot_messages,language,tags,created_timestamp,first_human_timestamp,previous_timestamp,first_agent_email\n")
   
    for item in x["issues"]:
        if str(item["redacted"]) == "False":
            issue_id = item["id"]
            language = "--"
            created = item["created_at"]
            app_publish_id = item["app_publish_id"]
            #author_email = str(item["author_email"])
            created_timestamp = item["messages"][0]["created_at"]
            ttfr_human = 0
            first_human_timestamp = 0
            human_outbound_messages = 0
            first_agent_email = ''
            number_of_customer_messages = 0
            number_of_bot_messages = 0
            bot_to_human_hold_time = 0
            previous_bot_timestamp = 0
            reopens = 0
            previous_timestamp = 0
            tags = '; '.join(item["tags"]).replace('\n', '').replace('\r', '')
            
            for message in item["messages"]:
                if message["origin"] == "helpshift" and message["author"]["emails"][0].startswith('bots-') == False and message["author"]["emails"][0].startswith('autobot') == False:
                    first_human_timestamp = message["created_at"]
                    first_agent_email = message["author"]["emails"][0]
                    bot_to_human_hold_time = first_human_timestamp - previous_timestamp


                    ttfr_human = message["created_at"] - created_timestamp

                    break
                else:
                    if message["author"]["emails"] != []:
                        if message["author"]["emails"][0].startswith('bots-') == True:
                            previous_timestamp = message["created_at"]

            for message in item["messages"]:
                if message["body"] == "Did not accept the solution":
                    reopens += 1

                if message["origin"] == "helpshift" and message["author"]["emails"][0].startswith('bots-') == False and message["author"]["emails"][0].startswith('autobot') == False:
                    human_outbound_messages += 1
                elif message["origin"] == "end-user" and message["body"] != "Accepted the solution":
                    number_of_customer_messages += 1
                elif message["author"]["emails"] == []:
                    number_of_customer_messages += 1
                elif message["author"]["emails"][0].startswith('bots-') == True and message["body"] != "Bot Ended" and message["body"] != "Bot Started" :
                    number_of_bot_messages += 1

            if human_outbound_messages > 0: 
                ttfr_human = round((ttfr_human/1000)/60,2)
                bot_to_human_hold_time = round((bot_to_human_hold_time/1000)/60,2)
            else:
                ttfr_human = "n/a"
                bot_to_human_hold_time = "n/a"
                first_agent_email = "n/a"

            if previous_timestamp == 0:
                bot_to_human_hold_time = "n/a"

            
            f.write(f"{issue_id},{ttfr_human},{bot_to_human_hold_time},{reopens},{human_outbound_messages},{number_of_customer_messages},{number_of_bot_messages},{language},{tags},{created_timestamp},{first_human_timestamp},{previous_timestamp},{first_agent_email}\n")
       
        
        else:
            print("Issue ID %s was redacted"%(item["id"]))

    print("------------------ Write Page %s compelete------------------"%(i))
        
    time.sleep(.25)
    i += 1


print("------------------ Download Complete ------------------")