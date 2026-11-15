variable "region" {
  description = "AWS region for the project."
  type        = string
  default     = "us-east-2"
}

variable "alert_email" {
  description = "Email address that receives budget alerts."
  type        = string
}

variable "budget_limit_usd" {
  description = "Monthly budget limit in USD."
  type        = number
  default     = 50
}

variable "alert_thresholds_usd" {
  description = "Send an email when actual monthly cost passes each of these amounts (USD)."
  type        = list(number)
  default     = [10, 25, 50]
}
