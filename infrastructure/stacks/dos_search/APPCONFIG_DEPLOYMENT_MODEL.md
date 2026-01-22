# AppConfig Alarm Thresholds - Updated Deployment Model

## Summary

The alarm thresholds system has been refactored to use **AppConfig as the live source of truth**. This enables operational teams to update thresholds via the AWS GUI without redeployment.

## Deployment Workflow

### Initial Setup (One-time, requires Terraform)

```bash
# Step 1: Create AppConfig application
cd infrastructure/stacks/app_config
terraform apply

# Step 2: Deploy dos_search stack (reads initial config from AppConfig)
cd infrastructure/stacks/dos_search
terraform apply
```

✅ CloudWatch alarms are now created with initial thresholds from AppConfig

### Ongoing Updates (No Terraform required)

**For Ops Teams** - Update via AWS AppConfig GUI:


1. AWS Console → AppConfig
2. Find: `{environment}-dos-search-alarm-thresholds`
3. Edit configuration JSON
4. Create deployment
5. Run `terraform apply` to sync state (optional but recommended)


**For Infrastructure Teams** - Update via Git:

1. Edit `toggles/alarm-thresholds.json`
2. Commit and merge to main
3. Run `terraform apply` in both app_config and dos_search stacks

## How It Works


### Before (Local File)

```
toggles/alarm-thresholds.json

        ↓ (Terraform reads local file)
CloudWatch Alarms
```


Problem: Any GUI changes to AppConfig would drift from Terraform

### After (AppConfig as Source)


```
AppConfig (Live in AWS)
        ↓ (Terraform reads LIVE via data source)
CloudWatch Alarms (Always in sync)
```


Benefit: GUI changes apply immediately, Terraform stays in sync


## Key Changes

### New Files

- `infrastructure/stacks/dos_search/appconfig_alarms.tf` - Reads **LIVE AppConfig** via data source

### Modified Files


- `infrastructure/stacks/app_config/app_config.tf` - Added alarm_thresholds_app_config module
- `infrastructure/stacks/dos_search/data.tf` - Added app_config remote state reference
- `infrastructure/stacks/dos_search/lambda_cloudwatch_alarms.tf` - All alarms use AppConfig locals
- `infrastructure/stacks/dos_search/APPCONFIG_ALARMS_GUIDE.md` - Updated documentation


## Important Notes

⚠️ **Terraform Reads Live AppConfig Data**

- When you run `terraform apply` in dos_search, it fetches the **current values from AppConfig**
- If you update AppConfig via GUI, the next `terraform apply` will detect those changes
- Terraform state will always reflect the live AppConfig configuration

✅ **No More Local File Dependencies**

- The local `toggles/alarm-thresholds.json` is now only used for **initial AppConfig creation**
- After initial setup, Terraform reads from AppConfig, not the file
- GUI updates to AppConfig take effect on next `terraform apply`

## Benefits

| Feature | Before | After |
|---------|--------|-------|
| **Update without redeployment** | ❌ Required Terraform | ✅ GUI only (with terraform apply to sync) |
| **Real-time effect** | ❌ Required deployment | ✅ Immediate (after terraform apply) |
| **Audit trail** | ❌ Git only | ✅ Git + AppConfig history |
| **Source of truth** | Local file | **Live AppConfig** |
| **Ops-friendly** | ❌ Requires code changes | ✅ GUI updates |

## Common Tasks


### Task 1: Ops wants to increase error threshold for search Lambda

```
1. AWS AppConfig GUI
2. Edit searchLambda.errors.threshold: 5 → 10
3. Deploy in AppConfig
4. Run: cd infrastructure/stacks/dos_search && terraform apply
5. Done! (CloudWatch alarm updated immediately)
```


### Task 2: Infrastructure team makes permanent config change

```
1. Edit toggles/alarm-thresholds.json
2. Commit to main
3. cd infrastructure/stacks/app_config && terraform apply
4. cd infrastructure/stacks/dos_search && terraform apply
5. Done! (Changes tracked in Git)
```

### Task 3: Lambda needs to read live thresholds at runtime

```python
# See APPCONFIG_ALARMS_GUIDE.md for Lambda code example
# Lambda uses AWS AppConfig Extension Layer to read live config

## Troubleshooting

**Q: I updated AppConfig but Terraform shows drift**
A: Run `terraform apply` in dos_search stack. Terraform will read the live AppConfig values and update alarms.

**Q: I want to revert a GUI change**
A: Use AppConfig version history to rollback, then run `terraform apply` to sync.

**Q: What if I edit both toggles/alarm-thresholds.json AND AppConfig?**
A: Terraform will use the live AppConfig values (not the local file). The file is only used during initial app_config stack deployment.
