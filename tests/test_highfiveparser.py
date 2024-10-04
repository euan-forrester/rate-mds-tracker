import sys
sys.path.append("../src")

from ratemdsparser import RateMdsParser

def test_parse():
  rating_string = '{"id":5374652,"created":"2024-08-03T13:50:09.699866-04:00","modified":"2024-08-03T13:50:09.699838-04:00","appointment_type_display":"In-person","doctor":2137096,"doctor_images":{"70x70":"//www.ratemds.com/static/img/doctors/doctor-female.png_thumbs/v1_at_70x70.29e415b8224a.jpg","77x77":"//www.ratemds.com/static/img/doctors/doctor-female.png_thumbs/v1_at_77x77.e638bec03d07.jpg","165x165":"//www.ratemds.com/static/img/doctors/doctor-female.png_thumbs/v1_at_165x165.0ec3aaa35c7b.jpg","32x32":"//www.ratemds.com/static/img/doctors/doctor-female.png_thumbs/v1_at_32x32.c66ce95f983a.jpg","100x100":"//www.ratemds.com/static/img/doctors/doctor-female.png_thumbs/v1_at_100x100.dd263c972e14.jpg","autoxauto":"//www.ratemds.com/static/img/doctors/doctor-female.png_thumbs/v1_at_autoxauto.0ec3aaa35c7b.jpg"},"doctor_full_name":"Dr. Kathryn Louise Toews","doctor_url":"/doctor-ratings/dr-kathryn-louise-toews-new-westminster-bc-ca/","staff":5.0,"punctuality":5.0,"helpfulness":5.0,"knowledge":5.0,"average":5.0,"comment":"She was the most incredible and amazing doctor I have dealt with! I was so happy I got her for the reason of coming into the hospital. I couldn’t thank her enough for being so kind, patient and knowledgable - we are very lucky to have her!","visible":true,"featured":false,"comments":[],"location":null,"DEPRECATED_hide_ratings":false,"feature_ratings":false,"votes":{"count":0},"has_flag":false,"has_pending":false,"appeal_key":"f5cac6782d2f90ada2c2c66bed22f357b0e029773ac50521e973452efb1cf5a2","appeal_date":false,"appointment_type":0}'

  rating_obj = json.loads(rating_string)

  rating = RateMdsParser.parse_rating(rating_obj)

  assert rating['id'] == 5374652
  assert RateMdsParser.stringify_date(rating['created']) == "Aug 3, 2024"
  assert rating['average'] == 5.0
  assert rating['visible'] == True
  assert rating['comment'] == 'She was the most incredible and amazing doctor I have dealt with! I was so happy I got her for the reason of coming into the hospital. I couldn’t thank her enough for being so kind, patient and knowledgable - we are very lucky to have her!'
