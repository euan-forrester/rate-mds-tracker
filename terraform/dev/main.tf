module "lambda" {
  source = "../modules/lambda"

  environment             = var.environment
  region                  = var.region
  application_name        = var.application_name

  num_days_to_keep_images = 7

  cron_expression         = "cron(0 16 * * ? *)"  # Run every day at 4:00 PM UTC = 9:00 AM PDT or 8:00 AM PST
  #cron_expression         = "cron(*/5 * * * ? *)"  # Run every 5 minutes for testing
  
  set_most_recent_high_five_id = true

  metrics_namespace       = var.application_name
  send_metrics            = true

  send_email              = true
  subject_line_singular   = var.subject_line_singular
  subject_line_plural     = var.subject_line_plural
  to_email                = var.to_email
  cc_email                = var.cc_email
  from_email              = var.from_email
  names_of_interest       = var.names_of_interest
  communities_of_interest = var.communities_of_interest

  base_url                = "https://www.fraserhealth.ca//sxa/search/results/?l=en&s={8A83A1F3-652A-4C01-B247-A2849DDE6C73}&sig=&defaultSortOrder=HighFiveDate,Descending&.ZFZ0zOzMLUY=null&v={C0113845-0CB6-40ED-83E4-FF43CF735D67}&o=HighFiveDate,Descending&site=null"

  batch_size              = 1000
  num_retries             = 3
  retry_backoff_factor    = 0.5
}

module "alarms" {
  source = "../modules/alarms"

  environment       = var.environment
  region            = var.region

  application_name  = var.application_name
  system_email      = var.system_email

  metrics_namespace = module.lambda.metrics_namespace

  cloudwatch_event_rule_cron_name = module.lambda.cloudwatch_event_rule_cron_name
  lamdba_dead_letter_queue_name   = module.lambda.lamdba_dead_letter_queue_name

  enable_alarms     = true
}

module "dashboard" {
  source = "../modules/dashboard"

  environment       = var.environment
  region            = var.region

  application_name  = var.application_name
  metrics_namespace = module.lambda.metrics_namespace

  cloudwatch_event_rule_cron_name = module.lambda.cloudwatch_event_rule_cron_name
  lamdba_dead_letter_queue_name   = module.lambda.lamdba_dead_letter_queue_name

  enable_dashboards = true
}
