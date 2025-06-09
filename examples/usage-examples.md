# ServiceNow MCP Server Usage Examples

This document provides practical examples of using the ServiceNow MCP Server with MCP-compatible tools and IDEs.

## Table of Contents

- [Incident Management](#incident-management)
- [Change Management](#change-management)
- [CMDB Operations](#cmdb-operations)
- [User Management](#user-management)
- [Knowledge Base](#knowledge-base)
- [Custom Tables](#custom-tables)
- [Advanced Queries](#advanced-queries)

## Incident Management

### Create a High Priority Incident

```
Create a high priority incident for the email server being down. Assign it to the Email Support group.
```

Tool invocation:
```json
{
  "tool": "incident_create",
  "arguments": {
    "short_description": "Email server down",
    "description": "Production email server is not responding to requests",
    "urgency": 1,
    "impact": 1,
    "assignment_group": "Email Support"
  }
}
```

### Update Incident with Work Notes

```
Update incident INC0000123 to In Progress state and add work notes that we're investigating the issue.
```

Tool invocation:
```json
{
  "tool": "incident_update",
  "arguments": {
    "number": "INC0000123",
    "state": 2,
    "work_notes": "Investigating the issue. Initial analysis shows network connectivity problems."
  }
}
```

### Search for Open Incidents

```
Find all open incidents assigned to me with high priority.
```

Tool invocation:
```json
{
  "tool": "incident_search",
  "arguments": {
    "assigned_to": "current.user",
    "state": [1, 2, 3],
    "priority": [1],
    "limit": 50
  }
}
```

### Resolve an Incident

```
Resolve incident INC0000123 with resolution code "Solved (Permanently)" and notes about replacing the faulty hardware.
```

Tool invocation:
```json
{
  "tool": "incident_update",
  "arguments": {
    "number": "INC0000123",
    "state": 6,
    "resolution_code": "Solved (Permanently)",
    "resolution_notes": "Replaced faulty network card in the email server. Server is now fully operational."
  }
}
```

## Change Management

### Create an Emergency Change

```
Create an emergency change request to patch critical security vulnerability in the web server.
```

Tool invocation:
```json
{
  "tool": "change_create",
  "arguments": {
    "short_description": "Emergency security patch for web server",
    "description": "Critical vulnerability CVE-2024-1234 needs immediate patching",
    "type": "emergency",
    "risk": 1,
    "impact": 1,
    "assignment_group": "Web Services Team",
    "start_date": "2024-01-15 02:00:00",
    "end_date": "2024-01-15 04:00:00"
  }
}
```

### Create a Standard Change

```
Create a standard change for monthly Windows updates on production servers.
```

Tool invocation:
```json
{
  "tool": "change_create",
  "arguments": {
    "short_description": "Monthly Windows Updates - Production Servers",
    "description": "Standard monthly Windows security and stability updates",
    "type": "standard",
    "risk": 3,
    "impact": 2,
    "assignment_group": "Windows Server Team",
    "start_date": "2024-02-01 02:00:00",
    "end_date": "2024-02-01 06:00:00"
  }
}
```

## CMDB Operations

### Search for Production Servers

```
Find all production web servers that are currently operational.
```

Tool invocation:
```json
{
  "tool": "ci_search",
  "arguments": {
    "name": "*web*",
    "class": "cmdb_ci_server",
    "operational_status": 1,
    "environment": "production",
    "limit": 100
  }
}
```

### Get CI Relationships

```
Show me all the dependencies for the main database server PROD-DB-01.
```

The assistant will first search for the CI:
```json
{
  "tool": "ci_search",
  "arguments": {
    "name": "PROD-DB-01"
  }
}
```

Then get its relationships:
```json
{
  "tool": "ci_relationships",
  "arguments": {
    "ci_sys_id": "<sys_id_from_search>"
  }
}
```

## User Management

### Find Users in a Department

```
List all active users in the IT department.
```

Tool invocation:
```json
{
  "tool": "user_search",
  "arguments": {
    "department": "Information Technology",
    "active": true,
    "limit": 100
  }
}
```

### Search for a Specific User

```
Find the user John Doe's account information.
```

Tool invocation:
```json
{
  "tool": "user_search",
  "arguments": {
    "name": "John Doe",
    "limit": 10
  }
}
```

## Knowledge Base

### Search for Password Reset Articles

```
Find knowledge articles about password reset procedures.
```

Tool invocation:
```json
{
  "tool": "kb_search",
  "arguments": {
    "query": "password reset",
    "workflow_state": "published",
    "limit": 10
  }
}
```

### Search in Specific Category

```
Find all published VPN setup guides.
```

Tool invocation:
```json
{
  "tool": "kb_search",
  "arguments": {
    "query": "VPN setup",
    "workflow_state": "published",
    "limit": 20
  }
}
```

## Custom Tables

### Query Custom Application Registry

```
Show me all active applications in our custom application registry that are in production.
```

Tool invocation:
```json
{
  "tool": "query_table",
  "arguments": {
    "table": "u_application_registry",
    "query": "u_active=true^u_environment=production",
    "fields": ["u_app_name", "u_version", "u_owner", "u_last_updated"],
    "order_by": "-u_last_updated",
    "limit": 50
  }
}
```

### Create Custom Record

```
Add a new entry to our vendor management table for Acme Corp.
```

Tool invocation:
```json
{
  "tool": "create_record",
  "arguments": {
    "table": "u_vendor_management",
    "data": {
      "u_vendor_name": "Acme Corp",
      "u_contact_email": "support@acmecorp.com",
      "u_contract_start": "2024-01-01",
      "u_contract_end": "2024-12-31",
      "u_status": "active"
    }
  }
}
```

## Advanced Queries

### Get Incident Statistics by Priority

```
Show me incident statistics grouped by priority for this month.
```

Tool invocation:
```json
{
  "tool": "get_stats",
  "arguments": {
    "table": "incident",
    "group_by": ["priority"],
    "aggregates": [
      {
        "type": "COUNT",
        "field": "sys_id",
        "alias": "total_count"
      },
      {
        "type": "AVG",
        "field": "u_resolution_time",
        "alias": "avg_resolution_time"
      }
    ],
    "query": "sys_created_on>=javascript:gs.beginningOfThisMonth()"
  }
}
```

### Complex Multi-Condition Search

```
Find all incidents that are either high priority unassigned tickets or medium priority tickets older than 7 days.
```

Tool invocation:
```json
{
  "tool": "incident_search",
  "arguments": {
    "text_search": "",
    "limit": 100
  }
}
```

Then apply custom query:
```json
{
  "tool": "query_table",
  "arguments": {
    "table": "incident",
    "query": "(priority=1^assigned_toISEMPTY)^OR(priority=2^sys_created_on<javascript:gs.daysAgo(7))",
    "fields": ["number", "short_description", "priority", "assigned_to", "sys_created_on"],
    "order_by": "priority,sys_created_on",
    "limit": 100
  }
}
```

## Integration Tips

### VS Code / Cursor

When using with VS Code or Cursor, you can:
- "Check for any P1 incidents before I deploy this code"
- "Create a change request for this deployment"
- "Find the CI record for the server I'm deploying to"

### Desktop Clients

With MCP desktop clients, you can:
- Monitor your team's incident queue
- Create knowledge articles about resolved issues
- Update the CMDB with newly provisioned servers

### Automation Scripts

You can also use the MCP server in automation:
- Pre-deployment checks for active incidents
- Post-deployment CMDB updates
- Automated incident creation from monitoring alerts
- Scheduled report generation

## Best Practices

1. **Use specific queries**: The more specific your request, the better the results
2. **Leverage display values**: The server returns both values and display values for reference fields
3. **Batch operations**: When possible, use bulk queries instead of individual lookups
4. **Monitor rate limits**: The server handles rate limiting automatically, but be mindful of API usage
5. **Secure credentials**: Always use environment variables or secure vaults for credentials