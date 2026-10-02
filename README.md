# LMS — O‘quv markazi

Django + Django REST Framework asosidagi LMS (learn_study arxitekturasi).

## Ishga tushirish

```bash
pip install -r requirements.txt
python manage.py migrate
python seed_data.py
python manage.py runserver
```

## Hisoblar

| Login | Parol | Rol |
|-------|-------|-----|
| admin | admin123 | Admin |
| teacher | teacher123 | O‘qituvchi |
| student | student123 | O‘quvchi |

## Modullar

- `accounts` — auth, profil, dashboard
- `courses` — kurs, modul, dars, guruh, xona
- `schedule` — haftalik jadval
- `attendance` — davomat + coin
- `normativ` — savollar, topshirish, baholash
- `coins` — tranzaksiya, do‘kon, reyting
- `news` — yangiliklar
- `api/` — DRF readonly endpoints (`/api/courses/`, `/api/groups/`, …)

## Havolalar

- Sayt: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- API: http://127.0.0.1:8000/api/
