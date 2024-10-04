resource "aws_ses_email_identity" "from_email" {
  email = var.from_email
}

resource "aws_ses_email_identity" "to_email" {
  email = var.to_email
}

resource "aws_ses_email_identity" "cc_email" {
  email = var.cc_email
}
