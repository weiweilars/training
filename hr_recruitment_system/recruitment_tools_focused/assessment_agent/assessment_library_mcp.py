#!/usr/bin/env python3
"""
Assessment Agent - Assessment Library MCP Server
Focused on test templates, question banks, and assessment content management
Port: 8102
"""

try:
    from fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    class FastMCP:
        def __init__(self, name):
            self.name = name
        def tool(self):
            def decorator(func):
                return func
            return decorator
        def run(self, **kwargs):
            print("FastMCP fallback - demo mode")

import json
import uuid
from datetime import datetime
import random

mcp = FastMCP(name="assessment-library")

# Assessment templates and question banks
assessment_templates_db = {
    "python_developer": {
        "id": "python_developer",
        "name": "Python Developer Assessment",
        "description": "Comprehensive Python development skills assessment",
        "duration_minutes": 90,
        "difficulty_levels": ["junior", "mid", "senior"],
        "question_categories": [
            {"category": "syntax_basics", "weight": 0.2, "question_count": 5},
            {"category": "data_structures", "weight": 0.3, "question_count": 4},
            {"category": "algorithms", "weight": 0.3, "question_count": 3},
            {"category": "frameworks", "weight": 0.2, "question_count": 3}
        ],
        "passing_score": 70
    },
    "frontend_developer": {
        "id": "frontend_developer", 
        "name": "Frontend Developer Assessment",
        "description": "JavaScript, HTML, CSS, and React skills assessment",
        "duration_minutes": 75,
        "difficulty_levels": ["junior", "mid", "senior"],
        "question_categories": [
            {"category": "javascript_fundamentals", "weight": 0.35, "question_count": 6},
            {"category": "html_css", "weight": 0.25, "question_count": 4},
            {"category": "react_framework", "weight": 0.25, "question_count": 4},
            {"category": "performance_optimization", "weight": 0.15, "question_count": 2}
        ],
        "passing_score": 75
    }
}

question_banks_db = {
    "python_syntax_basics": [
        {
            "id": "py_001",
            "question": "What is the output of: print([1, 2, 3][1:])",
            "type": "multiple_choice",
            "options": ["[1, 2, 3]", "[2, 3]", "[1, 2]", "Error"],
            "correct_answer": "[2, 3]",
            "difficulty": "junior",
            "explanation": "List slicing [1:] returns elements from index 1 to end"
        },
        {
            "id": "py_002",
            "question": "Implement a function that returns the factorial of a number",
            "type": "coding",
            "difficulty": "mid",
            "test_cases": [
                {"input": 5, "expected": 120},
                {"input": 0, "expected": 1},
                {"input": 1, "expected": 1}
            ],
            "time_limit_minutes": 10
        }
    ],
    "javascript_fundamentals": [
        {
            "id": "js_001",
            "question": "What is the difference between '==' and '===' in JavaScript?",
            "type": "short_answer",
            "difficulty": "junior",
            "sample_answer": "== compares values with type coercion, === compares values and types without coercion"
        }
    ]
}

custom_assessments_db = {}

@mcp.tool()
def create_custom_assessment_template(
    template_name: str,
    description: str,
    skills_focus: str,
    duration_minutes: int = 60,
    difficulty_level: str = "mid",
    question_categories: str = "{}",
    passing_score: int = 70
) -> str:
    """
    Create a custom assessment template
    
    Args:
        template_name: Name for the assessment template
        description: Description of what the assessment covers
        skills_focus: Comma-separated list of skills being tested
        duration_minutes: Total time allowed for assessment
        difficulty_level: Overall difficulty (junior, mid, senior)
        question_categories: JSON with category definitions
        passing_score: Minimum score to pass (0-100)
    """
    
    template_id = str(uuid.uuid4())[:8]
    skills_list = [skill.strip() for skill in skills_focus.split(",")]
    
    try:
        categories = json.loads(question_categories) if question_categories != "{}" else {}
    except json.JSONDecodeError:
        # Default categories based on skills
        categories = []
        weight_per_skill = 1.0 / len(skills_list)
        for skill in skills_list:
            categories.append({
                "category": skill.lower().replace(" ", "_"),
                "weight": weight_per_skill,
                "question_count": 3
            })
    
    template = {
        "id": template_id,
        "name": template_name,
        "description": description,
        "skills_focus": skills_list,
        "duration_minutes": duration_minutes,
        "difficulty_levels": [difficulty_level],
        "question_categories": categories,
        "passing_score": passing_score,
        "created_at": datetime.now().isoformat(),
        "created_by": "custom",
        "status": "active",
        "usage_count": 0
    }
    
    assessment_templates_db[template_id] = template
    
    return json.dumps({
        "success": True,
        "template_id": template_id,
        "message": f"Custom assessment template '{template_name}' created",
        "template": template
    }, indent=2)

@mcp.tool()
def add_questions_to_bank(
    category: str,
    questions_data: str
) -> str:
    """
    Add questions to a specific question bank category
    
    Args:
        category: Question category (e.g., "python_syntax_basics")
        questions_data: JSON array of question objects
    """
    
    try:
        questions = json.loads(questions_data)
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON in questions_data"})
    
    if category not in question_banks_db:
        question_banks_db[category] = []
    
    added_questions = []
    
    for question_data in questions:
        question_id = str(uuid.uuid4())[:8]
        
        question = {
            "id": question_id,
            "question": question_data.get("question", ""),
            "type": question_data.get("type", "multiple_choice"),
            "difficulty": question_data.get("difficulty", "mid"),
            "created_at": datetime.now().isoformat(),
            **question_data  # Include all other fields
        }
        
        question_banks_db[category].append(question)
        added_questions.append(question)
    
    return json.dumps({
        "success": True,
        "category": category,
        "questions_added": len(added_questions),
        "total_in_category": len(question_banks_db[category]),
        "added_questions": added_questions
    }, indent=2)

@mcp.tool()
def generate_assessment_from_template(
    template_id: str,
    difficulty_level: str = "",
    custom_duration: int = 0,
    exclude_categories: str = ""
) -> str:
    """
    Generate a specific assessment instance from a template
    
    Args:
        template_id: ID of template to use
        difficulty_level: Override difficulty (junior, mid, senior)
        custom_duration: Override duration in minutes (0 = use template default)
        exclude_categories: Comma-separated categories to exclude
    """
    
    if template_id not in assessment_templates_db:
        available = list(assessment_templates_db.keys())
        return json.dumps({
            "success": False,
            "error": f"Template not found. Available: {available}"
        })
    
    template = assessment_templates_db[template_id]
    excluded = [cat.strip() for cat in exclude_categories.split(",") if cat.strip()]
    
    assessment_id = str(uuid.uuid4())[:8]
    
    # Filter categories
    active_categories = [cat for cat in template["question_categories"] 
                        if cat["category"] not in excluded]
    
    # Generate questions for each category
    assessment_questions = []
    total_questions = 0
    
    for category_info in active_categories:
        category = category_info["category"]
        question_count = category_info["question_count"]
        
        # Get questions from bank
        available_questions = question_banks_db.get(category, [])
        
        # Filter by difficulty if specified
        if difficulty_level:
            available_questions = [q for q in available_questions 
                                 if q.get("difficulty", "mid") == difficulty_level]
        
        # Select questions (random selection for variety)
        selected_questions = random.sample(
            available_questions, 
            min(question_count, len(available_questions))
        )
        
        for question in selected_questions:
            assessment_questions.append({
                **question,
                "category": category,
                "points": 10,  # Standard points per question
                "time_allocation": category_info.get("time_allocation", 5)
            })
        
        total_questions += len(selected_questions)
    
    assessment_instance = {
        "assessment_id": assessment_id,
        "template_id": template_id,
        "template_name": template["name"],
        "difficulty_level": difficulty_level or template["difficulty_levels"][0],
        "duration_minutes": custom_duration or template["duration_minutes"],
        "total_questions": total_questions,
        "total_points": total_questions * 10,
        "passing_score": template["passing_score"],
        "questions": assessment_questions,
        "categories_included": [cat["category"] for cat in active_categories],
        "generated_at": datetime.now().isoformat(),
        "status": "ready",
        "instructions": generate_assessment_instructions(template, difficulty_level)
    }
    
    custom_assessments_db[assessment_id] = assessment_instance
    
    # Update template usage
    template["usage_count"] += 1
    
    return json.dumps({
        "success": True,
        "assessment_id": assessment_id,
        "message": f"Assessment generated from template '{template['name']}'",
        "assessment_summary": {
            "total_questions": total_questions,
            "duration_minutes": assessment_instance["duration_minutes"],
            "categories": len(active_categories),
            "difficulty": assessment_instance["difficulty_level"]
        }
    }, indent=2)

def generate_assessment_instructions(template: dict, difficulty_level: str) -> list:
    """Generate instructions for the assessment"""
    instructions = [
        f"This assessment covers {', '.join(template.get('skills_focus', ['various skills']))}",
        f"You have {template['duration_minutes']} minutes to complete all questions",
        f"Minimum passing score: {template['passing_score']}%",
        "Read each question carefully before answering",
        "You can navigate between questions, but submit before time expires"
    ]
    
    if difficulty_level == "senior":
        instructions.append("This is a senior-level assessment with advanced concepts")
    elif difficulty_level == "junior":
        instructions.append("This assessment focuses on fundamental concepts")
    
    return instructions

@mcp.tool()
def search_question_bank(
    search_query: str = "",
    category: str = "",
    difficulty: str = "",
    question_type: str = "",
    limit: int = 20
) -> str:
    """
    Search questions in the question banks
    
    Args:
        search_query: Text to search in question content
        category: Filter by category
        difficulty: Filter by difficulty (junior, mid, senior)
        question_type: Filter by type (multiple_choice, coding, short_answer)
        limit: Maximum results to return
    """
    
    results = []
    search_lower = search_query.lower()
    
    for bank_category, questions in question_banks_db.items():
        # Category filter
        if category and category != bank_category:
            continue
            
        for question in questions:
            # Apply filters
            if difficulty and question.get("difficulty") != difficulty:
                continue
            if question_type and question.get("type") != question_type:
                continue
            if search_query and search_lower not in question.get("question", "").lower():
                continue
            
            result = {
                **question,
                "category": bank_category,
                "relevance_score": calculate_relevance_score(question, search_query)
            }
            results.append(result)
    
    # Sort by relevance
    results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return json.dumps({
        "success": True,
        "search_criteria": {
            "query": search_query,
            "category": category,
            "difficulty": difficulty,
            "type": question_type
        },
        "total_found": len(results),
        "questions": results[:limit]
    }, indent=2)

def calculate_relevance_score(question: dict, search_query: str) -> int:
    """Calculate relevance score for search results"""
    if not search_query:
        return 50
    
    score = 0
    search_terms = search_query.lower().split()
    question_text = question.get("question", "").lower()
    
    for term in search_terms:
        if term in question_text:
            score += 20
    
    # Boost score for exact matches
    if search_query.lower() in question_text:
        score += 30
    
    return score

@mcp.tool()
def get_assessment_template_details(template_id: str) -> str:
    """
    Get detailed information about an assessment template
    
    Args:
        template_id: ID of template to retrieve
    """
    
    if template_id not in assessment_templates_db:
        available = list(assessment_templates_db.keys())
        return json.dumps({
            "success": False,
            "error": f"Template not found. Available: {available}"
        })
    
    template = assessment_templates_db[template_id]
    
    # Get sample questions for preview
    sample_questions = []
    for category_info in template["question_categories"]:
        category = category_info["category"]
        available_questions = question_banks_db.get(category, [])
        if available_questions:
            sample_questions.append({
                "category": category,
                "sample_question": available_questions[0]["question"],
                "question_type": available_questions[0]["type"],
                "total_questions_available": len(available_questions)
            })
    
    template_details = {
        **template,
        "sample_questions": sample_questions,
        "total_question_pool": sum(len(question_banks_db.get(cat["category"], [])) 
                                  for cat in template["question_categories"]),
        "estimated_completion_time": f"{template['duration_minutes']}-{template['duration_minutes'] + 15} minutes",
        "prerequisites": get_template_prerequisites(template)
    }
    
    return json.dumps({
        "success": True,
        "template_details": template_details
    }, indent=2)

def get_template_prerequisites(template: dict) -> list:
    """Get prerequisites for taking this assessment"""
    prerequisites = []
    
    for skill in template.get("skills_focus", []):
        if "python" in skill.lower():
            prerequisites.append("Basic Python programming knowledge")
        elif "javascript" in skill.lower():
            prerequisites.append("Understanding of JavaScript fundamentals")
        elif "react" in skill.lower():
            prerequisites.append("Experience with React framework")
    
    if not prerequisites:
        prerequisites.append("Relevant experience in the assessed skills")
    
    return prerequisites

@mcp.tool()
def clone_assessment_template(
    template_id: str,
    new_name: str,
    modifications: str = "{}"
) -> str:
    """
    Clone an existing template with optional modifications
    
    Args:
        template_id: ID of template to clone
        new_name: Name for the new template
        modifications: JSON with field modifications
    """
    
    if template_id not in assessment_templates_db:
        return json.dumps({"success": False, "error": "Template not found"})
    
    try:
        mods = json.loads(modifications) if modifications != "{}" else {}
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON in modifications"})
    
    original_template = assessment_templates_db[template_id]
    new_template_id = str(uuid.uuid4())[:8]
    
    # Clone template
    cloned_template = {
        **original_template,
        "id": new_template_id,
        "name": new_name,
        "created_at": datetime.now().isoformat(),
        "created_by": "cloned",
        "cloned_from": template_id,
        "usage_count": 0
    }
    
    # Apply modifications
    for field, value in mods.items():
        if field in cloned_template and field not in ["id", "created_at", "cloned_from"]:
            cloned_template[field] = value
    
    assessment_templates_db[new_template_id] = cloned_template
    
    return json.dumps({
        "success": True,
        "new_template_id": new_template_id,
        "message": f"Template cloned as '{new_name}'",
        "modifications_applied": len(mods),
        "cloned_template": cloned_template
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8102)