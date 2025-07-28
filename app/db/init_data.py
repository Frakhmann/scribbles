from app.db.session import SessionLocal
from app.models.university import University
from app.models.section import Section

universities_data = [
    {"name": "AMITY university Tashkent", "email_domain": "amity.uz"},
    {"name": "Bucheon university in Tashkent", "email_domain": "bucheon.uz"},
    {"name": "INHA university in Tashkent", "email_domain": "inha.uz"},
    {"name": "Japan Digital University", "email_domain": "jdu.uz"},
    {"name": "Webster university in Tashkent", "email_domain": "webster.edu"},
    {"name": "British Management University", "email_domain": "bmu-edu.uz"},
    {"name": "Westminster university", "email_domain": "students.wiut.uz"},
    {"name": "MDIS in Tashkent", "email_domain": "mdis.uz"},
    {"name": "Туринский политехнический университет", "email_domain": "studenti.polito.it"},
]

sections = [
    "Новости",
    "Аренда жилья",
    "Вакансии / стажировки",
    "Мероприятия",
    "Флудилка",
    "Общая лента"
]

def init_universities_and_sections():
    db = SessionLocal()
    for uni_data in universities_data:
        uni = db.query(University).filter_by(email_domain=uni_data["email_domain"]).first()
        if not uni:
            uni = University(**uni_data)
            db.add(uni)
            db.commit()
            db.refresh(uni)

        for name in sections:
            exists = db.query(Section).filter_by(name=name, university_id=uni.id).first()
            if not exists:
                section = Section(name=name, university_id=uni.id)
                db.add(section)
    db.commit()
    db.close()
