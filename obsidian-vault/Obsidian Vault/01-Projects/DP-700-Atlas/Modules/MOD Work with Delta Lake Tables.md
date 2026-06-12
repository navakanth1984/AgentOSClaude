---
date: 2026-06-11
tags: [dp700, module, fabric, ms-learn]
project: "DP-700 Atlas"
source: "https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/"
---

# Work with Delta Lake Tables

Up: [[DP-700 Atlas — MOC]]  ·  Learning path: *Implement a Lakehouse*

> MS Learn module: https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/

## Learning objectives
- Understand Delta Lake and delta tables
- Create and manage delta tables with Spark
- Optimize delta tables
- Query/transform delta data
- Use delta tables with structured streaming

## Key concepts
Delta = Parquet + transaction log (_delta_log): ACID, time travel (DESCRIBE HISTORY, VERSION AS OF), schema enforcement. Managed vs external tables. OPTIMIZE + V-Order, VACUUM for old files, partitioning. Sink/source for Spark structured streaming.

## Units
- [ ] [Understand Delta Lake](https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/2-understand-delta-lake)
- [ ] [Create delta tables](https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/3-create-delta-tables)
- [ ] [Optimize delta tables](https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/3b-optimize-delta-tables)
- [ ] [Work with delta tables in Spark](https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/4-work-delta-data)
- [ ] [Use delta tables with streaming data](https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/5-use-delta-lake-streaming-data)

## Neural links
Neurons: [[Lakehouse]] · [[Spark]] · [[OneLake]]
Skill groups: [[Optimize Performance]] · [[Ingest and Transform Streaming Data]]

## Deep notes
- [[UNIT Delta — Understand Delta Lake]]
- [[UNIT Delta — Create Delta Tables]]
- [[UNIT Delta — Optimize Delta Tables]]
- [[UNIT Delta — Streaming with Delta]]
