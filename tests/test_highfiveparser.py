import sys
sys.path.append("../src")

from highfiveparser import HighFiveParser

# If a High Five contains no communities, then the resultant object should have an empty list
def test_no_communities():
  high_five_obj = {
    "Id": "556f6b73-fb80-4562-854c-90c1bd4eaac0",
    "Language": "en",
    "Path": "/sitecore/content/FraserHealth/FraserHealth/Home/highfive/2023/high-five-8",
    "Url": "https://www.fraserhealth.ca/highfive/2023/high-five-8",
    "Name": None,
    "Html": "<div class=\"highfive-card\"><div class=\"card-message-wrapper\"><div class=\"field-message\">The nurses, physician and other staff made my young daughter and I feel taken care of. While chatting with us, the friendly greeter gave my child a goodie bag with toys and activities. The sweet discharge nurse gave her a Popsicle, and the attending doctor was caring and kind. Absolutely over and above any hospital visit I've ever had. Thank you to the staff for being kind and making an ill little girl feel better.</div><div class=\"field-highfivedate\">Sep 15, 2023</div><div class=\"field-firstname\">Samantha Johnstone </div></div></div>"
  }

  high_five = HighFiveParser.parse_high_five(high_five_obj)

  assert high_five['id'] == "556f6b73-fb80-4562-854c-90c1bd4eaac0"
  assert HighFiveParser.stringify_date(high_five['date']) == "Sep 15, 2023"
  assert high_five['name'] == "Samantha Johnstone"
  assert len(high_five['communities']) == 0
  assert high_five['message'] == "The nurses, physician and other staff made my young daughter and I feel taken care of. While chatting with us, the friendly greeter gave my child a goodie bag with toys and activities. The sweet discharge nurse gave her a Popsicle, and the attending doctor was caring and kind. Absolutely over and above any hospital visit I've ever had. Thank you to the staff for being kind and making an ill little girl feel better."

  high_five_strings = HighFiveParser.stringify_high_five_components(high_five)

  assert len(high_five_strings) == 3
  assert high_five_strings[0] == "Date: Sep 15, 2023"
  assert high_five_strings[1] == "From: Samantha Johnstone"
  assert high_five_strings[2] == "Message: The nurses, physician and other staff made my young daughter and I feel taken care of. While chatting with us, the friendly greeter gave my child a goodie bag with toys and activities. The sweet discharge nurse gave her a Popsicle, and the attending doctor was caring and kind. Absolutely over and above any hospital visit I've ever had. Thank you to the staff for being kind and making an ill little girl feel better."

# If a High Five contains one or more communities, then the resultant object should have a list containing those communities
def test_single_community():
  high_five_obj = {
    "Id": "556f6b73-fb80-4562-854c-90c1bd4eaac0",
    "Language": "en",
    "Path": "/sitecore/content/FraserHealth/FraserHealth/Home/highfive/2023/high-five-8",
    "Url": "https://www.fraserhealth.ca/highfive/2023/high-five-8",
    "Name": None,
    "Html": "<div class=\"highfive-card\"><div class=\"card-message-wrapper\"><div class=\"highfive-community\"><span class=\"community-label\">For</span><span class=\"field-communityname\">Maple Ridge</span></div><div class=\"field-message\">The nurses, physician and other staff made my young daughter and I feel taken care of. While chatting with us, the friendly greeter gave my child a goodie bag with toys and activities. The sweet discharge nurse gave her a Popsicle, and the attending doctor was caring and kind. Absolutely over and above any hospital visit I've ever had. Thank you to the staff for being kind and making an ill little girl feel better.</div><div class=\"field-highfivedate\">Sep 15, 2023</div><div class=\"field-firstname\">Samantha Johnstone </div></div></div>"
  }

  high_five = HighFiveParser.parse_high_five(high_five_obj)

  assert high_five['id'] == "556f6b73-fb80-4562-854c-90c1bd4eaac0"
  assert HighFiveParser.stringify_date(high_five['date']) == "Sep 15, 2023"
  assert high_five['name'] == "Samantha Johnstone"
  assert len(high_five['communities']) == 1
  assert high_five['communities'][0] == "Maple Ridge"
  assert high_five['message'] == "The nurses, physician and other staff made my young daughter and I feel taken care of. While chatting with us, the friendly greeter gave my child a goodie bag with toys and activities. The sweet discharge nurse gave her a Popsicle, and the attending doctor was caring and kind. Absolutely over and above any hospital visit I've ever had. Thank you to the staff for being kind and making an ill little girl feel better."

  high_five_strings = HighFiveParser.stringify_high_five_components(high_five)

  assert len(high_five_strings) == 4
  assert high_five_strings[0] == "Date: Sep 15, 2023"
  assert high_five_strings[1] == "From: Samantha Johnstone"
  assert high_five_strings[2] == "Community: Maple Ridge"
  assert high_five_strings[3] == "Message: The nurses, physician and other staff made my young daughter and I feel taken care of. While chatting with us, the friendly greeter gave my child a goodie bag with toys and activities. The sweet discharge nurse gave her a Popsicle, and the attending doctor was caring and kind. Absolutely over and above any hospital visit I've ever had. Thank you to the staff for being kind and making an ill little girl feel better."

# If a High Five contains one or more communities, then the resultant object should have a list containing those communities
def test_two_communities():
  high_five_obj = {
    "Id": "a00d07de-93b9-435a-a3f7-9139565aae0e",
    "Language": "en",
    "Path": "/sitecore/content/FraserHealth/FraserHealth/Home/highfive/2023/high-five-7",
    "Url": "https://www.fraserhealth.ca/highfive/2023/high-five-7",
    "Name": None,
    "Html": "<div class=\"highfive-card\"><div class=\"card-message-wrapper\"><div class=\"highfive-community\"><span class=\"community-label\">For</span><span class=\"field-communityname\">Maple Ridge</span><span class=\"field-communityname\">Fraser Health region</span></div><div class=\"field-message\">I received the highest quality of care during my stay in Ridge Meadows [Hospital]. Every nurse was cheerful, caring and invested in providing the best possible care. They regularly checked in on me and answered any questions I had. I feel fortunate to have been in the care of exceptionally dedicated, compassionate and kind nursing staff. Please convey my appreciation and thanks.</div><div class=\"field-highfivedate\">Aug 21, 2023</div><div class=\"field-firstname\">Carol</div></div></div>"
  }

  high_five = HighFiveParser.parse_high_five(high_five_obj)

  assert high_five['id'] == "a00d07de-93b9-435a-a3f7-9139565aae0e"
  assert HighFiveParser.stringify_date(high_five['date']) == "Aug 21, 2023"
  assert high_five['name'] == "Carol"
  assert len(high_five['communities']) == 2
  assert high_five['communities'][0] == "Maple Ridge"
  assert high_five['communities'][1] == "Fraser Health region"
  assert high_five['message'] == "I received the highest quality of care during my stay in Ridge Meadows [Hospital]. Every nurse was cheerful, caring and invested in providing the best possible care. They regularly checked in on me and answered any questions I had. I feel fortunate to have been in the care of exceptionally dedicated, compassionate and kind nursing staff. Please convey my appreciation and thanks."

  high_five_strings = HighFiveParser.stringify_high_five_components(high_five)

  assert len(high_five_strings) == 4
  assert high_five_strings[0] == "Date: Aug 21, 2023"
  assert high_five_strings[1] == "From: Carol"
  assert high_five_strings[2] == "Communities: Maple Ridge and Fraser Health region"
  assert high_five_strings[3] == "Message: I received the highest quality of care during my stay in Ridge Meadows [Hospital]. Every nurse was cheerful, caring and invested in providing the best possible care. They regularly checked in on me and answered any questions I had. I feel fortunate to have been in the care of exceptionally dedicated, compassionate and kind nursing staff. Please convey my appreciation and thanks."
