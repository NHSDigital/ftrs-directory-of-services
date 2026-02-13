# Slack Notifier Service

A reusable service for sending CloudWatch alarm notifications to Slack channels.

## Overview

This service processes CloudWatch alarm notifications from SNS topics and formats them for Slack delivery. It provides a clean, formatted view of AWS alarms with relevant context and links.

## Features

- Formats CloudWatch alarms for Slack
- Supports multiple alarm types
- Provides AWS console links
- Configurable Slack webhook integration

## Usage

The service is triggered automatically by SNS notifications from CloudWatch alarms. Configure your CloudWatch alarms to publish to the SNS topic that triggers this Lambda function.

## Configuration

Set the `SLACK_WEBHOOK_URL` environment variable to your Slack webhook URL.

## Development

```bash
make install   # Install dependencies
make lint      # Run linting
make test      # Run tests
make build     # Build artifacts
```
