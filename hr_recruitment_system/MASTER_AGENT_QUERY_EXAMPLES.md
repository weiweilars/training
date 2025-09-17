# Master Agent Query Examples

## 1. Complete End-to-End Hiring Process

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Execute complete hiring process for Senior Software Engineer role: source candidates, screen resumes, schedule interviews, conduct assessments, generate offers, handle negotiations, and ensure compliance. Track metrics throughout."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → All 3 Teams → 11 Individual Agents → 28 MCP Tools

## 2. Job Creation and Posting

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Create a new job posting for a Python Developer position with 5+ years experience, remote work option, competitive salary range $120-150k, and post it to multiple job boards."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → Acquisition Team → Job Requisition Agent → Job Creation/Workflow/Templates tools

## 3. Bulk Hiring Campaign

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Launch hiring campaign for 5 engineering positions: 2 Senior Engineers, 2 Data Scientists, 1 DevOps Lead. Coordinate parallel processing across all teams while maintaining quality standards."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → All Teams (parallel) → Multiple Agents (parallel) → Multiple Tools

## 4. Emergency/Urgent Hiring

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Handle urgent hiring request for critical DevOps Engineer role needed within 2 weeks. Prioritize speed while maintaining compliance and quality. Coordinate expedited workflow across all teams."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → Teams (expedited sequential) → Agents (priority mode) → Tools

## 5. Candidate Sourcing and Screening

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Find and screen candidates for a Frontend Developer position. Search LinkedIn, GitHub, and Stack Overflow for React specialists with 3+ years experience. Perform initial resume screening and background checks."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → Acquisition Team → Sourcing/Screening/Background Agents → Relevant Tools

## 6. Interview Coordination

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Schedule interviews for 5 shortlisted candidates for the Product Manager role. Coordinate with hiring managers'\'' calendars, send calendar invites, and prepare interview guides for the panel."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → Experience Team → Interview Scheduling/Communication Agents → Scheduling Tools

## 7. Assessment Management

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Conduct technical assessments for 3 Senior Backend Engineer candidates. Include coding challenges, system design evaluation, and behavioral assessments. Generate comprehensive reports."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → Experience Team → Assessment Agent → Assessment Tools

## 8. Offer Generation and Negotiation

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Generate offer letters for 2 approved candidates for Data Scientist positions. Include salary details, benefits, start dates. Prepare for potential negotiations and ensure all terms are compliant with company policies."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → Closing Team → Offer Management/Compliance Agents → Offer/Legal Tools

## 9. Analytics and Reporting

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Generate comprehensive quarterly hiring report including metrics from all teams: sourcing effectiveness, interview success rates, offer acceptance rates, compliance status, and recommendations for next quarter."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → All Teams → Analytics Reporting Agent → Analytics/Reporting Tools

## 10. Process Optimization

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Analyze current hiring processes across all teams, identify bottlenecks, and recommend optimizations. Focus on reducing time-to-hire while improving candidate experience and compliance."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → All Teams (analysis mode) → Analytics Agent → Process/Analytics Tools

## 11. Multi-Role Coordination

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "We'\''re expanding our engineering team. Create job postings for 3 roles: Senior Python Developer, DevOps Engineer, and QA Lead. Start sourcing immediately and prepare interview pipelines for each role."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → Teams (parallel per role) → Multiple Agents → Multiple Tools

## 12. Candidate Journey Management

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Manage the complete candidate journey for John Smith who applied for the Senior Developer role. Check application status, schedule next interview, send preparation materials, and track all interactions."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → Experience Team → Communication/Interview Agents → Journey/Communication Tools

## 13. Compliance and Legal Check

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Perform compliance review for all offers made this month. Ensure EEOC compliance, verify background check completions, confirm all legal requirements are met, and generate compliance report."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → Closing Team → Compliance Agent → Legal/Compliance Tools

## 14. Team Performance Analysis

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Analyze performance of all recruitment teams for the past quarter. Compare sourcing efficiency, screening accuracy, interview conversion rates, and offer acceptance rates. Identify top performers and areas for improvement."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → All Teams → Analytics Agent → Performance/Analytics Tools

## 15. Candidate Pipeline Status

```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "Provide complete status update on all active candidates in our pipeline. Group by role, stage, and priority. Highlight any blocked candidates and suggest next actions for each."
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

**Expected Flow**: Master → All Teams (status check) → All Agents → Status/Tracking Tools

## Usage Notes

### Basic Query Format
```bash
curl -X POST http://localhost:5040/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "id": "msg_'$(date +%s)'",
        "timestamp": "'$(date -Iseconds)'",
        "role": "user",
        "content": "YOUR_QUERY_HERE"
      }
    },
    "id": "req_'$(date +%s)'"
  }'
```

### Using the Query Tracer (Recommended)
```bash
# Direct query with full tracing
python scripts/monitoring/advanced_query_tracer.py "YOUR_QUERY_HERE"

# Interactive mode for testing multiple queries
python scripts/monitoring/advanced_query_tracer.py --interactive

# Extended trace for complex queries
python scripts/monitoring/advanced_query_tracer.py --trace-duration 60 "Complex multi-team query"
```

### Expected Response Structure
- Master acknowledges query
- Delegates to appropriate team coordinator(s)
- Teams activate relevant individual agents
- Agents call MCP tools as needed
- Results flow back up through the hierarchy
- Master provides consolidated response

### Tips for Effective Queries
1. **Be Specific**: Include details like role titles, requirements, timelines
2. **State Priority**: Mention if urgent or has special requirements
3. **Include Context**: Provide background for better decision making
4. **Request Metrics**: Ask for tracking/metrics if needed
5. **Specify Output**: Mention if you need reports, summaries, or actions