# Cloud Cost Analysis
**Project:** Plant Phenotyping CV Application (HADES / NPEC)\
**Course:** ADS-AI Year 2, Block D\
**Period:** 13 April – 12 June 2026\
**Team:** Group CV8

---

## Our Setup

This project runs on the university's Azure subscription with model training performed on university GPU infrastructure. This eliminates the two largest cost drivers for this type of project. The analysis below documents what resources are used and what they would cost if run independently.

---

## Azure Resources Used

| Resource | Purpose |
|---|---|
| Azure ML Workspace | Model registry, experiment tracking |
| Azure Blob Storage | Images, annotations, model weights |
| Azure Container Registry | Docker images (backend, frontend, DB) |
| Azure Container Apps | FastAPI inference API + Flask frontend |
| Azure Database for PostgreSQL | Submission metadata, predictions, metrics |
| Azure Monitor / App Insights | Latency, error rate, drift detection |
| Azure DevOps | Boards, CI/CD pipelines |
| GitHub Actions | Lint, test, build, deploy |
| Portainer (on-premise) | On-premise deployment |

---

## Actual Cost to the Team

Because the university covers the Azure subscription and provides GPU compute for training, **our out-of-pocket cost is €0**.

The resources we actively consume (Blob Storage, Container Apps, PostgreSQL, Container Registry) are low-cost services that fall well within the university allocation.

---

## Hypothetical Independent Cost

If this project were run on a personal Azure account without university support, the estimated cost over 8 weeks would be **€270–340**.

| Category | Resource | Estimated Cost |
|---|---|---|
| GPU training | Standard_NC6s_v3 (V100) — ~30 hrs total | ~€105 |
| Managed endpoint | Standard_DS2_v2 online endpoint | ~€100/mo if always-on |
| Hyperparameter tuning | 4× GPU sweep runs (~3 hrs each) | ~€42 |
| App hosting | Azure Container Apps (inference + frontend) | ~€20–40 |
| Database | PostgreSQL Flexible Server B1ms | ~€15/mo |
| Storage | Blob Storage ~100 GB | ~€5 |
| Container Registry | Basic tier | ~€5/mo |
| Monitoring | Azure Monitor (within free tier) | ~€0 |

Note: GPU compute alone accounts for roughly 65% of total costs in an independent setup. Training jobs and always-on endpoints are the two items that require the most active cost management.

---

## Cost Management Practices

Even under the university subscription, we follow these practices to avoid unnecessary spend:

- **Compute clusters scale to 0 when idle**: no always-on training instances.
- **Pipeline validation on small data subsets** before full runs (as outlined in Sprint 3 goals).
- **Endpoints shut down after Demo Day** to avoid post-deadline charges.
- **Weekly cost review**: one team member checks Azure Cost Management each sprint.
- **CPU for pipeline steps** (preprocessing, evaluation): GPU only for the training step itself.
---

## Notes

- All hypothetical prices are based on Azure West Europe region, April 2026.
- Actual costs vary with training duration, data volume, and endpoint uptime.
- Azure DevOps (≤5 users), GitHub Actions (2000 min/mo), and Azure Monitor (5 GB/mo) are free under their standard tiers.

## Related Documents
- [Project Plan and Roadmap](plan_roadmap.md)
