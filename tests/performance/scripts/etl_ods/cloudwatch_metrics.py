"""Fetch CloudWatch metrics for ETL ODS Lambda, SQS, and EventBridge resources.

Collects per-stage latency (p50/p90/p95/p99), error rates, throughput,
and queue health for the ETL ODS pipeline. Exports to console, JSON, or CSV.

Usage:
    ENVIRONMENT=dev python scripts/etl_ods/cloudwatch_metrics.py
    ENVIRONMENT=dev python scripts/etl_ods/cloudwatch_metrics.py --hours 2 --export-csv
    ENVIRONMENT=dev python scripts/etl_ods/cloudwatch_metrics.py --start '2026-03-10 14:00' --end '2026-03-10 15:00'
    ENVIRONMENT=dev WORKSPACE=my-branch python scripts/etl_ods/cloudwatch_metrics.py

Required:  ENVIRONMENT (dev|test|int|ref)
Optional:  WORKSPACE (default: "default"), AWS_REGION (default: eu-west-2),
           AWS_PROFILE (optional)
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import boto3

# Allow running from any directory
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from cloudwatch_config import Config

REPORTS_DIR = SCRIPT_DIR.parent.parent / "reports"


class CloudWatchMetricsFetcher:
    """Fetch CloudWatch metrics for Lambda, SQS, and EventBridge."""

    MAX_DATAPOINTS = 1440

    def __init__(self, region: str | None = None, profile: str | None = None) -> None:
        self.region = region or Config.AWS_REGION

        if profile:
            print(f"Using AWS Profile: {profile}")
            session = boto3.Session(profile_name=profile, region_name=self.region)
            self.client = session.client("cloudwatch")
        else:
            self.client = boto3.client("cloudwatch", region_name=self.region)

        print(f"Region: {self.region}")
        print(f"Environment: {Config.ENVIRONMENT}")
        print(f"Prefix: {Config.get_prefix()}")

    def _calculate_period(
        self,
        start_time: datetime,
        end_time: datetime,
        min_period: int = 60,
    ) -> int:
        duration_seconds = (end_time - start_time).total_seconds()
        required_period = duration_seconds / self.MAX_DATAPOINTS
        valid_periods = [60, 300, 900, 3600, 21600, 86400]

        for period in valid_periods:
            if period >= required_period and period >= min_period:
                return period
        return valid_periods[-1]

    def _get_metric(
        self,
        namespace: str,
        metric_name: str,
        dimensions: list[dict],
        start_time: datetime,
        end_time: datetime,
        period: int,
        statistic: str,
    ) -> list[dict]:
        try:
            response = self.client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=[statistic],
            )
            datapoints = sorted(
                response.get("Datapoints", []), key=lambda x: x["Timestamp"]
            )
            return [
                {
                    "timestamp": dp["Timestamp"].isoformat(),
                    "value": dp.get(statistic, 0),
                }
                for dp in datapoints
            ]
        except Exception as e:
            print(f"  Warning: {metric_name} ({statistic}): {e}")
            return []

    def _get_percentile_metric(
        self,
        namespace: str,
        metric_name: str,
        dimensions: list[dict],
        start_time: datetime,
        end_time: datetime,
        period: int,
        percentile: int,
    ) -> list[dict]:
        """Fetch percentile metrics (p50, p90, p95, p99)."""
        try:
            response = self.client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                ExtendedStatistics=[f"p{percentile}"],
            )
            datapoints = sorted(
                response.get("Datapoints", []), key=lambda x: x["Timestamp"]
            )
            return [
                {
                    "timestamp": dp["Timestamp"].isoformat(),
                    "value": dp.get("ExtendedStatistics", {}).get(
                        f"p{percentile}", 0
                    ),
                }
                for dp in datapoints
            ]
        except Exception as e:
            print(f"  Warning: {metric_name} (p{percentile}): {e}")
            return []

    def get_lambda_metrics(
        self,
        function_name: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        period: int | None = None,
    ) -> dict[str, Any]:
        end_time = end_time or datetime.now(timezone.utc)
        start_time = start_time or (end_time - timedelta(hours=1))

        if period is None:
            period = self._calculate_period(start_time, end_time)

        dims = [{"Name": "FunctionName", "Value": function_name}]

        return {
            "function_name": function_name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "period_seconds": period,
            "invocations": self._get_metric(
                "AWS/Lambda", "Invocations", dims, start_time, end_time, period, "Sum"
            ),
            "errors": self._get_metric(
                "AWS/Lambda", "Errors", dims, start_time, end_time, period, "Sum"
            ),
            "throttles": self._get_metric(
                "AWS/Lambda", "Throttles", dims, start_time, end_time, period, "Sum"
            ),
            "concurrent_executions": self._get_metric(
                "AWS/Lambda",
                "ConcurrentExecutions",
                dims,
                start_time,
                end_time,
                period,
                "Maximum",
            ),
            "duration_avg": self._get_metric(
                "AWS/Lambda",
                "Duration",
                dims,
                start_time,
                end_time,
                period,
                "Average",
            ),
            "duration_min": self._get_metric(
                "AWS/Lambda",
                "Duration",
                dims,
                start_time,
                end_time,
                period,
                "Minimum",
            ),
            "duration_max": self._get_metric(
                "AWS/Lambda",
                "Duration",
                dims,
                start_time,
                end_time,
                period,
                "Maximum",
            ),
            "duration_p50": self._get_percentile_metric(
                "AWS/Lambda", "Duration", dims, start_time, end_time, period, 50
            ),
            "duration_p90": self._get_percentile_metric(
                "AWS/Lambda", "Duration", dims, start_time, end_time, period, 90
            ),
            "duration_p95": self._get_percentile_metric(
                "AWS/Lambda", "Duration", dims, start_time, end_time, period, 95
            ),
            "duration_p99": self._get_percentile_metric(
                "AWS/Lambda", "Duration", dims, start_time, end_time, period, 99
            ),
        }

    def get_sqs_metrics(
        self,
        queue_name: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        period: int | None = None,
    ) -> dict[str, Any]:
        end_time = end_time or datetime.now(timezone.utc)
        start_time = start_time or (end_time - timedelta(hours=1))

        if period is None:
            period = self._calculate_period(start_time, end_time)

        dims = [{"Name": "QueueName", "Value": queue_name}]

        return {
            "queue_name": queue_name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "period_seconds": period,
            "messages_sent": self._get_metric(
                "AWS/SQS",
                "NumberOfMessagesSent",
                dims,
                start_time,
                end_time,
                period,
                "Sum",
            ),
            "messages_received": self._get_metric(
                "AWS/SQS",
                "NumberOfMessagesReceived",
                dims,
                start_time,
                end_time,
                period,
                "Sum",
            ),
            "messages_visible": self._get_metric(
                "AWS/SQS",
                "ApproximateNumberOfMessagesVisible",
                dims,
                start_time,
                end_time,
                period,
                "Average",
            ),
            "oldest_message_age_avg": self._get_metric(
                "AWS/SQS",
                "ApproximateAgeOfOldestMessage",
                dims,
                start_time,
                end_time,
                period,
                "Average",
            ),
            "oldest_message_age_max": self._get_metric(
                "AWS/SQS",
                "ApproximateAgeOfOldestMessage",
                dims,
                start_time,
                end_time,
                period,
                "Maximum",
            ),
        }

    def get_eventbridge_metrics(
        self,
        rule_name: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        period: int | None = None,
    ) -> dict[str, Any]:
        end_time = end_time or datetime.now(timezone.utc)
        start_time = start_time or (end_time - timedelta(hours=1))

        if period is None:
            period = self._calculate_period(start_time, end_time)

        dims = [{"Name": "RuleName", "Value": rule_name}]

        return {
            "rule_name": rule_name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "period_seconds": period,
            "invocations": self._get_metric(
                "AWS/Events",
                "Invocations",
                dims,
                start_time,
                end_time,
                period,
                "Sum",
            ),
            "failed_invocations": self._get_metric(
                "AWS/Events",
                "FailedInvocations",
                dims,
                start_time,
                end_time,
                period,
                "Sum",
            ),
        }

    def get_summary(self, metrics: dict[str, Any]) -> dict[str, dict]:
        """Compute min/max/avg/total/count for each metric series."""
        summary: dict[str, dict] = {}
        for key, values in metrics.items():
            if isinstance(values, list) and len(values) > 0:
                data = [v["value"] for v in values if v["value"] is not None]
                if data:
                    summary[key] = {
                        "min": min(data),
                        "max": max(data),
                        "avg": sum(data) / len(data),
                        "total": sum(data),
                        "count": len(data),
                    }
        return summary

    def print_metrics(self, metrics: dict[str, Any]) -> None:
        """Print detailed metrics for a single resource."""
        print("\n" + "=" * 70)
        name = (
            metrics.get("function_name")
            or metrics.get("queue_name")
            or metrics.get("rule_name")
            or "Unknown"
        )
        print(f"Resource: {name}")
        print(f"Period: {metrics.get('start_time')} to {metrics.get('end_time')}")
        print(f"Resolution: {metrics.get('period_seconds', 60)} seconds")
        print("-" * 70)

        summary = self.get_summary(metrics)
        if not summary:
            print("  No data available")
            return

        duration_metrics = {k: v for k, v in summary.items() if "duration" in k}
        other_metrics = {k: v for k, v in summary.items() if "duration" not in k}

        for key, stats in other_metrics.items():
            print(f"  {key}:")
            print(
                f"    Total: {stats['total']:.2f} | "
                f"Avg: {stats['avg']:.2f} | "
                f"Min: {stats['min']:.2f} | "
                f"Max: {stats['max']:.2f}"
            )

        if duration_metrics:
            print(f"\n  {'─' * 40}")
            print("  DURATION METRICS (milliseconds)")
            print(f"  {'─' * 40}")

            for key, stats in duration_metrics.items():
                label = key.replace("duration_", "").upper()
                print(
                    f"    {label:6}: {stats['avg']:.2f} ms "
                    f"(min: {stats['min']:.2f}, max: {stats['max']:.2f})"
                )

    def print_performance_summary(self, all_metrics: dict[str, dict]) -> None:
        """Print a performance summary table with percentile latencies."""
        print("\n" + "=" * 70)
        print("PERFORMANCE SUMMARY - LATENCY PERCENTILES")
        print("=" * 70)
        print(
            f"{'Resource':<45} {'P50 (ms)':<12} {'P90 (ms)':<12} {'P99 (ms)':<12}"
        )
        print("-" * 70)

        for name, metrics in all_metrics.items():
            summary = self.get_summary(metrics)

            p50 = summary.get("duration_p50", {}).get("avg", 0)
            p90 = summary.get("duration_p90", {}).get("avg", 0)
            p99 = summary.get("duration_p99", {}).get("avg", 0)

            display_name = name[:43] + ".." if len(name) > 45 else name
            print(f"{display_name:<45} {p50:<12.2f} {p90:<12.2f} {p99:<12.2f}")

        print("=" * 70)

    def fetch_etl_ods_metrics(
        self,
        hours: int = 1,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> dict[str, dict]:
        """Fetch all ETL ODS metrics for the given time window.

        If --start/--end are provided they take precedence over --hours.
        """
        if start or end:
            end_time = end or datetime.now(timezone.utc)
            start_time = start or (end_time - timedelta(hours=hours))
            label = f"{start_time.isoformat()} → {end_time.isoformat()}"
        else:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            label = f"Last {hours} hour(s)"

        period = self._calculate_period(start_time, end_time)

        print(f"\n{'=' * 70}")
        print(f"ETL-ODS CloudWatch Metrics ({label})")
        print(f"{'=' * 70}")
        print(f"From: {start_time.isoformat()}")
        print(f"To:   {end_time.isoformat()}")
        print(f"Period: {period} seconds ({period // 60} minutes)")

        all_metrics: dict[str, dict] = {}

        # Lambda functions
        print("\n>>> LAMBDA METRICS <<<")
        for func_name in Config.get_lambda_functions():
            print(f"\nFetching: {func_name}")
            try:
                metrics = self.get_lambda_metrics(
                    func_name, start_time, end_time, period
                )
                self.print_metrics(metrics)
                all_metrics[func_name] = metrics
            except Exception as e:
                print(f"  Error: {e}")

        # SQS queues
        print("\n>>> SQS METRICS <<<")
        for queue_name in Config.get_sqs_queues():
            print(f"\nFetching: {queue_name}")
            try:
                metrics = self.get_sqs_metrics(
                    queue_name, start_time, end_time, period
                )
                self.print_metrics(metrics)
                all_metrics[queue_name] = metrics
            except Exception as e:
                print(f"  Error: {e}")

        # DLQs
        print("\n>>> DLQ METRICS <<<")
        for dlq_name in Config.get_sqs_dlqs():
            print(f"\nFetching: {dlq_name}")
            try:
                metrics = self.get_sqs_metrics(
                    dlq_name, start_time, end_time, period
                )
                self.print_metrics(metrics)
                all_metrics[dlq_name] = metrics
            except Exception as e:
                print(f"  Error: {e}")

        # EventBridge schedule
        print("\n>>> EVENTBRIDGE METRICS <<<")
        rule_name = Config.get_eventbridge_rule()
        print(f"\nFetching: {rule_name}")
        try:
            metrics = self.get_eventbridge_metrics(
                rule_name, start_time, end_time, period
            )
            self.print_metrics(metrics)
            all_metrics[rule_name] = metrics
        except Exception as e:
            print(f"  Error: {e}")

        # Performance summary
        self.print_performance_summary(all_metrics)

        print(f"\n{'=' * 70}")
        print("Report Complete")
        print(f"{'=' * 70}\n")

        return all_metrics

    def export_to_json(
        self, metrics: dict[str, dict], filename: str | None = None
    ) -> None:
        """Export full metrics to JSON."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        if not filename:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = str(REPORTS_DIR / f"etl_metrics_{timestamp}.json")
        with open(filename, "w") as f:
            json.dump(metrics, f, indent=2, default=str)
        print(f"Exported to: {filename}")

    def export_to_csv(
        self, metrics: dict[str, dict], filename: str | None = None
    ) -> None:
        """Export performance summary to CSV."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        if not filename:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = str(REPORTS_DIR / f"etl_latency_report_{timestamp}.csv")

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Resource",
                    "P50_ms",
                    "P90_ms",
                    "P95_ms",
                    "P99_ms",
                    "Avg_ms",
                    "Max_ms",
                    "Invocations",
                    "Errors",
                ]
            )

            for name, m in metrics.items():
                summary = self.get_summary(m)
                writer.writerow(
                    [
                        name,
                        f"{summary.get('duration_p50', {}).get('avg', 0):.2f}",
                        f"{summary.get('duration_p90', {}).get('avg', 0):.2f}",
                        f"{summary.get('duration_p95', {}).get('avg', 0):.2f}",
                        f"{summary.get('duration_p99', {}).get('avg', 0):.2f}",
                        f"{summary.get('duration_avg', {}).get('avg', 0):.2f}",
                        f"{summary.get('duration_max', {}).get('max', 0):.2f}",
                        f"{summary.get('invocations', {}).get('total', 0):.0f}",
                        f"{summary.get('errors', {}).get('total', 0):.0f}",
                    ]
                )

        print(f"Latency report exported to: {filename}")


def _parse_datetime(value: str) -> datetime:
    """Parse a datetime string in common formats.

    Supported formats:
        2026-03-10T14:00:00       (local, treated as UTC)
        2026-03-10T14:00:00Z      (explicit UTC)
        2026-03-10 14:00:00       (space-separated)
        2026-03-10 14:00          (no seconds)
        2026-03-10                (date only, midnight UTC)
    """
    value = value.strip()
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"Invalid datetime: '{value}'. "
        "Use YYYY-MM-DD, 'YYYY-MM-DD HH:MM', or YYYY-MM-DDTHH:MM:SS"
    )


def main() -> None:
    """CLI entry point for ETL ODS CloudWatch metrics."""
    parser = argparse.ArgumentParser(
        description="Fetch CloudWatch Metrics for ETL-ODS pipeline"
    )
    parser.add_argument(
        "--hours", "-t", type=int, default=1, help="Hours to look back (default: 1)"
    )
    parser.add_argument(
        "--start",
        type=_parse_datetime,
        default=None,
        help="Start time (e.g. '2026-03-10 14:00'). Overrides --hours.",
    )
    parser.add_argument(
        "--end",
        type=_parse_datetime,
        default=None,
        help="End time (default: now). Use with --start.",
    )
    parser.add_argument(
        "--profile", type=str, help="AWS profile name (overrides AWS_PROFILE env var)"
    )
    parser.add_argument(
        "--export-json", action="store_true", help="Export full metrics to JSON"
    )
    parser.add_argument(
        "--export-csv", action="store_true", help="Export latency summary to CSV"
    )
    args = parser.parse_args()

    fetcher = CloudWatchMetricsFetcher(profile=args.profile)
    metrics = fetcher.fetch_etl_ods_metrics(
        hours=args.hours, start=args.start, end=args.end
    )

    if args.export_json:
        fetcher.export_to_json(metrics)

    if args.export_csv:
        fetcher.export_to_csv(metrics)


if __name__ == "__main__":
    main()
