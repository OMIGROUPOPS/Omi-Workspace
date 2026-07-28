# Integrated P0 v1-v4 + CASUKA D1-D3 DEPLOYMENT AUTHORIZATION V2

This canonical report authorizes one ceremony. The authorization commit is supplied separately and is intentionally absent from the payload.

```json
{
  "authorization_commit_supplied_separately": true,
  "authorization_report_path": ".claude/audit_20260728_integrated_live_safety_prerun/EXECUTION_AUTHORIZATION_DEPLOYMENT_V2.md",
  "authorization_state": "AUTHORIZED_ONCE",
  "backup_path": "/root/Omi-Workspace/arb-executor/live_v4.py.pre-integrated-p0v4-casuka.integrated-p0v4-casuka-deploy-20260728-attempt1.bak",
  "candidate": {
    "bytes": 1047115,
    "git_blob_oid": "d7d7cd1d6e9ca28863e97ed8593e0fbf4c87e223",
    "sha256": "62614501cb9708bb3c3c2b35823ba8431b2e95acdc027f659a4b37a66a777034"
  },
  "candidate_retry_after_mutation": "FORBIDDEN",
  "casuka_d1_d3_pass": "66136e6240f2adda990ea8fddc7e00cc643cfb4c",
  "casuka_repair": "94be41137c0b64bfa448546c8bc3ee7c4ae32a60",
  "ceremony_command_template": "OUTCOME_PROOF=\".claude/integrated_live_safety_prerun_20260728/PRE_DEPLOYMENT_OUTCOME_PROOF_CONTRACT.json\" python -B arb-executor/deploy/integrated_live_safety_ceremony_v1.py --repo . --control .claude/integrated_live_safety_prerun_20260728/DEPLOYMENT_CONTROL_V1.json --mode execute --package-audit-pass \"$PACKAGE_AUDIT_PASS\" --authorization-commit \"$AUTHORIZATION_COMMIT\" --authorization-report \"$AUTHORIZATION_REPORT\"",
  "deployment_command": "OUTCOME_PROOF=/root/Omi-Workspace/.claude/integrated_live_safety_results_integrated-p0v4-casuka-deploy-20260728-attempt1/PRE_DEPLOYMENT_OUTCOME_PROOF_CONTRACT.json OUTCOME_PROOF_SHA=11e70454863e3508d5a7cbc8e83162232e3a4a09 /root/Omi-Workspace/arb-executor/deploy/deploy_live_v4.sh 11e70454863e3508d5a7cbc8e83162232e3a4a09",
  "deployment_id": "integrated-p0v4-casuka-deploy-20260728-attempt1",
  "failed_v1_authorization_superseded": "8a142c8623afb498f61be23d4b710af1834c856a",
  "host": "root@104.131.191.95",
  "integration_commit": "11e70454863e3508d5a7cbc8e83162232e3a4a09",
  "outcome_proof_contract": {
    "path": ".claude/integrated_live_safety_prerun_20260728/PRE_DEPLOYMENT_OUTCOME_PROOF_CONTRACT.json",
    "sha256": "38c6daee4f3b231e2dfc24dd13708b50eb2ba831f8d76d13920936fa4d8f50f0",
    "status": "PRE_DEPLOYMENT_CONTRACT_ACTIVE"
  },
  "p0_v4_pass": "cac1a144342de6d99c0d2701e355ce63745063b0",
  "package_audit_pass": "3e84c1c8f3f2c397b41255ef815a271d9364c7cd",
  "package_commit": "1dd5787cfe00f8c69488fff1c9c93fbb7c3eb0a1",
  "preimage": {
    "bytes": 997352,
    "git_blob_oid": "f1857199164664037fef41b024e60f27fa373548",
    "sha256": "834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54"
  },
  "results_dir": ".claude/integrated_live_safety_results_integrated-p0v4-casuka-deploy-20260728-attempt1/",
  "rollback_command": "ssh root@104.131.191.95 bash -se -- /root/Omi-Workspace/arb-executor/live_v4.py /root/Omi-Workspace/arb-executor/live_v4.py.pre-integrated-p0v4-casuka.integrated-p0v4-casuka-deploy-20260728-attempt1.bak live_v4 834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54 997352 /var/spool/cron/crontabs/root 0e2af22e4ab536b4273e61d9251359eda71e369fb8591f22443c66aa88709926 /root/root.crontab.pre_schedule_liar_stop_20260728_e7004235.raw 4c38967f85112908020b7207f491a8486cbfc9c70a8b9d6c8cc5d0a2500c98f4 < arb-executor/deploy/integrated_live_safety_rollback_v1.sh",
  "rollback_commit": "904a1993030c09c839a56ff78d5a7dc0dfd13b99",
  "schema_version": "integrated-live-safety-deployment-authorization-v1",
  "service": "live_v4",
  "target_path": "/root/Omi-Workspace/arb-executor/live_v4.py"
}
```
