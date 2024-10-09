resource "aws_ssm_parameter" "base_url" {
  name        = "/${var.application_name}/${var.environment}/base-url"
  description = "Base URL from which to get ratings"
  type        = "String"
  value       = var.base_url
}

resource "aws_ssm_parameter" "batch_size" {
  name        = "/${var.application_name}/${var.environment}/batch-size"
  description = "How many ratings to get in a single call"
  type        = "String"
  value       = var.batch_size
}

resource "aws_ssm_parameter" "request_retries" {
  name        = "/${var.application_name}/${var.environment}/num-retries"
  description = "How many times to retry our request"
  type        = "String"
  value       = var.num_retries
}

resource "aws_ssm_parameter" "request_backoff_factor" {
  name        = "/${var.application_name}/${var.environment}/retry-backoff-factor"
  description = "Number of seconds to add to backoff amount for each failed request"
  type        = "String"
  value       = var.retry_backoff_factor
}

resource "aws_ssm_parameter" "aws_region" {
  name        = "/${var.application_name}/${var.environment}/aws-region"
  description = "AWS region to send our emails from"
  type        = "String"
  value       = var.region
}

resource "aws_ssm_parameter" "run_at_script_startup" {
  name        = "/${var.application_name}/${var.environment}/run-at-script-startup"
  description = "Whether to run our check when the script first starts (or wait for Lambda to call the entrypoint)"
  type        = "String"
  value       = "False" # This option is for running the script locally for testing. When deployed to lambda we never want to do this.
}

resource "aws_ssm_parameter" "send_metrics" {
  name        = "/${var.application_name}/${var.environment}/send-metrics"
  description = "Whether to send cloudwatch metrics"
  type        = "String"
  value       = var.send_metrics
}

resource "aws_ssm_parameter" "metrics_namespace" {
  name        = "/${var.application_name}/${var.environment}/metrics-namespace"
  description = "Namespace for cloudwatch metrics"
  type        = "String"
  value       = var.metrics_namespace
}

resource "aws_ssm_parameter" "send_email" {
  name        = "/${var.application_name}/${var.environment}/send-email"
  description = "Whether to send an email with all of the new ratings we found"
  type        = "String"
  value       = var.send_email
}

resource "aws_ssm_parameter" "minimum_average_score" {
  name        = "/${var.application_name}/${var.environment}/minimum-average-score"
  description = "Minimum average score of a rating to warrant inclusion in an email"
  type        = "String"
  value       = var.minimum_average_score
}

resource "aws_ssm_parameter" "subject_line_singular" {
  name        = "/${var.application_name}/${var.environment}/subject-line-singular"
  description = "Subject line to use when sending one new rating"
  type        = "String"
  value       = var.subject_line_singular
}

resource "aws_ssm_parameter" "subject_line_plural" {
  name        = "/${var.application_name}/${var.environment}/subject-line-plural"
  description = "Subject line to use when sending more than one new rating"
  type        = "String"
  value       = var.subject_line_plural
}

# Arguably we should make this encrypted, but it costs money to maintain the KMS key
resource "aws_ssm_parameter" "to_email" {
  name        = "/${var.application_name}/${var.environment}/to-email"
  description = "Email address to send our new ratings"
  type        = "String"
  value       = var.to_email
}

# Arguably we should make this encrypted, but it costs money to maintain the KMS key
resource "aws_ssm_parameter" "cc_email" {
  name        = "/${var.application_name}/${var.environment}/cc-email"
  description = "Email address to cc when we send our new ratings"
  type        = "String"
  value       = var.cc_email
}

# Arguably we should make this encrypted, but it costs money to maintain the KMS key
resource "aws_ssm_parameter" "from_email" {
  name        = "/${var.application_name}/${var.environment}/from-email"
  description = "Email address from which our emails come"
  type        = "String"
  value       = var.from_email
}

resource "aws_ssm_parameter" "set_most_recent_high_five_id" {
  name        = "/${var.application_name}/${var.environment}/set-most-recent-rating-id"
  description = "Whether to set the most recent rating ID encountered during this invocation of the lambda function"
  type        = "String"
  value       = var.set_most_recent_rating_id
}

# We're going to use this as external storage, to persist the most recent ID encountered between invocations of our lamdba function
# So, ignore changes to the value of this parameter
resource "aws_ssm_parameter" "previous_most_recent_rating_id" {
  name        = "/${var.application_name}/${var.environment}/previous-most-recent-rating-id"
  description = "The ID of the most recent rating ID encountered on the previous run of the lambda expression"
  type        = "String"
  value       = "dummy"

  lifecycle {
    ignore_changes = [
      value,
    ]
  }
}
