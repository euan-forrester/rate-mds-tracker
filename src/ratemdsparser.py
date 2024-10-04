from dateutil import parser
from datetime import date

def parse_date(s):
  if s is None:
    return None

  return parser.parse(s).date() # Example date is '2024-08-03T13:50:09.699866-04:00'

class RateMdsParser:
  
  @staticmethod
  def parse_rating(i):
    return {
      'id': i['id'],
      'created': parse_date(i['created']),
      'average': i['average'],
      'visible': i['visible'],
      'comment': i['comment']
    }

  @staticmethod
  def stringify_rating_components(rating):
    components = [
      f"Created: {RateMdsParser.stringify_date(rating['created'])}" if rating['created'] is not None else None,
    ]

    components.append(f"Comment: {rating['comment']}")

    return list(filter(None, components))

  @staticmethod
  def stringify_rating(rating):
    return "\n".join(RateMdsParser.stringify_rating_components(rating))

  @staticmethod
  def stringify_date(date):
    return date.strftime('%b %-d, %Y')
