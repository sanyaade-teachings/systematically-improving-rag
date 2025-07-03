"""
Database utilities using SQLModel
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from sqlmodel import SQLModel, Session, create_engine, select, Field
from pydantic import BaseModel
from core.synthetic_queries import SearchQueries


# SQLModel table definitions
class Conversation(SQLModel, table=True):
    conversation_hash: str = Field(primary_key=True)
    text: str
    conversation_full: str
    timestamp: Optional[datetime] = None
    language: str = "English"
    country: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Question(SQLModel, table=True):
    id: str = Field(primary_key=True)
    conversation_hash: str = Field(foreign_key="conversation.conversation_hash")
    version: str
    question: str
    experiment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Summary(SQLModel, table=True):
    id: str = Field(primary_key=True)
    conversation_hash: str = Field(foreign_key="conversation.conversation_hash")
    technique: str
    summary: str
    experiment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Evaluation(SQLModel, table=True):
    id: str = Field(primary_key=True)
    question_id: str = Field(foreign_key="question.id")
    summary_id: Optional[str] = Field(foreign_key="summary.id", default=None)
    metric_name: str
    metric_value: float
    experiment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


def get_engine(db_path: Path):
    """Get SQLModel engine for database"""
    return create_engine(f"sqlite:///{db_path}")


def clear_database(db_path: Path) -> None:
    """Clear SQLite database"""
    engine = get_engine(db_path)
    SQLModel.metadata.drop_all(engine)
    setup_database(db_path)


def setup_database(db_path: Path) -> None:
    """Set up SQLite database with all required tables using SQLModel"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)


def load_conversations_to_sqlite(
    conversations: List[Dict[str, Any]], db_path: Path
) -> int:
    """Load conversations into SQLite database"""
    engine = get_engine(db_path)
    inserted = 0

    with Session(engine) as session:
        for conv in conversations:
            try:
                conversation = Conversation(
                    conversation_hash=conv["conversation_hash"],
                    text=conv["text"],  # Remove truncation
                    conversation_full=conv["conversation_full"],
                    timestamp=conv.get("timestamp"),
                    language=conv.get("language", "English"),
                    country=conv.get("country"),
                )
                session.add(conversation)
                session.commit()
                inserted += 1
            except Exception as e:
                print(
                    f"Error inserting conversation {conv.get('conversation_hash')}: {e}"
                )
                session.rollback()
                continue

    return inserted


def save_questions_to_sqlite(questions: List[SearchQueries], db_path: Path) -> int:
    """Save generated questions to SQLite"""
    engine = get_engine(db_path)
    inserted = 0

    with Session(engine) as session:
        for q in questions:
            try:
                question = Question(
                    id=q["id"],
                    conversation_hash=q["conversation_hash"],
                    version=q["version"],
                    question=q["question"],
                    experiment_id=q.get("experiment_id"),
                )
                session.add(question)
                session.commit()
                inserted += 1
            except Exception as e:
                print(f"Error inserting question {q.get('id')}: {e}")
                session.rollback()
                continue

    return inserted


def save_summaries_to_sqlite(summaries: List[Dict[str, Any]], db_path: Path) -> int:
    """Save generated summaries to SQLite"""
    engine = get_engine(db_path)
    inserted = 0

    with Session(engine) as session:
        for s in summaries:
            try:
                summary = Summary(
                    id=s["id"],
                    conversation_hash=s["conversation_hash"],
                    technique=s["technique"],
                    summary=s["summary"],
                    experiment_id=s.get("experiment_id"),
                )
                session.add(summary)
                session.commit()
                inserted += 1
            except Exception as e:
                print(f"Error inserting summary {s.get('id')}: {e}")
                session.rollback()
                continue

    return inserted


def save_evaluations_to_sqlite(evaluations: List[Dict[str, Any]], db_path: Path) -> int:
    """Save evaluation results to SQLite"""
    engine = get_engine(db_path)
    inserted = 0

    with Session(engine) as session:
        for eval_result in evaluations:
            try:
                evaluation = Evaluation(
                    id=eval_result["id"],
                    question_id=eval_result["question_id"],
                    summary_id=eval_result.get("summary_id"),
                    metric_name=eval_result["metric_name"],
                    metric_value=eval_result["metric_value"],
                    experiment_id=eval_result.get("experiment_id"),
                )
                session.add(evaluation)
                session.commit()
                inserted += 1
            except Exception as e:
                print(f"Error inserting evaluation {eval_result.get('id')}: {e}")
                session.rollback()
                continue

    return inserted


def get_conversations_by_hashes(
    conversation_hashes: List[str], db_path: Path
) -> List[Dict[str, Any]]:
    """Get conversations by their hashes"""
    engine = get_engine(db_path)

    with Session(engine) as session:
        statement = select(Conversation).where(
            Conversation.conversation_hash.in_(conversation_hashes)
        )
        conversations = session.exec(statement).all()
        return [conv.dict() for conv in conversations]


def get_questions_by_technique(
    technique: str, db_path: Path, experiment_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get questions by technique"""
    engine = get_engine(db_path)

    with Session(engine) as session:
        statement = select(Question).where(Question.technique == technique)
        if experiment_id:
            statement = statement.where(Question.experiment_id == experiment_id)

        questions = session.exec(statement).all()
        return [q.dict() for q in questions]


def get_summaries_by_technique(
    technique: str, db_path: Path, experiment_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get summaries by technique"""
    engine = get_engine(db_path)

    with Session(engine) as session:
        statement = select(Summary).where(Summary.technique == technique)
        if experiment_id:
            statement = statement.where(Summary.experiment_id == experiment_id)

        summaries = session.exec(statement).all()
        return [s.dict() for s in summaries]


def get_evaluation_results(experiment_id: str, db_path: Path) -> List[Dict[str, Any]]:
    """Get evaluation results for an experiment"""
    engine = get_engine(db_path)

    with Session(engine) as session:
        statement = (
            select(Evaluation, Question, Summary)
            .join(Question, Evaluation.question_id == Question.id)
            .outerjoin(Summary, Evaluation.summary_id == Summary.id)
            .where(Evaluation.experiment_id == experiment_id)
        )

        results = session.exec(statement).all()
        return [
            {
                **eval_result.dict(),
                "question_version": question.version,
                "summary_version": summary.version if summary else None,
            }
            for eval_result, question, summary in results
        ]


def get_processed_question_hashes(version: str, db_path: Path, experiment_id: Optional[str] = None) -> List[str]:
    """Get conversation hashes that already have questions generated for a specific version"""
    engine = get_engine(db_path)
    
    with Session(engine) as session:
        statement = select(Question.conversation_hash).where(Question.version == version)
        if experiment_id:
            statement = statement.where(Question.experiment_id == experiment_id)
        
        return list(session.exec(statement).all())


def get_processed_summary_hashes(technique: str, db_path: Path, experiment_id: Optional[str] = None) -> List[str]:
    """Get conversation hashes that already have summaries generated for a specific technique"""
    engine = get_engine(db_path)
    
    with Session(engine) as session:
        statement = select(Summary.conversation_hash).where(Summary.technique == technique)
        if experiment_id:
            statement = statement.where(Summary.experiment_id == experiment_id)
        
        return list(session.exec(statement).all())


def filter_unprocessed_hashes(conversation_hashes: List[str], version: str, db_path: Path, 
                            experiment_id: Optional[str] = None, is_summary: bool = False) -> List[str]:
    """Filter conversation hashes to only include unprocessed ones"""
    if is_summary:
        processed_hashes = set(get_processed_summary_hashes(version, db_path, experiment_id))
    else:
        processed_hashes = set(get_processed_question_hashes(version, db_path, experiment_id))
    
    return [h for h in conversation_hashes if h not in processed_hashes]


def get_database_stats(db_path: Path) -> Dict[str, int]:
    """Get database statistics"""
    if not db_path.exists():
        return {}

    engine = get_engine(db_path)
    stats = {}

    with Session(engine) as session:
        from sqlmodel import func
        stats["conversations"] = session.exec(select(func.count(Conversation.conversation_hash))).one()
        stats["questions"] = session.exec(select(func.count(Question.id))).one()
        stats["summaries"] = session.exec(select(func.count(Summary.id))).one()
        stats["evaluations"] = session.exec(select(func.count(Evaluation.id))).one()

    return stats
