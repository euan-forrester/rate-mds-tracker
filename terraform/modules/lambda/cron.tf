resource "aws_cloudwatch_event_rule" "cron" {
  name        = "${var.application_name}-cron-rule-${var.environment}"
  state       = "ENABLED"
  description = "Fire our lambda expression"
  schedule_expression = var.cron_expression # Note that these need to be Quartz cron expressions, not unix cron
}

resource "aws_cloudwatch_event_target" "cron" {
  rule      = aws_cloudwatch_event_rule.cron.name
  target_id = "TriggerLambda"
  arn       = aws_lambda_function.rate_mds.arn
}
