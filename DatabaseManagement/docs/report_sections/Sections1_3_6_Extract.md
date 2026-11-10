# Report-Ready Extract: Sections 1, 3 and 6

## 1. Business Context and Design Goals

### 1.1 Scenario

The system supports membership and group-class management for a gym. Members purchase membership plans, check in at the gym, and enrol in classes taught by trainers. A member may enrol in many classes and a class may contain many members; the associative entity `Enrollment` resolves this many-to-many relationship. Cancellation is represented by `Enrollment.is_canceled`, so a cancelled enrolment remains available for audit while being excluded from active-enrolment counts.

The workload has two main paths. Operational writes create check-ins and enrolments and must preserve referential integrity and uniqueness. Operational reads and management reports identify highly enrolled members, trainer workloads, and check-in activity by membership type. `CheckIn` and `Enrollment` are the high-volume tables in the test workload, while the other tables provide the member, plan, trainer, and class context.

### 1.2 Stakeholders

| Stakeholder | Requirement | Database response |
|---|---|---|
| Member | Enrol in classes without duplicate active records and retain a cancellation history | `Enrollment(mid, class_id)` composite primary key and `is_canceled` flag |
| Front desk | Record valid check-ins and enrolments without references to non-existent members or classes | Foreign keys on all child records |
| Trainer | Obtain an accurate teaching workload, including trainers with no assigned classes | `Trainer LEFT JOIN Class` and `COUNT(Class.class_id)` |
| Operations manager | Monitor active enrolments, class demand, and check-in activity | Aggregation queries that exclude cancelled enrolments |
| DBA | Preserve integrity, support efficient lookups, and retain recoverable audit records | InnoDB constraints, targeted indexes, and logical cancellation |

### 1.3 Measurable goals and constraints

- **G1 — enrolment integrity:** zero duplicate `(mid, class_id)` enrolment records and zero enrolments referencing a non-existent member or class.
- **G2 — check-in integrity:** zero check-ins referencing a non-existent member.
- **G3 — active-enrolment accuracy:** cancelled enrolments must be excluded from Q1; only members with more than three active classes are returned.
- **G4 — trainer-report completeness:** Q2 must return all 30 trainers, including the seven trainers with zero classes, whose class count must be 0 rather than NULL.
- **G5 — check-in lookup latency:** the indexed lookup for `mid = 22` should average below 1 ms on the fixed test environment. Section 5 reports 0.245 ms with the index, compared with 7.10 ms without it.
- **G6 — membership reporting accuracy:** Q3 must aggregate all check-ins by membership type rather than return one row per member.

## 3. Design Rationale: Consistency, Availability and Latency

### 3.1 Single-node architecture

The system uses a single-node MySQL deployment with InnoDB tables. There is no replication or distributed failover, so a CP-versus-AP choice between replicas is not part of the present design. The relevant trade-off is between strong operational integrity, query latency, and write overhead. InnoDB transactions, primary keys, and foreign keys protect the write path, while indexes reduce the rows examined by read queries.

Availability in this version means crash recovery through the database engine, not uninterrupted service during a node failure. This limitation must not be presented as measured failover capability.

### 3.2 Consistency on the write path

`Enrollment` uses the composite primary key `(mid, class_id)` to prevent duplicate enrolment records. Its foreign keys require both the member and class to exist. `CheckIn.mid`, `Member.membership_id`, and `Class.trainer_id` likewise prevent orphaned operational records. Cancellation updates `is_canceled` rather than deleting the enrolment, preserving the historical record while allowing active-enrolment queries to filter it out.

These constraints favour correctness over unrestricted writes: invalid inserts are rejected, and indexes must be maintained during inserts and updates. This is appropriate because a duplicate enrolment or orphaned check-in is a business error, whereas the small amount of additional write maintenance is acceptable for the stated read-heavy workload.

### 3.3 Latency and reporting

The read paths use indexes and joins rather than repeatedly scanning large child tables. The clearest measured case is the `CheckIn(mid, time)` index: for the fixed `mid = 22` lookup, Section 5 reports a reduction from 7.10 ms to 0.245 ms on the experimental dataset. This result supports a targeted-index policy rather than indexing every column, because each additional index also consumes storage and adds write maintenance.

Management aggregates are kept separate from the core integrity rules. Q1 excludes cancelled enrolments before grouping, Q2 retains zero-class trainers through `LEFT JOIN`, and Q3 groups check-ins by membership type. Thus reporting logic does not weaken the operational constraints.

### 3.4 Boundary of the current architecture

If the deployment later requires service during a node failure or low-latency access across regions, the single-node design will no longer be sufficient. Read replicas could support reporting, but stale replica reads must not be used to make integrity-critical decisions. Enrolment and check-in writes should remain on the primary so that uniqueness and referential integrity continue to be enforced at one authoritative location.

## 6. Discussion and Limitations

- **Test scale:** the experimental dataset is much smaller than a production workload and fits in memory. The measured timings demonstrate behaviour on this environment; they do not establish production-scale throughput or disk-I/O performance.
- **Single node:** crash recovery is not equivalent to high availability. Failover time and replication lag were not measured.
- **Concurrency:** the current evaluation does not include a concurrent stress test. Constraint tests demonstrate rejected invalid writes, but they do not quantify behaviour under heavy contention.
- **Workload assumptions:** the index policy assumes a read-heavy workload. A substantially more write-intensive workload would require reassessing index maintenance costs.
- **Scope:** the six-table model covers membership type, members, check-ins, trainers, classes, and enrolments. Payments, card validity windows, class capacity, and multi-card membership history are outside the implemented schema and are not claimed as supported features.

---

## 编辑说明（不进入最终报告）

原文以下内容未纳入，因为与当前 `sql/CDS534_Topic3_Gym.sql` 或已验证的 Section 5 不一致：

- 会员卡有效期、状态、总次数和剩余次数字段。
- 课程容量与费用、超容量报名事务、财务收入确认。
- 另一套 Q1–Q3、300 Member、300 Membership、120 Class、800 CheckIn、600 Enrollment 数据集。
- 所有 `___` 占位数值及尚未执行的延迟、并发和容量实验。

原稿中关于单节点 CAP 边界、读写路径差异、索引写放大、测试规模和并发局限的论证已保留并改写，但没有把未实现功能描述为现有能力。
