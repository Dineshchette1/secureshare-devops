# AI Review Log

I use AI tools to speed up infrastructure work, and I review, test and
validate everything they produce. This log records what I checked and fixed.

| Date | Phase | What the AI helped with | What was wrong or missed | How I verified / fixed it |
|------|-------|-------------------------|--------------------------|---------------------------|
| 2026-11-14 | 0 | Cost plan for the project | Suggested VPC interface endpoints to avoid a NAT Gateway; 7 endpoints x 2 AZs cost more than one NAT | Priced both; chose public subnets locked by security groups for dev |
| 2026-11-15 | 0 | Terraform bootstrap config | Assumed ca-central-1; the account's SCP only allows us-east-2 | Traced AccessDenied errors to the SCP, tested regions, switched to us-east-2 |
