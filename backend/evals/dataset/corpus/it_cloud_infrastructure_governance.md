# Cloud Infrastructure Governance and Cost Management (ENG-POL-602)

## 1. Multi-Cloud Architecture
Our primary infrastructure runs on Google Cloud Platform (GCP) for containerized microservices and AI workloads, with Amazon Web Services (AWS) providing disaster recovery cold storage.

## 2. Mandatory Resource Tagging
All provisioned cloud resources (VMs, Cloud Run services, buckets, databases) must include the following metadata labels:
- `environment`: `production`, `staging`, or `development`
- `owner`: team email alias (e.g., `team-rag@enterprise.com`)
- `cost-center`: financial department allocation code
- `service`: microservice name
Unlabeled resources in non-production environments are automatically deleted after 48 hours.

## 3. Idle Resource Auto-Shutdown
Non-production development clusters and sandbox environments are automatically stopped between 8:00 PM and 7:00 AM local time on weekdays and all weekend to minimize unnecessary cloud computing expenditure.