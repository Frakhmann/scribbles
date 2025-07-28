from sqlalchemy.orm import Session
from app.models.report import Report
from app.schemas.report import ReportCreate

def create_report(db: Session, report_in: ReportCreate, user_id: int):
    report = Report(
        post_id=report_in.post_id,
        user_id=user_id,
        reason=report_in.reason,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def get_reports(db: Session, skip=0, limit=100):
    return db.query(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
