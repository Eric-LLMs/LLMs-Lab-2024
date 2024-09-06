import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

from Utils import print_json
from POI import POI

_ = load_dotenv(find_dotenv())


if __name__ == "__main__":
    client = OpenAI()
    amap_key = "22b34521f11ce01f5744ffa28893cmef"

    poi = POI(client, amap_key)

    prompt = "I am on a business trip to Beijing, recommend hotels in Sanlitun and cafes near Wudaokou." # Requesting two function calls in one request
    # prompt = "I want to have coffee near Wudaokou in Beijing, please recommend some places."

    messages = [
        {"role": "system", "content": "You are a map expert who can find any address."},
        {"role": "user", "content": prompt}
    ]

    response = poi.get_completion(messages)
    messages.append(response)  # Add the model's response to the conversation
    print("===== GPT Response =====")
    print_json(response)

    while response.tool_calls is not None:
        # Support multiple Function-Calling requests in one response, so handle this situation
        for tool_call in response.tool_calls:
            args = json.loads(tool_call.function.arguments)
            print("Function arguments:")
            print_json(args)

            # Function routing
            if tool_call.function.name == "get_location_coordinate":
                print("Call: get_location_coordinate")
                result = poi.get_location_coordinate(**args)
            elif tool_call.function.name == "search_nearby_pois":
                print("Call: search_nearby_pois")
                result = poi.search_nearby_pois(**args)

            print("===== Function Return =====")
            print_json(result)

            messages.append({
                "tool_call_id": tool_call.id,  # Identifier for the Function-Calling ID
                "role": "tool",
                "name": tool_call.function.name,
                "content": str(result)  # The result value must be converted to a string
            })

        response = poi.get_completion(messages)
        print_json(response)
        messages.append(response)  # Add the model's response to the conversation

    print("===== Final Response =====")
    print(response.content)
    print("===== Conversation History =====")
    print_json(messages)


# The process tracking is as follows:

# ************************************************************************************************************************

#******************* prompt = "I am on a business trip to Beijing, recommend hotels in Sanlitun and cafes near Wudaokou." # Requesting two function calls in one request ***********
#
# ===== GPT Response =====
# {
#     "content": null,
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": [
#         {
#             "id": "call_ReHB3gGH27JdjueiYxNqTlc3",
#             "function": {
#                 "arguments": "{\"location\": \"三里屯\", \"city\": \"北京\"}",
#                 "name": "get_location_coordinate"
#             },
#             "type": "function"
#         },
#         {
#             "id": "call_rSsQviBwZl6fQNSHgowCeIah",
#             "function": {
#                 "arguments": "{\"location\": \"五道口\", \"city\": \"北京\"}",
#                 "name": "get_location_coordinate"
#             },
#             "type": "function"
#         }
#     ],
#     "refusal": null
# }
# Function arguments:
# {
#     "location": "三里屯",
#     "city": "北京"
# }
# Call: get_location_coordinate
# https://restapi.amap.com/v5/place/text?key=22b34521f11ce01f5744ffa28893cmef&keywords=三里屯&region=北京
# ===== Function Return =====
# {
#     "parent": "",
#     "address": "朝阳区",
#     "distance": "",
#     "pcode": "110000",
#     "adcode": "110105",
#     "pname": "北京市",
#     "cityname": "北京市",
#     "type": "地名地址信息;热点地名;热点地名",
#     "typecode": "190700",
#     "adname": "朝阳区",
#     "citycode": "010",
#     "name": "三里屯",
#     "location": "116.455294,39.937492",
#     "id": "B0FFF5BER7"
# }
# Function arguments:
# {
#     "location": "五道口",
#     "city": "北京"
# }
# Call: get_location_coordinate
# https://restapi.amap.com/v5/place/text?key=22b34521f11ce01f5744ffa28893cmef&keywords=五道口&region=北京
# ===== Function Return =====
# {
#     "parent": "",
#     "address": "海淀区",
#     "distance": "",
#     "pcode": "110000",
#     "adcode": "110108",
#     "pname": "北京市",
#     "cityname": "北京市",
#     "type": "地名地址信息;热点地名;热点地名",
#     "typecode": "190700",
#     "adname": "海淀区",
#     "citycode": "010",
#     "name": "五道口",
#     "location": "116.338611,39.992552",
#     "id": "B000A8WSBH"
# }
# {

#     "content": null,
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": [
#         {
#             "id": "call_pQ0Cj4YoQb428mLJYV8mOdQL",
#             "function": {
#                 "arguments": "{\"longitude\": \"116.455294\", \"latitude\": \"39.937492\", \"keyword\": \"hotel\"}",
#                 "name": "search_nearby_pois"
#             },
#             "type": "function"
#         },
#         {
#             "id": "call_G67iuHqCxng4HaRoqJpSMofo",
#             "function": {
#                 "arguments": "{\"longitude\": \"116.338611\", \"latitude\": \"39.992552\", \"keyword\": \"cafe\"}",
#                 "name": "search_nearby_pois"
#             },
#             "type": "function"
#         }
#     ],
#     "refusal": null
# }
# Function arguments:
# {
#     "longitude": "116.455294",
#     "latitude": "39.937492",
#     "keyword": "hotel"
# }
# Call: search_nearby_pois
# https://restapi.amap.com/v5/place/around?key=22b34521f11ce01f5744ffa28893cmef&keywords=hotel&location=116.455294,39.937492
# ===== Function Return =====
# 秋果酒店(三里屯太古里店)
# 三里屯路11号院三里屯太古里北区L1层
# Distance: 98 meters
#
# 三里屯太古里旗舰店(幸福三村小街店)
# 三里屯路11号三里屯太古里北区
# Distance: 103 meters
#
# 北京三里屯太古里CitiGO欢阁酒店
# 三里屯新东路12号院南区3号楼
# Distance: 359 meters
#
#
# Function arguments:
# {
#     "longitude": "116.338611",
#     "latitude": "39.992552",
#     "keyword": "cafe"
# }
# Call: search_nearby_pois
# https://restapi.amap.com/v5/place/around?key=22b34521f11ce01f5744ffa28893cmef&keywords=cafe&location=116.338611,39.992552
# ===== Function Return =====
# PAGEONE CAFE(五道口购物中心店)
# 成府路28号五道口购物中心(五道口地铁站B南口步行190米)
# Distance: 9 meters
#
# 星巴克(北京五道口购物中心店)
# 成府路28号1层101-10B及2层201-09号
# Distance: 39 meters
#
# luckin coffee 瑞幸咖啡(五道口购物中心店)
# 成府路28号五道口购物中心负一层101号
# Distance: 67 meters
#
#
# {
#     "content": "### Hotels in Sanlitun:\n1. **秋果酒店(三里屯太古里店)**\n   - Address: 三里屯路11号院三里屯太古里北区L1层\n   - Distance: 98 meters\n\n2. **三里屯太古里旗舰店(幸福三村小街店)**\n   - Address: 三里屯路11号三里屯太古里北区\n   - Distance: 103 meters\n\n3. **北京三里屯太古里CitiGO欢乐酒店**\n   - Address: 三里屯新东路12号院南区3号楼\n   - Distance: 359 meters\n\n### Cafes near Wudaokou:\n1. **PAGEONE CAFE(五道口购物中心店)**\n   - Address: 成府路28号五道口购物中心(五道口地铁站B南口步行190米)\n   - Distance: 9 meters\n\n2. **星巴克(北京五道口购物中心店)**\n   - Address: 成府路28号1号楼101-10B及2号楼201-09号\n   - Distance: 39 meters\n\n3. **luckin coffee 瑞幸咖啡(五道口购物中心店)**\n   - Address: 成府路28号五道口购物中心负一楼101号\n   - Distance: 67 meters\n\nEnjoy your stay and coffee in Beijing!",
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": null,
#     "refusal": null
# }
# ===== Final Response =====
# ### Hotels in Sanlitun:
# 1. **秋果酒店(三里屯太古里店)**
#    - Address: 三里屯路11号院三里屯太古里北区L1层
#    - Distance: 98 meters
#
# 2. **三里屯太古里旗舰店(幸福三村小街店)**
#    - Address: 三里屯路11号三里屯太古里北区
#    - Distance: 103 meters
#
# 3. **北京三里屯太古里CitiGO欢乐酒店**
#    - Address: 三里屯新东路12号院南区3号楼
#    - Distance: 359 meters
#
# ### Cafes near Wudaokou:
# 1. **PAGEONE CAFE(五道口购物中心店)**
#    - Address: 成府路28号五道口购物中心(五道口地铁站B南口步行190米)
#    - Distance: 9 meters
#
# 2. **星巴克(北京五道口购物中心店)**
#    - Address: 成府路28号1号楼101-10B及2号楼201-09号
#    - Distance: 39 meters
#
# 3. **luckin coffee 瑞幸咖啡(五道口购物中心店)**
#    - Address: 成府路28号五道口购物中心负一楼101号
#    - Distance: 67 meters
#
# Enjoy your stay and coffee in Beijing!
# ===== Conversation History =====
# {
#     "role": "system",
#     "content": "You are a map expert who can find any address."
# }
# {
#     "role": "user",
#     "content": "I am on a business trip to Beijing, recommend hotels in Sanlitun and cafes near Wudaokou."
# }
# {
#     "content": null,
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": [
#         {
#             "id": "call_ReHB3gGH27JdjueiYxNqTlc3",
#             "function": {
#                 "arguments": "{\"location\": \"三里屯\", \"city\": \"北京\"}",
#                 "name": "get_location_coordinate"
#             },
#             "type": "function"
#         },
#         {
#             "id": "call_rSsQviBwZl6fQNSHgowCeIah",
#             "function": {
#                 "arguments": "{\"location\": \"五道口\", \"city\": \"北京\"}",
#                 "name": "get_location_coordinate"
#             },
#             "type": "function"
#         }
#     ],
#     "refusal": null
# }
# {
#     "tool_call_id": "call_ReHB3gGH27JdjueiYxNqTlc3",
#     "role": "tool",
#     "name": "get_location_coordinate",
#     "content": "{'parent': '', 'address': '朝阳区', 'distance': '', 'pcode': '110000', 'adcode': '110105', 'pname': '北京市', 'cityname': '北京市', 'type': '地名地址信息;热点地名;热点地名', 'typecode': '190700', 'adname': '朝阳区', 'citycode': '010', 'name': '三里屯', 'location': '116.455294,39.937492', 'id': 'B0FFF5BER7'}"
# }
# {
#     "tool_call_id": "call_rSsQviBwZl6fQNSHgowCeIah",
#     "role": "tool",
#     "name": "get_location_coordinate",
#     "content": "{'parent': '', 'address': '海淀区', 'distance': '', 'pcode': '110000', 'adcode': '110108', 'pname': '北京市', 'cityname': '北京市', 'type': '地名地址信息;热点地名;热点地名', 'typecode': '190700', 'adname': '海淀区', 'citycode': '010', 'name': '五道口', 'location': '116.338611,39.992552', 'id': 'B000A8WSBH'}"
# }
# {
#     "content": null,
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": [
#         {
#             "id": "call_pQ0Cj4YoQb428mLJYV8mOdQL",
#             "function": {
#                 "arguments": "{\"longitude\": \"116.455294\", \"latitude\": \"39.937492\", \"keyword\": \"hotel\"}",
#                 "name": "search_nearby_pois"
#             },
#             "type": "function"
#         },
#         {
#             "id": "call_G67iuHqCxng4HaRoqJpSMofo",
#             "function": {
#                 "arguments": "{\"longitude\": \"116.338611\", \"latitude\": \"39.992552\", \"keyword\": \"cafe\"}",
#                 "name": "search_nearby_pois"
#             },
#             "type": "function"
#         }
#     ],
#     "refusal": null
# }
# {
#     "tool_call_id": "call_pQ0Cj4YoQb428mLJYV8mOdQL",
#     "role": "tool",
#     "name": "search_nearby_pois",
#     "content": "秋果酒店(三里屯太古里店)\n三里屯路11号院三里屯太古里北区L1层\nDistance: 98 meters\n\n三里屯太古里旗舰店(幸福三村小街店)\n三里屯路11号三里屯太古里北区\nDistance: 103 meters\n\n北京三里屯太古里CitiGO欢阁酒店\n三里屯新东路12号院南区3号楼\nDistance: 359 meters\n\n"
# }
# {
#     "tool_call_id": "call_G67iuHqCxng4HaRoqJpSMofo",
#     "role": "tool",
#     "name": "search_nearby_pois",
#     "content": "PAGEONE CAFE(五道口购物中心店)\n成府路28号五道口购物中心(五道口地铁站B南口步行190米)\nDistance: 9 meters\n\n星巴克(北京五道口购物中心店)\n成府路28号1层101-10B及2层201-09号\nDistance: 39 meters\n\nluckin coffee 瑞幸咖啡(五道口购物中心店)\n成府路28号五道口购物中心负一层101号\nDistance: 67 meters\n\n"
# }
# {
#     "content": "### Hotels in Sanlitun:\n1. **秋果酒店(三里屯太古里店)**\n   - Address: 三里屯路11号院三里屯太古里北区L1层\n   - Distance: 98 meters\n\n2. **三里屯太古里旗舰店(幸福三村小街店)**\n   - Address: 三里屯路11号三里屯太古里北区\n   - Distance: 103 meters\n\n3. **北京三里屯太古里CitiGO欢乐酒店**\n   - Address: 三里屯新东路12号院南区3号楼\n   - Distance: 359 meters\n\n### Cafes near Wudaokou:\n1. **PAGEONE CAFE(五道口购物中心店)**\n   - Address: 成府路28号五道口购物中心(五道口地铁站B南口步行190米)\n   - Distance: 9 meters\n\n2. **星巴克(北京五道口购物中心店)**\n   - Address: 成府路28号1号楼101-10B及2号楼201-09号\n   - Distance: 39 meters\n\n3. **luckin coffee 瑞幸咖啡(五道口购物中心店)**\n   - Address: 成府路28号五道口购物中心负一楼101号\n   - Distance: 67 meters\n\nEnjoy your stay and coffee in Beijing!",
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": null,
#     "refusal": null
# }


# ************************************************************************************************************************
#******************* prompt = "I want to have coffee near Wudaokou in Beijing, please recommend some places." ***********

# ===== GPT Response =====
# {
#     "content": null,
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": [
#         {
#             "id": "call_HbbNLlp9D7ukKFfkF9V1iims",
#             "function": {
#                 "arguments": "{\"location\":\"五道口\",\"city\":\"北京\"}",
#                 "name": "get_location_coordinate"
#             },
#             "type": "function"
#         }
#     ],
#     "refusal": null
# }
# Function arguments:
# {
#     "location": "五道口",
#     "city": "北京"
# }
# Call: get_location_coordinate
# https://restapi.amap.com/v5/place/text?key=22b34521f11ce01f5744ffa28893cmef&keywords=五道口&region=北京
# ===== Function Return =====
# {
#     "parent": "",
#     "address": "海淀区",
#     "distance": "",
#     "pcode": "110000",
#     "adcode": "110108",
#     "pname": "北京市",
#     "cityname": "北京市",
#     "type": "地名地址信息;热点地名;热点地名",
#     "typecode": "190700",
#     "adname": "海淀区",
#     "citycode": "010",
#     "name": "五道口",
#     "location": "116.338611,39.992552",
#     "id": "B000A8WSBH"
# }
# {
#     "content": null,
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": [
#         {
#             "id": "call_rCozYIIg2Ws1yVu5nK4WRZON",
#             "function": {
#                 "arguments": "{\"longitude\":\"116.338611\",\"latitude\":\"39.992552\",\"keyword\":\"咖啡\"}",
#                 "name": "search_nearby_pois"
#             },
#             "type": "function"
#         }
#     ],
#     "refusal": null
# }
# Function arguments:
# {
#     "longitude": "116.338611",
#     "latitude": "39.992552",
#     "keyword": "咖啡"
# }
# Call: search_nearby_pois
# https://restapi.amap.com/v5/place/around?key=22b34521f11ce01f5744ffa28893cmef&keywords=咖啡&location=116.338611,39.992552
# ===== Function Return =====
# PAGEONE CAFE(五道口购物中心店)
# 成府路28号五道口购物中心(五道口地铁站B南口步行190米)
# Distance: 9 meters
#
# 星巴克(北京五道口购物中心店)
# 成府路28号1层101-10B及2层201-09号
# Distance: 39 meters
#
# luckin coffee 瑞幸咖啡(五道口购物中心店)
# 成府路28号五道口购物中心负一层101号
# Distance: 67 meters
#
#
# {
#     "content": "Here are some coffee places near Wudaokou in Beijing:\n\n1. **PAGEONE CAFE (Wudaokou Shopping Center)**  \n   Address: 成府路28号五道口购物中心(五道口地铁站B南口步行190米)  \n   Distance: 9 meters\n\n2. **Starbucks (Beijing Wudaokou Shopping Center)**  \n   Address: 成府路28号1层101-10B及2层201-09号  \n   Distance: 39 meters\n\n3. **Luckin Coffee (Wudaokou Shopping Center)**  \n   Address: 成府路28号五道口购物中心负一层101号  \n   Distance: 67 meters\n\nEnjoy your coffee!",
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": null,
#     "refusal": null
# }
# ===== Final Response =====
# Here are some coffee places near Wudaokou in Beijing:
#
# 1. **PAGEONE CAFE (Wudaokou Shopping Center)**
#    Address: 成府路28号五道口购物中心(五道口地铁站B南口步行190米)
#    Distance: 9 meters
#
# 2. **Starbucks (Beijing Wudaokou Shopping Center)**
#    Address: 成府路28号1层101-10B及2层201-09号
#    Distance: 39 meters
#
# 3. **Luckin Coffee (Wudaokou Shopping Center)**
#    Address: 成府路28号五道口购物中心负一层101号
#    Distance: 67 meters
#
# Enjoy your coffee!
# ===== Conversation History =====
# {
#     "role": "system",
#     "content": "You are a map expert who can find any address."
# }
# {
#     "role": "user",
#     "content": "I want to have coffee near Wudaokou in Beijing, please recommend some places."
# }
# {
#     "content": null,
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": [
#         {
#             "id": "call_HbbNLlp9D7ukKFfkF9V1iims",
#             "function": {
#                 "arguments": "{\"location\":\"五道口\",\"city\":\"北京\"}",
#                 "name": "get_location_coordinate"
#             },
#             "type": "function"
#         }
#     ],
#     "refusal": null
# }
# {
#     "tool_call_id": "call_HbbNLlp9D7ukKFfkF9V1iims",
#     "role": "tool",
#     "name": "get_location_coordinate",
#     "content": "{'parent': '', 'address': '海淀区', 'distance': '', 'pcode': '110000', 'adcode': '110108', 'pname': '北京市', 'cityname': '北京市', 'type': '地名地址信息;热点地名;热点地名', 'typecode': '190700', 'adname': '海淀区', 'citycode': '010', 'name': '五道口', 'location': '116.338611,39.992552', 'id': 'B000A8WSBH'}"
# }
# {
#     "content": null,
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": [
#         {
#             "id": "call_rCozYIIg2Ws1yVu5nK4WRZON",
#             "function": {
#                 "arguments": "{\"longitude\":\"116.338611\",\"latitude\":\"39.992552\",\"keyword\":\"咖啡\"}",
#                 "name": "search_nearby_pois"
#             },
#             "type": "function"
#         }
#     ],
#     "refusal": null
# }
# {
#     "tool_call_id": "call_rCozYIIg2Ws1yVu5nK4WRZON",
#     "role": "tool",
#     "name": "search_nearby_pois",
#     "content": "PAGEONE CAFE(五道口购物中心店)\n成府路28号五道口购物中心(五道口地铁站B南口步行190米)\nDistance: 9 meters\n\n星巴克(北京五道口购物中心店)\n成府路28号1层101-10B及2层201-09号\nDistance: 39 meters\n\nluckin coffee 瑞幸咖啡(五道口购物中心店)\n成府路28号五道口购物中心负一层101号\nDistance: 67 meters\n\n"
# }
# {
#     "content": "Here are some coffee places near Wudaokou in Beijing:\n\n1. **PAGEONE CAFE (Wudaokou Shopping Center)**  \n   Address: 成府路28号五道口购物中心(五道口地铁站B南口步行190米)  \n   Distance: 9 meters\n\n2. **Starbucks (Beijing Wudaokou Shopping Center)**  \n   Address: 成府路28号1层101-10B及2层201-09号  \n   Distance: 39 meters\n\n3. **Luckin Coffee (Wudaokou Shopping Center)**  \n   Address: 成府路28号五道口购物中心负一层101号  \n   Distance: 67 meters\n\nEnjoy your coffee!",
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": null,
#     "refusal": null
# }
