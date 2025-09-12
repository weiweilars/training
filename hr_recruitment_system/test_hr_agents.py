#!/usr/bin/env python3
"""
HR Recruitment Agents Test Suite
Comprehensive testing of all HR recruitment agents and their MCP tools
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any
import sys

class HRAgentsTestSuite:
    """Test suite for HR recruitment agents"""
    
    def __init__(self):
        self.base_url = "http://localhost"
        self.agents = {
            "job_requisition": {
                "name": "Job Requisition Agent", 
                "port": 5020,
                "test_scenarios": [
                    {
                        "name": "Create Software Engineer Job Posting", 
                        "message": "Create a job posting for a Senior Software Engineer position requiring 5+ years Python experience, cloud platform knowledge (AWS/Azure), and microservices architecture experience. Location: San Francisco, CA. Salary range: $140k-$180k."
                    },
                    {
                        "name": "Create Marketing Manager Role",
                        "message": "I need to create a job requisition for a Marketing Manager role. Requirements: 3+ years digital marketing, SEO/SEM expertise, content strategy experience. Remote position with 10% travel required."
                    },
                    {
                        "name": "Update Job Requirements",
                        "message": "Update the job requirements for REQ-2024-001 to include Kubernetes experience and increase the salary range to $150k-$190k."
                    }
                ]
            },
            "sourcing": {
                "name": "Sourcing Agent",
                "port": 5021, 
                "test_scenarios": [
                    {
                        "name": "Source Python Developers",
                        "message": "Find Python developers with 3+ years experience in San Francisco Bay Area. Focus on candidates with Django, FastAPI, and cloud experience."
                    },
                    {
                        "name": "Build Talent Pool",
                        "message": "Build a talent pool for DevOps engineers. Search LinkedIn and GitHub for professionals with Kubernetes, Docker, and CI/CD experience."
                    },
                    {
                        "name": "Passive Candidate Outreach",
                        "message": "Identify passive candidates for our Data Science team. Look for professionals with ML/AI background currently working at tech companies."
                    }
                ]
            },
            "resume_screening": {
                "name": "Resume Screening Agent",
                "port": 5022,
                "test_scenarios": [
                    {
                        "name": "Screen Python Developer Resume",
                        "message": "Screen this candidate resume for the Senior Python Developer role (REQ-2024-001). Resume: John Smith - 5 years Python, Django, FastAPI, AWS, PostgreSQL. Previous roles at startups building scalable web applications."
                    },
                    {
                        "name": "Batch Resume Analysis", 
                        "message": "Analyze 15 resumes for the Marketing Manager position. Rank candidates based on digital marketing experience, leadership skills, and campaign management expertise."
                    },
                    {
                        "name": "Skills Gap Analysis",
                        "message": "Compare candidate skills against job requirements for REQ-2024-003 (DevOps Engineer). Identify which candidates need additional training or certifications."
                    }
                ]
            },
            "communication": {
                "name": "Communication Agent",
                "port": 5027,
                "test_scenarios": [
                    {
                        "name": "Send Interview Invitation",
                        "message": "Send an interview invitation email to John Smith (john.smith@email.com) for the Senior Python Developer position. Schedule for next Tuesday at 2 PM PST."
                    },
                    {
                        "name": "Rejection Email with Feedback",
                        "message": "Send a professional rejection email to candidate Sarah Johnson. Provide constructive feedback that while her frontend skills are excellent, we need more backend Python experience for this role."
                    },
                    {
                        "name": "Follow-up Campaign",
                        "message": "Create an automated follow-up sequence for candidates who haven't responded to our initial outreach within 7 days."
                    }
                ]
            },
            "interview_scheduling": {
                "name": "Interview Scheduling Agent",
                "port": 5024,
                "test_scenarios": [
                    {
                        "name": "Schedule Technical Interview",
                        "message": "Schedule a technical interview for John Smith with our engineering team. Need 2-hour slot next week, including 1-hour coding session and 1-hour system design discussion."
                    },
                    {
                        "name": "Multi-Round Interview Setup", 
                        "message": "Set up a full interview loop for Marketing Manager candidate: 30-min phone screen, 1-hour behavioral interview, 45-min case study presentation, and 30-min culture fit discussion."
                    },
                    {
                        "name": "Handle Reschedule Request",
                        "message": "Candidate requested to reschedule their Friday 3 PM interview. Find alternative slots for next week and coordinate with the 3 interviewers."
                    }
                ]
            },
            "assessment": {
                "name": "Assessment Agent",
                "port": 5023,
                "test_scenarios": [
                    {
                        "name": "Create Technical Assessment",
                        "message": "Create a technical assessment for Senior Python Developer role. Include coding challenges for API development, database queries, and system design questions."
                    },
                    {
                        "name": "Behavioral Assessment Setup",
                        "message": "Design a behavioral assessment for leadership roles. Focus on conflict resolution, team management, and strategic thinking scenarios."
                    },
                    {
                        "name": "Score Assessment Results",
                        "message": "Score the technical assessment for candidate ID #12345. They completed the Python API challenge in 45 minutes with working code but missed some edge cases."
                    }
                ]
            },
            "background_verification": {
                "name": "Background Verification Agent", 
                "port": 5025,
                "test_scenarios": [
                    {
                        "name": "Initiate Background Check",
                        "message": "Initiate background verification for John Smith (SSN: XXX-XX-1234). Include employment history, education verification, and criminal background check."
                    },
                    {
                        "name": "Reference Check Coordination",
                        "message": "Contact references for Sarah Johnson: former manager at TechCorp (Mike Brown), colleague at StartupXYZ (Lisa Chen), and professor from Stanford (Dr. Smith)."
                    },
                    {
                        "name": "Education Credential Verification",
                        "message": "Verify candidate's MS in Computer Science from UC Berkeley (2018) and BS in Engineering from UCLA (2016)."
                    }
                ]
            },
            "offer_management": {
                "name": "Offer Management Agent",
                "port": 5026,
                "test_scenarios": [
                    {
                        "name": "Generate Job Offer",
                        "message": "Generate offer letter for John Smith: Senior Python Developer, $165,000 salary, $20k signing bonus, equity package, standard benefits. Start date: March 15, 2024."
                    },
                    {
                        "name": "Handle Counter-Offer",
                        "message": "Candidate countered our $165k offer with $180k salary request. Analyze market data and provide recommendation for counter-proposal."
                    },
                    {
                        "name": "Prepare Onboarding Package",
                        "message": "Prepare onboarding documentation for new hire Sarah Johnson: equipment requests, first-day schedule, paperwork checklist, and buddy assignment."
                    }
                ]
            },
            "compliance": {
                "name": "Compliance Agent",
                "port": 5028,
                "test_scenarios": [
                    {
                        "name": "EEOC Compliance Check",
                        "message": "Review our hiring process for the last quarter for EEOC compliance. Check for any potential bias in job descriptions, interview questions, or selection criteria."
                    },
                    {
                        "name": "Data Privacy Audit",
                        "message": "Conduct GDPR compliance audit of our candidate data handling. Review data retention policies, consent mechanisms, and data processing procedures."
                    },
                    {
                        "name": "Interview Question Validation",
                        "message": "Validate these interview questions for legal compliance: 'What is your age?', 'Are you planning to have children?', 'What is your experience with Python programming?'"
                    }
                ]
            },
            "analytics_reporting": {
                "name": "Analytics & Reporting Agent",
                "port": 5029,
                "test_scenarios": [
                    {
                        "name": "Generate Recruitment Metrics",
                        "message": "Generate recruitment metrics report for Q4 2023. Include time-to-hire, cost-per-hire, source effectiveness, and offer acceptance rates."
                    },
                    {
                        "name": "Pipeline Analysis",
                        "message": "Analyze our current hiring pipeline. How many candidates are at each stage? What are the conversion rates between stages?"
                    },
                    {
                        "name": "Diversity Metrics",
                        "message": "Provide diversity analytics for our tech roles hired in the last 6 months. Break down by gender, ethnicity, and educational background."
                    }
                ]
            },
            "team_coordinator": {
                "name": "Team Coordinator Agent",
                "port": 5030,
                "test_scenarios": [
                    {
                        "name": "Coordinate Hiring Process",
                        "message": "Coordinate the full hiring process for a new Senior Software Engineer. We have 15 candidates in the pipeline."
                    },
                    {
                        "name": "Multi-Agent Task Distribution",
                        "message": "Distribute tasks to other agents: sourcing needs to find 10 more candidates, screening needs to review 5 resumes, and scheduling needs to book 3 interviews for tomorrow."
                    },
                    {
                        "name": "Status Report Generation",
                        "message": "Generate a comprehensive status report for all active job requisitions. Include candidate pipeline status and next steps for each role."
                    }
                ]
            }
        }
        
        self.test_results = []
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def test_agent_card(self, agent_name: str, port: int) -> Dict[str, Any]:
        """Test agent card discovery endpoint"""
        try:
            url = f"{self.base_url}:{port}/.well-known/agent-card.json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "name": data.get("name", "Unknown"),
                        "skills_count": len(data.get("skills", [])),
                        "capabilities": data.get("capabilities", {}),
                        "metadata": data.get("metadata", {})
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_agent_message(self, agent_name: str, port: int, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test sending a message to an agent"""
        try:
            url = f"{self.base_url}:{port}/"
            session_id = f"test-{agent_name}-{int(time.time())}"
            
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": scenario["message"],
                    "sessionId": session_id
                },
                "id": str(uuid.uuid4())
            }
            
            start_time = time.time()
            async with self.session.post(url, json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    result = data.get("result", {})
                    
                    if result.get("status") == "completed":
                        response_content = result.get("result", {}).get("message", {}).get("content", "")
                        return {
                            "success": True,
                            "scenario": scenario["name"],
                            "response_time": round(response_time, 2),
                            "response_length": len(response_content),
                            "response_preview": response_content[:200] + "..." if len(response_content) > 200 else response_content,
                            "task_id": result.get("taskId"),
                            "session_id": session_id
                        }
                    else:
                        return {
                            "success": False,
                            "scenario": scenario["name"],
                            "error": f"Task status: {result.get('status')}",
                            "response_time": round(response_time, 2)
                        }
                else:
                    return {
                        "success": False,
                        "scenario": scenario["name"], 
                        "error": f"HTTP {response.status}",
                        "response_time": round(response_time, 2)
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "scenario": scenario["name"],
                "error": str(e),
                "response_time": 0
            }

    async def test_single_agent(self, agent_name: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single agent comprehensively"""
        print(f"\n🧪 Testing {agent_config['name']} (Port {agent_config['port']})")
        print("=" * 60)
        
        agent_results = {
            "agent_name": agent_name,
            "port": agent_config["port"],
            "card_test": None,
            "scenario_tests": [],
            "summary": {
                "total_scenarios": len(agent_config["test_scenarios"]),
                "successful_scenarios": 0,
                "failed_scenarios": 0,
                "avg_response_time": 0,
                "card_available": False
            }
        }
        
        # Test agent card
        print("📋 Testing agent card discovery...")
        card_result = await self.test_agent_card(agent_name, agent_config["port"])
        agent_results["card_test"] = card_result
        
        if card_result["success"]:
            print(f"   ✅ Agent card available: {card_result['name']}")
            print(f"   📊 Skills available: {card_result['skills_count']}")
            agent_results["summary"]["card_available"] = True
        else:
            print(f"   ❌ Agent card failed: {card_result['error']}")
        
        # Test scenarios
        print(f"\n💬 Testing {len(agent_config['test_scenarios'])} scenarios...")
        total_response_time = 0
        
        for i, scenario in enumerate(agent_config["test_scenarios"], 1):
            print(f"   {i}. {scenario['name']}")
            
            scenario_result = await self.test_agent_message(agent_name, agent_config["port"], scenario)
            agent_results["scenario_tests"].append(scenario_result)
            
            if scenario_result["success"]:
                print(f"      ✅ Success ({scenario_result['response_time']}s)")
                print(f"      💭 Preview: {scenario_result['response_preview']}")
                agent_results["summary"]["successful_scenarios"] += 1
                total_response_time += scenario_result['response_time']
            else:
                print(f"      ❌ Failed: {scenario_result['error']}")
                agent_results["summary"]["failed_scenarios"] += 1
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Calculate summary
        if agent_results["summary"]["successful_scenarios"] > 0:
            agent_results["summary"]["avg_response_time"] = round(
                total_response_time / agent_results["summary"]["successful_scenarios"], 2
            )
        
        print(f"\n📈 {agent_config['name']} Summary:")
        print(f"   ✅ Successful: {agent_results['summary']['successful_scenarios']}")
        print(f"   ❌ Failed: {agent_results['summary']['failed_scenarios']}")
        print(f"   ⏱️  Avg Response Time: {agent_results['summary']['avg_response_time']}s")
        
        return agent_results

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests for all agents"""
        print("🚀 HR Recruitment Agents Test Suite")
        print("=" * 60)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 Testing {len(self.agents)} agents")
        
        overall_results = {
            "test_run_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "agents_tested": len(self.agents),
            "agents_results": [],
            "overall_summary": {
                "total_agents": len(self.agents),
                "agents_available": 0,
                "total_scenarios": 0,
                "successful_scenarios": 0,
                "failed_scenarios": 0,
                "avg_response_time": 0
            }
        }
        
        total_response_time = 0
        total_successful = 0
        
        for agent_name, agent_config in self.agents.items():
            try:
                agent_result = await self.test_single_agent(agent_name, agent_config)
                overall_results["agents_results"].append(agent_result)
                
                # Update overall summary
                if agent_result["summary"]["card_available"]:
                    overall_results["overall_summary"]["agents_available"] += 1
                
                overall_results["overall_summary"]["total_scenarios"] += agent_result["summary"]["total_scenarios"]
                overall_results["overall_summary"]["successful_scenarios"] += agent_result["summary"]["successful_scenarios"] 
                overall_results["overall_summary"]["failed_scenarios"] += agent_result["summary"]["failed_scenarios"]
                
                if agent_result["summary"]["successful_scenarios"] > 0:
                    total_response_time += (agent_result["summary"]["avg_response_time"] * agent_result["summary"]["successful_scenarios"])
                    total_successful += agent_result["summary"]["successful_scenarios"]
                    
            except Exception as e:
                print(f"❌ Error testing {agent_name}: {e}")
                overall_results["agents_results"].append({
                    "agent_name": agent_name,
                    "error": str(e),
                    "summary": {"total_scenarios": 0, "successful_scenarios": 0, "failed_scenarios": 0}
                })
        
        # Calculate overall average response time
        if total_successful > 0:
            overall_results["overall_summary"]["avg_response_time"] = round(total_response_time / total_successful, 2)
        
        return overall_results

    def print_final_report(self, results: Dict[str, Any]):
        """Print comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 FINAL TEST REPORT")
        print("=" * 80)
        
        summary = results["overall_summary"]
        print(f"🤖 Agents Tested: {summary['total_agents']}")
        print(f"✅ Agents Available: {summary['agents_available']}")
        print(f"💬 Total Scenarios: {summary['total_scenarios']}")
        print(f"✅ Successful Tests: {summary['successful_scenarios']}")
        print(f"❌ Failed Tests: {summary['failed_scenarios']}")
        print(f"⏱️  Average Response Time: {summary['avg_response_time']}s")
        
        success_rate = (summary['successful_scenarios'] / summary['total_scenarios'] * 100) if summary['total_scenarios'] > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🏆 Top Performing Agents:")
        sorted_agents = sorted(
            [r for r in results["agents_results"] if not r.get("error")],
            key=lambda x: x["summary"]["successful_scenarios"],
            reverse=True
        )[:3]
        
        for i, agent in enumerate(sorted_agents, 1):
            print(f"   {i}. {agent['agent_name']}: {agent['summary']['successful_scenarios']}/{agent['summary']['total_scenarios']} scenarios")
        
        print(f"\n📋 Detailed Results:")
        for agent_result in results["agents_results"]:
            if agent_result.get("error"):
                print(f"   ❌ {agent_result['agent_name']}: {agent_result['error']}")
            else:
                s = agent_result["summary"]
                print(f"   📊 {agent_result['agent_name']}: {s['successful_scenarios']}/{s['total_scenarios']} ({s['avg_response_time']}s avg)")

    async def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hr_agents_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

async def main():
    """Main test execution"""
    try:
        async with HRAgentsTestSuite() as test_suite:
            results = await test_suite.run_all_tests()
            test_suite.print_final_report(results)
            await test_suite.save_results(results)
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test suite error: {e}")

if __name__ == "__main__":
    print("HR Recruitment Agents Test Suite")
    print("Ensure all agents and MCP tools are running before starting tests...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)