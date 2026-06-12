---
date: 2026-06-11
tags: [dp700, module, fabric, ms-learn]
project: "DP-700 Atlas"
source: "https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/"
---

# Medallion Architecture

Up: [[DP-700 Atlas — MOC]]  ·  Learning path: *Implement a Lakehouse*

> MS Learn module: https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/

## Learning objectives
- Describe medallion architecture principles
- Implement Bronze/Silver/Gold in Fabric
- Query and report with Direct Lake
- Secure and govern a medallion lakehouse

## Key concepts
Bronze = raw as-ingested; Silver = validated/deduplicated/conformed; Gold = business-ready, often dimensional. Layers as separate lakehouses/workspaces. Direct Lake semantic models on Gold. Governance: access per layer, sensitivity labels.

## Units
- [ ] [Describe medallion architecture](https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/2-describe-medallion-architecture)
- [ ] [Implement a medallion architecture in Fabric](https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/3-implement-medallion-archecture-fabric)
- [ ] [Query and report on data in your lakehouse](https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/4-query-report-data)
- [ ] [Considerations for managing your lakehouse](https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/5-secure-govern)

## Neural links
Neurons: [[Lakehouse]] · [[Semantic Model]] · [[Data Security]]
Skill groups: [[Design Loading Patterns]] · [[Ingest and Transform Batch Data]]
