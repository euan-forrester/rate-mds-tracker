resource "aws_cloudwatch_metric_alarm" "most-recent-high-five-age-days" {
  count = var.enable_alarms ? 1 : 0 # Don't create this if we turn off alarms (e.g. for dev)

  alarm_name                = "${var.application_name} Most recent High Five age days - ${var.environment}"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = "most-recent-high-five-age-days"
  namespace                 = var.metrics_namespace
  period                    = "300"
  statistic                 = "Maximum"
  threshold                 = "30" # High Fives are uploaded to the system by hand, so even when they're fresh they're dated a week or two prior to the current date
  treat_missing_data        = "notBreaching"
  alarm_description         = "Alerts if the High Five system is not generating new High Fives"
  alarm_actions             = [aws_sns_topic.alarms.arn]
  insufficient_data_actions = [aws_sns_topic.alarms.arn]
  ok_actions                = [aws_sns_topic.alarms.arn]

  dimensions = {
    Environment = var.environment
  }
}
