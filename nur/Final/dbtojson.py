from app import app, db, User, Talep
from flask_login import UserMixin
from datetime import datetime
import os
import json

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///talep.db'

# Eğer modeller app.py içinde tanımlıysa burada tekrar tanımlamaya gerek yok,
# sadece import etmen yeterli. Eğer burada tanımlıysa aşağıdaki tanımlar yeterli.

def export_data_to_json():
    with app.app_context():
        # Eğer tablolar yoksa oluştur
        db.create_all()

        users = User.query.all()
        talepler = Talep.query.all()

        data = {
            "users": [   # Burada anahtar string olmalı
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "is_admin": u.is_admin,
                } for u in users
            ],
            "talepler": [   # Burada da string olmalı
                {
                    "id": t.id,
                    "subject": t.subject,
                    "description": t.description,
                    "priority": t.priority,
                    "tags": t.tags,
                    "reply": t.reply,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "kullanici_id": t.kullanici_id,
                } for t in talepler
            ]
        }

        file_path = os.path.join(os.path.dirname(__file__), "veri_aktarimi.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"JSON dosyası başarıyla oluşturuldu: {file_path}")


if __name__ == "__main__":
    export_data_to_json()
