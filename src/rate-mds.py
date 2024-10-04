#!/usr/bin/env python3

import sys
sys.path.insert(0, './common')

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import logging
import sys
import json
from datetime import date
from itertools import takewhile

from ratemdsparser import RateMdsParser
from confighelper import ConfigHelper
from metricshelper import MetricsHelper
from emailhelper import EmailHelper

#
# Setup logging
#

if logging.getLogger().hasHandlers():
  # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
  # `.basicConfig` does not execute. Thus we set the level directly.
  logging.getLogger().setLevel(logging.INFO)
else:
  logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()

#
# Get our config
#

config_helper = ConfigHelper.get_config_helper(default_env_name="dev", application_name="rate-mds-tracker")

AWS_REGION              = config_helper.get("aws-region")

BASE_URL                = config_helper.get("base-url")
NUM_RETRIES             = config_helper.getInt("num-retries")
RETRY_BACKOFF_FACTOR    = config_helper.getFloat("retry-backoff-factor")

MINIMUM_AVERAGE_SCORE    = config_helper.getFloat("minimum-average-score")

RUN_AT_SCRIPT_STARTUP   = config_helper.getBool("run-at-script-startup")

METRICS_NAMESPACE       = config_helper.get("metrics-namespace")
SEND_METRICS            = config_helper.getBool("send-metrics")

SET_MOST_RECENT_RATING_ID = config_helper.getBool("set-most-recent-rating-id")

SEND_EMAIL              = config_helper.getBool("send-email")
SUBJECT_LINE_SINGULAR   = config_helper.get("subject-line-singular")
SUBJECT_LINE_PLURAL     = config_helper.get("subject-line-plural")
TO_EMAIL_ADDRESS        = config_helper.get("to-email")
CC_EMAIL_ADDRESS        = config_helper.get("cc-email")
FROM_EMAIL_ADDRESS      = config_helper.get("from-email")

#
# Init AWS stuff
#

email_helper   = EmailHelper(region=AWS_REGION)
metrics_helper = MetricsHelper(environment=config_helper.get_environment(), region=AWS_REGION, metrics_namespace=METRICS_NAMESPACE)

#
# Helper functions
#

def get_all_ratings():
  retries = Retry(total=NUM_RETRIES, backoff_factor=RETRY_BACKOFF_FACTOR)
  adapter = HTTPAdapter(max_retries=retries)

  session = requests.Session()
  session.mount("https://", adapter)

  current_page = 1 # Requesting page 0 gives the last page, as does requesting every page > the last page
  total_ratings = 0

  all_ratings = []

  while True:
    url = BASE_URL + f"&page={current_page}"

    response = session.get(url)

    if response.status_code != 200:
      logger.error(f"Received status code {response.status_code} after {REQUEST_RETRIES} attempts from URL '{url}'")
      sys.exit(-1)

    response_data = json.loads(response.text)

    total_pages = response_data['total_pages']

    ratings_batch = list(map(RateMdsParser.parse_rating, response_data['results']))
    ratings_batch = list(filter(lambda high_five:high_five['comment'] is not None, ratings_batch))

    all_ratings += ratings_batch

    if current_page >= total_pages:
      break

    current_page += 1

  return all_ratings

def email_ratings(ratings):
  body_text = "\n\n".join(map(RateMdsParser.stringify_rating, ratings))

  subject_line = SUBJECT_LINE_SINGULAR

  if len(high_fives) > 1:
    subject_line = SUBJECT_LINE_PLURAL.format(len(ratings))

  email_helper.send_email(FROM_EMAIL_ADDRESS, TO_EMAIL_ADDRESS, CC_EMAIL_ADDRESS, subject_line, body_text)

def calculate_metrics(all_ratings, new_ratings):
  logger.info("*** Metrics information ***")
  num_ratings_found = len(all_ratings)
  num_new_ratings_found = len(new_ratings)

  logger.info(f"Found {num_ratings_found} total ratings")
  logger.info(f"Found {num_new_ratings_found} new ratings")

  if num_ratings_found == 0:
    logger.info("No ratings found, so no further telemetry can be sent")
    return

  most_recent_rating = all_ratings[0]

  if most_recent_rating['created'] is None:
    logger.info(f"No created date found in rating {most_recent_rating['id']} so can't send telemetry about its age")
  else:
    most_recent_rating_age_days = (date.today() - most_recent_rating['created']).days
    logger.info(f"Most recent rating found is {most_recent_rating_age_days} days old")

  if SEND_METRICS:
    metrics_helper.send_count("total-ratings", num_ratings_found)
    metrics_helper.send_count("most-recent-rating-age-days", most_recent_rating_age_days)
    metrics_helper.send_count("new-ratings", num_new_ratings_found)

def log_rating(rating):
  rating_components = RateMdsParser.stringify_rating_components(rating)

  for component in rating_components:
    logger.info(component)

def get_new_ratings_and_send_email(event, context):

  # Need to do this at the start of every request, since Lambda doesn't necessarily re-run the entire script for each invocation
  PREVIOUS_MOST_RECENT_RATING_ID = config_helper.get("previous-most-recent-rating-id")

  # Request all of the ratings

  all_ratings = get_all_ratings()

  new_ratings = list(takewhile(lambda rating:rating['id'] != PREVIOUS_MOST_RECENT_RATING_ID, all_ratings))

  logger.info(f"Found {len(new_ratings)} new ratings")

  interesting_ratings = list(filter(lambda rating:rating['average'] >= MINIMUM_AVERAGE_SCORE, new_ratings))

  logger.info(f"Found {len(interesting_ratings)} interesting ratings")
  for rating in interesting_ratings:
    logger.info("\n\n")
    log_rating(rating)

  if SEND_EMAIL:
    if len(interesting_ratings) > 0:
      email_ratings(interesting_ratings)
    else:
      logger.info("No interesting ratings found, so not sending email")

  calculate_metrics(all_ratings, new_ratings)

  # Be sure to do this last, so that if we have an error earlier (e.g. sending the email) then we won't miss sending out a rating in a subsequent run
  if SET_MOST_RECENT_RATING_ID and (len(all_ratings) > 0):
    config_helper.set("previous-most-recent-rating-id", str(all_ratings[0]['id']))

if RUN_AT_SCRIPT_STARTUP:
  get_new_ratings_and_send_email(None, None)