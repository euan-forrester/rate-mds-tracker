resource "aws_cloudwatch_dashboard" "main" {
  count = var.enable_dashboards ? 1 : 0 # Don't create this if we turn off dashboards (e.g. for dev). We only get a few dashboards in total at the AWS Free Tier

  dashboard_name = "${var.application_name}-${var.environment}"

  # Formet described here: https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/CloudWatch-Dashboard-Body-Structure.html
  # Although the docs say that you can use D or W when specifying "start" below, I found that only H worked
  dashboard_body = <<EOF
  {
    "start": "-PT672H",
    "periodOverride": "inherit",
    "widgets": [
       {
          "x":0,
          "y":0,
          "width":12,
          "height":6,
          ${local.template_file_most_recent_rating_age_days}
       },
       {
          "x":12,
          "y":0,
          "width":12,
          "height":6,
          ${local.template_file_num_ratings_filtered_out}
       },
       {
          "x":0,
          "y":6,
          "width":12,
          "height":6,
          ${local.template_file_total_ratings}
       },
       {
          "x":12,
          "y":6,
          "width":12,
          "height":6,
          ${local.template_file_new_ratings}
       },
       {
          "x":0,
          "y":12,
          "width":12,
          "height":6,
          ${local.template_file_eventbridge_failed_invocations}
       },
       {
          "x":12,
          "y":12,
          "width":12,
          "height":6,
          ${local.template_file_dead_letter_queue_items}
       }
    ]
  }
  
EOF

}

locals {
  template_file_most_recent_rating_age_days = templatefile("${path.module}/most_recent_rating_age_days.tftpl", {
    metrics_namespace = var.metrics_namespace
    environment       = var.environment
    region            = var.region   
  })

  template_file_num_ratings_filtered_out = templatefile("${path.module}/num_ratings_filtered_out.tftpl", {
    metrics_namespace = var.metrics_namespace
    environment       = var.environment
    region            = var.region   
  })

  template_file_total_ratings = templatefile("${path.module}/total_ratings.tftpl", {
    metrics_namespace = var.metrics_namespace
    environment       = var.environment
    region            = var.region
  })

  template_file_new_ratings = templatefile("${path.module}/new_ratings.tftpl", {
    metrics_namespace = var.metrics_namespace
    environment       = var.environment
    region            = var.region
  })

  template_file_eventbridge_failed_invocations = templatefile("${path.module}/eventbridge_failed_invocations.tftpl", {
    rule_name         = var.cloudwatch_event_rule_cron_name
    region            = var.region
  })

  template_file_dead_letter_queue_items = templatefile("${path.module}/dead_letter_queue_items.tftpl", {
    queue_name        = var.lamdba_dead_letter_queue_name
    region            = var.region
  })
}
