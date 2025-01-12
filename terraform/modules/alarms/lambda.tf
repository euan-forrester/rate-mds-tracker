resource "aws_cloudwatch_metric_alarm" "eventbridge_failedinvocations" {
  count = var.enable_alarms ? 1 : 0 # Don't create this if we turn off alarms (e.g. for dev)

  alarm_name                = "${var.application_name} EventBridge FailedInvocations - ${var.environment}"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = "FailedInvocations"
  namespace                 = "AWS/Events"
  period                    = "300"
  statistic                 = "Sum"
  threshold                 = "1"
  treat_missing_data        = "ignore"
  alarm_description         = "Alerts if EventBridge fails to publish a cron event to lambda"
  alarm_actions             = [aws_sns_topic.alarms.arn]
  insufficient_data_actions = [aws_sns_topic.alarms.arn]
  ok_actions                = [aws_sns_topic.alarms.arn]

  dimensions = {
    RuleName = var.cloudwatch_event_rule_cron_name
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_dead_letter_queue_items" {
  count = var.enable_alarms ? 1 : 0 # Don't create this if we turn off alarms (e.g. for dev)

  alarm_name                = "${var.lamdba_dead_letter_queue_name} items"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = "ApproximateNumberOfMessagesVisible"
  namespace                 = "AWS/SQS"
  period                    = "300"
  statistic                 = "Maximum"
  threshold                 = "1"
  treat_missing_data        = "ignore" # Maintain alarm state on missing data - sometimes data will just be missing for queues for some reason
  alarm_description         = "Alerts if the lambda dead-letter queue has items in it"
  alarm_actions             = [aws_sns_topic.alarms.arn]
  insufficient_data_actions = [aws_sns_topic.alarms.arn]
  ok_actions                = [aws_sns_topic.alarms.arn]

  dimensions = {
    QueueName = var.lamdba_dead_letter_queue_name
  }
}
