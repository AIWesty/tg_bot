from fpdf import FPDF
from datetime import datetime
from aiogram import Bot
from aiogram.types import FSInputFile  # Используем конкретную реализацию
from typing import List
import os
import csv

async def generate_daily_report(bot: Bot, admin_ids: List[int]) -> None:
    """Генерирует ежедневный отчет в PDF и отправляет его администраторам."""
    try:
        #Создаем PDF документ
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        #Формируем текущую дату для отчета
        today = datetime.now().strftime("%Y-%m-%d")
        pdf.cell(200, 10, text=f"📊 Отчет за {today}", ln=True, align="C")
        
        #сбор статы пользователей
        try:
            with open("data/users.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                user_count = sum(1 for row in reader)
        except FileNotFoundError:
            user_count = 0
            pdf.cell(200, 10, text="⚠ Файл с пользователями не найден", ln=True)
        
        pdf.cell(200, 10, text=f"👥 Пользователей: {user_count}", ln=True)
        
        #Сохраняем отчет
        os.makedirs("data/reports", exist_ok=True)  # Создаем папку, если ее нет
        report_path = f"data/reports/report_{today}.pdf"
        pdf.output(report_path)
        
        #Отправляем администраторам
        for admin_id in admin_ids:
            try:
                # Используем FSInputFile для файла в файловой системе
                input_file = FSInputFile(report_path)
                await bot.send_document(
                    chat_id=admin_id,
                    document=input_file,
                    caption=f"📅 Отчет за {today}"
                )
            except Exception as e:
                print(f"Ошибка отправки отчета администратору {admin_id}: {e}")
                
    except Exception as e:
        print(f"Критическая ошибка при генерации отчета: {e}")