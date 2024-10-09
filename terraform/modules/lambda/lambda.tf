# This prevents a circular dependency between aws_lambda_function.high_fives and aws_cloudwatch_log_group.high_five_logs
variable "lambda_function_name" {
  default = "email_ratings"
}

# Infra to support our lambda function:
# Policies for it to assume a role and to be able to trigger events based on success/failure,
# and also the source file and the lambda function itself

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_caller_identity" "lambda" {
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "${var.application_name}-${var.environment}-iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  inline_policy {
    name = "email-logs-lambda-policy-${var.environment}"
    policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SSMParameterAccessPolicy",
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:PutParameter"
      ],
      "Resource": [
        "arn:aws:ssm:*:${data.aws_caller_identity.lambda.account_id}:parameter/${var.application_name}/${var.environment}/*"
      ]
    },
    {
      "Sid": "SESSendPolicy",
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail"
      ],
      "Resource": "*"
    },
    {
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Effect": "Allow",
      "Resource": "*"
    },
    {
      "Sid": "SQSDeadLetterAccessPolicy",
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage"
      ],
      "Resource": [
        "${aws_sqs_queue.lambda_dead_letter_queue.arn}"
      ]
    }
  ]
}
POLICY
  }
}

resource "aws_lambda_permission" "allow_cloudwatch_events" {
  statement_id  = "AllowExecutionFromCloudWatchEvents"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rate_mds.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cron.arn
}

resource "aws_lambda_function" "rate_mds" {
  image_uri = "${aws_ecr_repository.rate_mds.repository_url}:latest"
  architectures = ["x86_64"]
  #architectures = ["arm64"]
  package_type = "Image"
  function_name = "${var.lambda_function_name}-${var.environment}"
  role = aws_iam_role.iam_for_lambda.arn
  publish = true
  timeout = 90 # Normally takes 3-4 seconds to start up. Currently takes about 30s to run
  memory_size = 256 # Normally takes about 80MB

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.high_five_logs,
  ]
}

# Infra to respond to our lamdba function:
# If the invocation fails then the input gets put on a dead-letter queue and an alarm is triggered

resource "aws_lambda_function_event_invoke_config" "rate_mds" {
  function_name = aws_lambda_function.rate_mds.function_name

  maximum_event_age_in_seconds = 60
  maximum_retry_attempts       = 2

  destination_config {
    on_failure {
      destination = aws_sqs_queue.lambda_dead_letter_queue.arn
    }
  }
}

resource "aws_sqs_queue" "lambda_dead_letter_queue" {
  name                      = "${var.application_name}-lambda-dead-letter-${var.environment}"
  delay_seconds             = 0
  max_message_size          = 262144  # 256kB
  message_retention_seconds = 1209600 # 14 days
  receive_wait_time_seconds = 0
}

# Lambda function automatically write to cloudwatch logs if we give them permission

resource "aws_cloudwatch_log_group" "high_five_logs" {
  name              = "/aws/lambda/${var.lambda_function_name}-${var.environment}"
  retention_in_days = 14
}

# See also the following AWS managed policy: AWSLambdaBasicExecutionRole
data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "${var.application_name}-${var.environment}-lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}