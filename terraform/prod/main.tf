module "lambda" {
  source = "../modules/lambda"

  environment             = var.environment
  region                  = var.region
  application_name        = var.application_name

  num_days_to_keep_images = 30

  cron_expression         = "cron(0 16 * * ? *)"  # Run every day at 4:00 PM UTC = 9:00 AM PDT or 8:00 AM PST

  set_most_recent_rating_id = true

  metrics_namespace       = var.application_name
  send_metrics            = true

  send_email              = true
  subject_line_singular   = var.subject_line_singular
  subject_line_plural     = var.subject_line_plural
  to_email                = var.to_email
  cc_email                = var.cc_email
  from_email              = var.from_email
  minimum_average_score   = var.minimum_average_score

  base_url                = "https://www.ratemds.com/doctor-ratings/dr-kathryn-louise-toews-new-westminster-bc-ca/?json=true"

  batch_size              = 1000
  num_retries             = 5
  retry_backoff_factor    = 1 # Backoff time is backoff_factor * 2^retries
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
