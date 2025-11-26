"""Test suite management for SIRA evaluation framework.

Loads and manages test questions across multiple domains for baseline
comparison and learning trajectory analysis.
"""
import json
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TestQuestion:
    """Single test question."""
    id: str
    question: str
    expected_answer: str
    difficulty: str
    category: str
    domain: str


class TestSuite:
    """Manages test questions across multiple domains."""
    
    def __init__(self, test_suites_path: str = "./tests/evaluation/test_suites"):
        """Initialize test suite manager.
        
        Args:
            test_suites_path: Path to test suites directory
        """
        self.test_suites_path = Path(test_suites_path)
        self.questions: List[TestQuestion] = []
        self.domains: Dict[str, List[TestQuestion]] = {}
        logger.info("test_suite_initialized", path=test_suites_path)
    
    def load_all_suites(self) -> int:
        """Load all test suites from directory.
        
        Returns:
            Total number of questions loaded
        """
        self.questions = []
        self.domains = {}
        
        # Load all JSON files from test_suites directory
        suite_files = list(self.test_suites_path.glob("*.json"))
        
        for suite_file in suite_files:
            try:
                with open(suite_file, 'r', encoding='utf-8') as f:
                    suite_data = json.load(f)
                
                domain = suite_data.get("domain", "unknown")
                questions_data = suite_data.get("questions", [])
                
                domain_questions = []
                for q in questions_data:
                    # Skip placeholder questions
                    if "NOTE:" in q.get("question", "") or "Placeholder" in q.get("expected_answer", ""):
                        continue
                    
                    question = TestQuestion(
                        id=q["id"],
                        question=q["question"],
                        expected_answer=q["expected_answer"],
                        difficulty=q.get("difficulty", "medium"),
                        category=q.get("category", "general"),
                        domain=domain
                    )
                    domain_questions.append(question)
                    self.questions.append(question)
                
                self.domains[domain] = domain_questions
                logger.info(
                    "loaded_test_suite",
                    domain=domain,
                    question_count=len(domain_questions),
                    file=suite_file.name
                )
                
            except Exception as e:
                logger.error(
                    "failed_to_load_suite",
                    file=suite_file.name,
                    error=str(e)
                )
        
        total_count = len(self.questions)
        logger.info(
            "all_suites_loaded",
            total_questions=total_count,
            domains=list(self.domains.keys())
        )
        
        return total_count
    
    def get_by_domain(self, domain: str) -> List[TestQuestion]:
        """Get all questions for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of questions for that domain
        """
        return self.domains.get(domain, [])
    
    def get_by_difficulty(self, difficulty: str) -> List[TestQuestion]:
        """Get all questions of a specific difficulty.
        
        Args:
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            List of questions with that difficulty
        """
        return [q for q in self.questions if q.difficulty == difficulty]
    
    def get_sample(self, count: int, domain: Optional[str] = None) -> List[TestQuestion]:
        """Get a random sample of questions.
        
        Args:
            count: Number of questions to sample
            domain: Optional domain to sample from
            
        Returns:
            List of sampled questions
        """
        import random
        
        if domain:
            source = self.domains.get(domain, [])
        else:
            source = self.questions
        
        if len(source) <= count:
            return source
        
        return random.sample(source, count)
    
    def get_all_questions(self) -> List[TestQuestion]:
        """Get all loaded questions.
        
        Returns:
            List of all questions
        """
        return self.questions
    
    def get_summary(self) -> Dict[str, any]:
        """Get summary statistics of loaded test suites.
        
        Returns:
            Dictionary with statistics
        """
        difficulty_counts = {}
        for q in self.questions:
            difficulty_counts[q.difficulty] = difficulty_counts.get(q.difficulty, 0) + 1
        
        return {
            "total_questions": len(self.questions),
            "total_domains": len(self.domains),
            "domains": {domain: len(questions) for domain, questions in self.domains.items()},
            "difficulty_distribution": difficulty_counts
        }
