#!/usr/bin/env python3
"""
AI Agent Analysis Example

This script demonstrates how an AI agent would use V5 queries and summaries
to analyze system failures and propose improvements.
"""

import asyncio
from typing import List, Dict, Any
from collections import defaultdict
from dataclasses import dataclass
import json

# Example of how an AI agent would analyze conversations


@dataclass
class FailurePattern:
    """Represents a pattern of failures identified across conversations"""
    pattern_type: str  # comprehension, knowledge, reasoning, execution
    root_cause: str
    frequency: int
    severity: str  # minor, moderate, critical
    affected_domains: List[str]
    example_conversations: List[str]
    proposed_solution: str
    expected_impact: float


@dataclass 
class ImprovementHypothesis:
    """Represents a hypothesis for system improvement"""
    title: str
    description: str
    failure_patterns_addressed: List[str]
    implementation_approach: str
    estimated_effort: str  # low, medium, high
    expected_roi: float
    priority: int


class AIAnalysisAgent:
    """Agent that analyzes conversations to identify improvement opportunities"""
    
    def __init__(self, retrieval_client):
        self.retrieval_client = retrieval_client
        self.failure_patterns = defaultdict(lambda: FailurePattern(
            pattern_type="", root_cause="", frequency=0, severity="",
            affected_domains=[], example_conversations=[], 
            proposed_solution="", expected_impact=0.0
        ))
        
    async def analyze_system_performance(self) -> List[ImprovementHypothesis]:
        """Main analysis workflow"""
        
        # Step 1: Retrieve different types of failures
        failure_queries = [
            # Comprehension failures
            "AI failed to understand technical request multiple clarifications needed",
            "misunderstanding about user intent leading to wrong solution provided",
            
            # Knowledge gaps
            "conversation revealing need for domain-specific knowledge not available",
            "AI lacking depth in technical topic user frustrated",
            
            # Tool limitations
            "system limitation preventing user goal achievement workaround required",
            "user requesting feature not currently supported abandoned task",
            
            # Recovery patterns
            "AI successfully recovered from initial misunderstanding by asking clarifying questions",
            "user satisfaction improved after AI adjusted approach",
        ]
        
        all_conversations = []
        for query in failure_queries:
            results = await self.retrieval_client.search(query, top_k=20)
            all_conversations.extend(results)
            
        # Step 2: Analyze patterns across conversations
        patterns = self._extract_failure_patterns(all_conversations)
        
        # Step 3: Group similar failures
        grouped_patterns = self._group_similar_patterns(patterns)
        
        # Step 4: Generate improvement hypotheses
        hypotheses = []
        for pattern_group in grouped_patterns:
            hypothesis = self._generate_hypothesis(pattern_group)
            hypotheses.append(hypothesis)
            
        # Step 5: Prioritize by ROI
        return sorted(hypotheses, key=lambda h: h.expected_roi, reverse=True)
    
    def _extract_failure_patterns(self, conversations: List[Dict[str, Any]]) -> List[FailurePattern]:
        """Extract failure patterns from conversation summaries"""
        patterns = []
        
        for conv in conversations:
            summary = conv.get("summary", "")
            
            # Parse V5 summary structure to extract failure information
            # In a real implementation, this would use structured parsing
            if "FAILURE ANALYSIS" in summary:
                pattern = FailurePattern(
                    pattern_type=self._extract_pattern_type(summary),
                    root_cause=self._extract_root_cause(summary),
                    frequency=1,  # Will be aggregated later
                    severity=self._extract_severity(summary),
                    affected_domains=[self._extract_domain(summary)],
                    example_conversations=[conv.get("hash", "")],
                    proposed_solution=self._extract_improvement(summary),
                    expected_impact=self._calculate_impact(summary)
                )
                patterns.append(pattern)
                
        return patterns
    
    def _group_similar_patterns(self, patterns: List[FailurePattern]) -> List[List[FailurePattern]]:
        """Group similar failure patterns together"""
        # Group by root cause similarity
        groups = defaultdict(list)
        
        for pattern in patterns:
            # Simple grouping by pattern type and domain
            key = f"{pattern.pattern_type}:{pattern.affected_domains[0]}"
            groups[key].append(pattern)
            
        return list(groups.values())
    
    def _generate_hypothesis(self, pattern_group: List[FailurePattern]) -> ImprovementHypothesis:
        """Generate improvement hypothesis from a group of similar patterns"""
        
        # Aggregate information from the group
        total_frequency = sum(p.frequency for p in pattern_group)
        domains = set()
        for p in pattern_group:
            domains.update(p.affected_domains)
            
        # Determine severity
        severities = [p.severity for p in pattern_group]
        max_severity = max(severities, key=lambda x: ["minor", "moderate", "critical"].index(x))
        
        # Create hypothesis
        pattern_type = pattern_group[0].pattern_type
        root_cause = pattern_group[0].root_cause
        
        hypothesis = ImprovementHypothesis(
            title=f"Improve {pattern_type} handling for {', '.join(domains)}",
            description=f"Address root cause: {root_cause}",
            failure_patterns_addressed=[p.root_cause for p in pattern_group],
            implementation_approach=self._suggest_implementation(pattern_type, root_cause),
            estimated_effort=self._estimate_effort(pattern_type),
            expected_roi=self._calculate_roi(total_frequency, max_severity),
            priority=self._calculate_priority(total_frequency, max_severity)
        )
        
        return hypothesis
    
    def _suggest_implementation(self, pattern_type: str, root_cause: str) -> str:
        """Suggest implementation approach based on pattern type"""
        
        suggestions = {
            "comprehension": "Enhance prompt engineering and add clarification strategies",
            "knowledge": "Create specialized knowledge base or fine-tune on domain data",
            "reasoning": "Implement chain-of-thought prompting or reasoning modules",
            "execution": "Add new tools or expand existing tool capabilities"
        }
        
        return suggestions.get(pattern_type, "Conduct further analysis")
    
    def _estimate_effort(self, pattern_type: str) -> str:
        """Estimate implementation effort"""
        
        effort_map = {
            "comprehension": "low",  # Usually prompt changes
            "knowledge": "medium",   # Knowledge base creation
            "reasoning": "high",     # Complex system changes
            "execution": "medium"    # Tool development
        }
        
        return effort_map.get(pattern_type, "medium")
    
    def _calculate_roi(self, frequency: int, severity: str) -> float:
        """Calculate expected ROI based on frequency and severity"""
        
        severity_weights = {"minor": 1.0, "moderate": 3.0, "critical": 10.0}
        weight = severity_weights.get(severity, 1.0)
        
        # Simple ROI calculation
        return frequency * weight
    
    def _calculate_priority(self, frequency: int, severity: str) -> int:
        """Calculate priority score (1-10)"""
        
        roi = self._calculate_roi(frequency, severity)
        
        if roi > 100:
            return 10
        elif roi > 50:
            return 8
        elif roi > 20:
            return 6
        elif roi > 10:
            return 4
        else:
            return 2
    
    # Helper methods for parsing summaries
    def _extract_pattern_type(self, summary: str) -> str:
        if "comprehension failure" in summary.lower():
            return "comprehension"
        elif "knowledge limitation" in summary.lower():
            return "knowledge"
        elif "reasoning failure" in summary.lower():
            return "reasoning"
        elif "execution failure" in summary.lower() or "tool limitation" in summary.lower():
            return "execution"
        return "unknown"
    
    def _extract_root_cause(self, summary: str) -> str:
        # In real implementation, would parse structured summary
        if "Root cause:" in summary:
            start = summary.find("Root cause:") + len("Root cause:")
            end = summary.find("\n", start)
            return summary[start:end].strip()
        return "Unknown root cause"
    
    def _extract_severity(self, summary: str) -> str:
        if "critical" in summary.lower():
            return "critical"
        elif "moderate" in summary.lower():
            return "moderate"
        else:
            return "minor"
    
    def _extract_domain(self, summary: str) -> str:
        # Extract domain from metadata section
        if "Domain:" in summary:
            start = summary.find("Domain:") + len("Domain:")
            end = summary.find("\n", start)
            domain = summary[start:end].strip()
            return domain.strip("[]")
        return "general"
    
    def _extract_improvement(self, summary: str) -> str:
        if "Would benefit from" in summary:
            start = summary.find("Would benefit from")
            end = summary.find("\n", start)
            return summary[start:end].strip()
        return "No specific improvement suggested"
    
    def _calculate_impact(self, summary: str) -> float:
        # Extract business impact and convert to score
        if "Business impact: high" in summary:
            return 10.0
        elif "Business impact: medium" in summary:
            return 5.0
        else:
            return 1.0


async def main():
    """Example usage of the analysis agent"""
    
    # This would use your actual retrieval client
    class MockRetrievalClient:
        async def search(self, query: str, top_k: int = 30) -> List[Dict[str, Any]]:
            # Mock results with V5 summary format
            return [
                {
                    "hash": "conv123",
                    "summary": """
                    FAILURE ANALYSIS:
                    - Root cause: AI failed to understand Docker networking concepts
                    - Failure pattern: comprehension failure
                    - User impact: User spent 30 minutes clarifying their setup
                    
                    INTERACTION DYNAMICS:
                    - Communication breakdowns: 3 rounds of clarification needed
                    - User frustration indicators: "This is the third time I'm explaining"
                    
                    METADATA FOR ANALYSIS:
                    - Domain: [technical/devops]
                    - Failure severity: [moderate]
                    - Business impact: [medium]
                    """
                },
                # More mock results...
            ]
    
    # Create agent and run analysis
    client = MockRetrievalClient()
    agent = AIAnalysisAgent(client)
    
    print("Running AI system analysis...")
    hypotheses = await agent.analyze_system_performance()
    
    # Display results
    print("\n=== IMPROVEMENT RECOMMENDATIONS ===\n")
    
    for i, hypothesis in enumerate(hypotheses[:5], 1):
        print(f"{i}. {hypothesis.title}")
        print(f"   Description: {hypothesis.description}")
        print(f"   Priority: {hypothesis.priority}/10")
        print(f"   Effort: {hypothesis.estimated_effort}")
        print(f"   Expected ROI: {hypothesis.expected_roi:.1f}")
        print(f"   Implementation: {hypothesis.implementation_approach}")
        print()
    
    # Save full report
    report = {
        "analysis_timestamp": "2024-01-15T10:00:00Z",
        "total_conversations_analyzed": 150,
        "improvement_hypotheses": [
            {
                "title": h.title,
                "description": h.description,
                "priority": h.priority,
                "effort": h.estimated_effort,
                "roi": h.expected_roi,
                "implementation": h.implementation_approach,
                "patterns_addressed": h.failure_patterns_addressed
            }
            for h in hypotheses
        ]
    }
    
    with open("improvement_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"Full report saved to improvement_report.json")


if __name__ == "__main__":
    asyncio.run(main())