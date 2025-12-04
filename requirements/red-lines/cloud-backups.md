# Immutable Cloud Backups

## Summary

Teams within Products & Platforms operating on the following cloud platforms must use the following blueprints for immutable cloud backups. Teams must not build bespoke solutions, or use other backup services, without prior approval from the Engineering Board

- [Blueprint for cloud backups on AWS (v1.1)](https://github.com/NHSDigital/terraform-aws-backup/tree/v1.1.0)

  - Version 1 is in production with 1 team and is ready to be adopted by other teams
  - Version 2 is expected to focus on ease of adoption
  - There will continue to be more to add (e.g. modules for additional AWS services, support for multiple alerting options, etc) - adopting teams should enrich the blueprint as they adopt it
  - Note: AWS air-gapped vaults (recently announced) will be considered for a future version of the blueprint

- [Blueprint for cloud backups on Azure](https://github.com/NHSDigital/az-backup)
  - Version 1 under construction: design details have been discussed with and supported by Microsoft
  - Teams are encouraged to get involved with building out the blueprint

Note: we may (later) combine the 2 repositories above into a single backups blueprint repository

Teams must consume the above solutions and be ready to upgrade to new versions of the blueprint as required:

- Note: crafting bespoke solutions based on the blueprints is not acceptable, because teams must ensure they can uplift to new versions of the blueprint as required - in practice, this means teams should consume the blueprint as terraform modules rather than copying-and-pasting code from the blueprint into their own repositories
- This page will hold the current version teams are required to use, and instructions to upgrade where necessary will be communicated by the Engineering Board

Teams must add any new functionality to the blueprint rather than building bespoke additions into their products. For example, if a team adopts the blueprint and finds it includes teams alerts but the team would prefer slack alerts: the team must add support for slack alerts into the blueprint so that other teams can benefit from the enhancement

## Frequently Asked Questions

### What do we mean by “have an immutable backup”

Specifically we mean that you have followed the Immutable backup Blueprints for your Cloud provider, and you have a “locked” archive in a dedicated account as per the blue print, note, if you have an archive in a dedicated account but have not locked this yet then you do not have an immutable backup for this purpose. Therefore, any recovery testing you do in the meantime will need to be re-run once the archive is locked, to prove that locking the archive doesn't break the recovery process.

### How long should I retain my immutable backup?

This is a product question: the right retention period (both as a minimum and a maximum) will depend on the specifics of your service and its data. If you have no other number to work with, assume as a starting point that you should keep daily backups for at least 30 days in immutable storage. If you are backing up less frequently then please come and talk to us as we likely will require you to have more backups. The expectation is that we would only ever need an immutable backup for a restore in the last month. The service may wish to keep backups longer than the immutable period, for audit purposes say that is also okay if needed. We are asking for a month of backups as we are accounting for situations where we might not notice data corruption immediately and/or for situations around bank holidays etc. to avoid situations where all copies expire before the team detects the failure.

### What data should I backup?

There are a range of data items that must be backed up - the requirements will be specific to each team, however the data that you back up must support you in being able to restore a functioning service. note this doesn't have to include all historical data - we are specifically looking for only the data that is essential to restore the service.

Non-essential (for the operation of your service) data should be considered out of scope for immutable backups - for example we wouldn't expect log files to be stored immutably if you do not require those log files to recover your service. Teams may even choose not to backup this data at all.

## What non data do I need to backup?

The scenarios we are planning for will mean that your production build and source code are not accessible, so teams should backup any other files they need to restore production and keep them in an immutable store for at least 30 days. These items needed to restore the service may include: configuration information, the production build, secrets, certificates. System/release files that change more slowly should have at least 2 copies kept in an immutable backup store for at least 30 days.

Note: the GitHub admins are providing a shared solution for immutable backups of repositories in <https://github.com/NHSDigital>

## What testing do I need to do?

Please see the test scenarios for cloud-5 and cloud-6.

## Supporting Details

This position is based on the work of the cloud backups working group:

- Requirements for cloud backups
- Options analysis for technologies to support cloud backups

## Governance Audit

- This position was discussed at TRG on 04/09/2024 during review of SDO-2720 NHS Backup as a Service (BaaS) in which it was agreed that BaaS will be appropriate for other contexts (e.g. corporate ICT) but not to teams in Products & Platforms
- Classification of cloud-native backup services as “mainstream” was agreed at the Engineering Board in September 2024
