output "cloudwatch_event_rule_cron_name" {
  value       = aws_cloudwatch_event_rule.cron.name
  description = "Name of the EventBridge cron rule that runs our lambda expression"
}

output "lamdba_dead_letter_queue_name" {
  value       = aws_sqs_queue.lambda_dead_letter_queue.name
  description = "Name of the SQS dead-letter queue for our lamdba expression"
}

output "metrics_namespace" {
  value       = var.metrics_namespace
  description = "Namespace used for our custom cloudwatch metrics"
}
