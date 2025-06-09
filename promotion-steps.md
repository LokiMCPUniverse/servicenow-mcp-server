# Manual Promotion Steps for ServiceNow MCP Server

## 1. Complete awesome-mcp-servers Pull Request

The changes have been prepared locally. Complete these steps:

1. Fork https://github.com/wong2/awesome-mcp-servers on GitHub
2. Add your fork as remote:
   ```bash
   cd /Users/lokesh/git/MCP-Servers/awesome-mcp-servers
   git remote add myfork https://github.com/asklokesh/awesome-mcp-servers.git
   ```
3. Push the branch:
   ```bash
   git push -u myfork add-servicenow-mcp-server
   ```
4. Create PR on GitHub with title: "Add ServiceNow MCP Server to Community Servers"

## 2. Add GitHub Topics

Go to https://github.com/asklokesh/servicenow-mcp-server/settings and add these topics:
- servicenow
- mcp
- model-context-protocol
- api-integration
- incident-management
- change-management
- cmdb
- itsm
- itil
- python
- async
- automation
- enterprise
- api-client
- devops

## 3. Update Repository Description

In repository settings, update description to:
"Enterprise ServiceNow integration via Model Context Protocol. Complete API coverage for ITSM, CMDB, and Service Catalog. Async Python with comprehensive error handling."

## 4. Submit to Other Awesome Lists

### awesome-servicenow
- Repository: https://github.com/ServiceNowDevProgram/awesome-servicenow
- Add under "Tools & Utilities" section:
  ```markdown
  - **[ServiceNow MCP Server](https://github.com/asklokesh/servicenow-mcp-server)** - Model Context Protocol server for ServiceNow API integration. Enables seamless integration with modern development tools and automation frameworks. Supports all major ServiceNow modules with async Python implementation.
  ```

### awesome-python
- Repository: https://github.com/vinta/awesome-python
- Add under "Third Party APIs" section:
  ```markdown
  - [servicenow-mcp-server](https://github.com/asklokesh/servicenow-mcp-server) - Async Python client and MCP server for ServiceNow API integration.
  ```

## 5. Post Announcements

Use the templates in ANNOUNCEMENT_TEMPLATE.md to post on:
- Reddit: r/servicenow, r/devops
- LinkedIn
- Twitter/X
- Dev.to or Hashnode

## 6. ServiceNow Community

Post in the ServiceNow Community Forum:
- https://community.servicenow.com/
- Post in the Developer forum section

## Status Tracker

- [ ] awesome-mcp-servers PR submitted
- [ ] GitHub topics added
- [ ] Repository description updated
- [ ] awesome-servicenow PR submitted
- [ ] awesome-python PR submitted
- [ ] Reddit posts created
- [ ] LinkedIn announcement posted
- [ ] Twitter/X thread posted
- [ ] Dev.to article published
- [ ] ServiceNow Community post created