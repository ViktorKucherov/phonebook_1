"""
Телефонный справочник
Консольное приложение для управления контактами
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class Contact:
    """Класс для представления контакта"""
    
    def __init__(self, name: str, phone: str, comment: str = "", contact_id: Optional[int] = None):
        self.id = contact_id
        self.name = name.strip()
        self.phone = phone.strip()
        self.comment = comment.strip()
    
    def to_dict(self) -> Dict:
        """Преобразует контакт в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'comment': self.comment
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Contact':
        """Создает контакт из словаря"""
        # Проверяем наличие обязательных полей
        if 'name' not in data or 'phone' not in data:
            raise ValueError(f"Контакт должен содержать поля 'name' и 'phone'. Получено: {list(data.keys())}")
        return cls(
            name=data['name'],
            phone=data['phone'],
            comment=data.get('comment', ''),
            contact_id=data.get('id')
        )
    
    def __str__(self) -> str:
        id_str = str(self.id) if self.id is not None else "Нет"
        return f"ID: {id_str} | {self.name} | {self.phone} | {self.comment}"
    
    def __repr__(self) -> str:
        return self.__str__()


class PhoneBook:
    """Класс для работы с телефонным справочником"""
    
    def __init__(self, filename: str = "phonebook.json"):
        self.filename = filename
        self.contacts: List[Contact] = []
        self.next_id = 1
        self.modified = False
    
    def load_from_file(self) -> bool:
        """Загружает контакты из файла"""
        try:
            if not os.path.exists(self.filename):
                print(f"Файл {self.filename} не найден. Создан новый справочник.")
                return True
            
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Загружаем контакты с обработкой ошибок валидации
            contacts_list = []
            for i, contact_data in enumerate(data.get('contacts', [])):
                try:
                    contacts_list.append(Contact.from_dict(contact_data))
                except (ValueError, KeyError) as e:
                    print(f"Предупреждение: Пропущен некорректный контакт #{i+1}: {e}")
                    continue
            
            self.contacts = contacts_list
            
            # Определяем следующий ID и присваиваем ID контактам без него
            modified_by_id_assignment = False
            if self.contacts:
                # Находим максимальный ID среди контактов, у которых есть ID
                ids_with_values = [contact.id for contact in self.contacts if contact.id is not None]
                if ids_with_values:
                    self.next_id = max(ids_with_values) + 1
                else:
                    self.next_id = 1
                
                # Присваиваем ID всем контактам, у которых его нет
                for contact in self.contacts:
                    if contact.id is None:
                        contact.id = self.next_id
                        self.next_id += 1
                        modified_by_id_assignment = True
            else:
                self.next_id = 1
            
            # Не сбрасываем modified, если мы только что добавили ID контактам
            if not modified_by_id_assignment:
                self.modified = False
            print(f"Загружено контактов: {len(self.contacts)}")
            return True
            
        except json.JSONDecodeError:
            print(f"Ошибка: Файл {self.filename} поврежден или имеет неверный формат.")
            return False
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return False
    
    def save_to_file(self) -> bool:
        """Сохраняет контакты в файл"""
        try:
            data = {
                'contacts': [contact.to_dict() for contact in self.contacts],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.modified = False
            print(f"Справочник сохранен в файл {self.filename}")
            return True
            
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            return False
    
    def show_all_contacts(self):
        """Показывает все контакты"""
        if not self.contacts:
            print("Справочник пуст.")
            return
        
        print("\n" + "="*60)
        print("ВСЕ КОНТАКТЫ")
        print("="*60)
        for contact in self.contacts:
            print(contact)
        print("="*60 + "\n")
    
    def create_contact(self):
        """Создает новый контакт"""
        try:
            print("\nСоздание нового контакта")
            print("-" * 30)
            
            name = input("Введите имя: ").strip()
            if not name:
                print("Ошибка: Имя не может быть пустым.")
                return
            
            phone = input("Введите телефон: ").strip()
            if not phone:
                print("Ошибка: Телефон не может быть пустым.")
                return
            
            # Простая валидация телефона
            if not self._validate_phone(phone):
                print("Предупреждение: Телефон может содержать только цифры, пробелы, +, -, (, )")
            
            comment = input("Введите комментарий (необязательно): ").strip()
            
            contact = Contact(
                name=name,
                phone=phone,
                comment=comment,
                contact_id=self.next_id
            )
            
            self.contacts.append(contact)
            self.next_id += 1
            self.modified = True
            
            print(f"\nКонтакт '{name}' успешно создан с ID {contact.id}")
            
        except KeyboardInterrupt:
            print("\n\nОперация отменена.")
        except Exception as e:
            print(f"Ошибка при создании контакта: {e}")
    
    def find_contact(self):
        """Поиск контакта"""
        if not self.contacts:
            print("Справочник пуст.")
            return
        
        try:
            print("\nПоиск контакта")
            print("-" * 30)
            print("1. Поиск по имени")
            print("2. Поиск по телефону")
            print("3. Поиск по комментарию")
            print("4. Общий поиск (по всем полям)")
            
            choice = input("\nВыберите тип поиска (1-4): ").strip()
            search_term = input("Введите поисковый запрос: ").strip().lower()
            
            if not search_term:
                print("Поисковый запрос не может быть пустым.")
                return
            
            results = []
            
            if choice == "1":
                results = [c for c in self.contacts if search_term in c.name.lower()]
            elif choice == "2":
                # Поиск по телефону без учета регистра (для консистентности)
                results = [c for c in self.contacts if search_term in c.phone.lower()]
            elif choice == "3":
                results = [c for c in self.contacts if search_term in c.comment.lower()]
            elif choice == "4":
                results = [c for c in self.contacts 
                          if search_term in c.name.lower() 
                          or search_term in c.phone.lower()
                          or search_term in c.comment.lower()]
            else:
                print("Неверный выбор. Используется общий поиск.")
                results = [c for c in self.contacts 
                          if search_term in c.name.lower() 
                          or search_term in c.phone.lower()
                          or search_term in c.comment.lower()]
            
            if results:
                print(f"\nНайдено контактов: {len(results)}")
                print("="*60)
                for contact in results:
                    print(contact)
                print("="*60 + "\n")
            else:
                print("Контакты не найдены.")
                
        except KeyboardInterrupt:
            print("\n\nОперация отменена.")
        except Exception as e:
            print(f"Ошибка при поиске: {e}")
    
    def edit_contact(self):
        """Редактирование контакта"""
        if not self.contacts:
            print("Справочник пуст.")
            return
        
        try:
            contact_id = input("\nВведите ID контакта для редактирования: ").strip()
            
            if not contact_id.isdigit():
                print("Ошибка: ID должен быть числом.")
                return
            
            contact_id = int(contact_id)
            contact = self._find_by_id(contact_id)
            
            if not contact:
                print(f"Контакт с ID {contact_id} не найден.")
                return
            
            print(f"\nТекущие данные контакта:")
            print(contact)
            print("\nВведите новые данные (оставьте пустым, чтобы оставить без изменений):")
            
            new_name = input(f"Имя [{contact.name}]: ").strip()
            if new_name:
                contact.name = new_name
            
            new_phone = input(f"Телефон [{contact.phone}]: ").strip()
            if new_phone:
                if not self._validate_phone(new_phone):
                    print("Предупреждение: Телефон может содержать только цифры, пробелы, +, -, (, )")
                contact.phone = new_phone
            
            new_comment = input(f"Комментарий [{contact.comment}]: ").strip()
            if new_comment:
                contact.comment = new_comment
            
            self.modified = True
            print(f"\nКонтакт с ID {contact_id} успешно изменен.")
            
        except KeyboardInterrupt:
            print("\n\nОперация отменена.")
        except Exception as e:
            print(f"Ошибка при редактировании контакта: {e}")
    
    def delete_contact(self):
        """Удаление контакта"""
        if not self.contacts:
            print("Справочник пуст.")
            return
        
        try:
            contact_id = input("\nВведите ID контакта для удаления: ").strip()
            
            if not contact_id.isdigit():
                print("Ошибка: ID должен быть числом.")
                return
            
            contact_id = int(contact_id)
            contact = self._find_by_id(contact_id)
            
            if not contact:
                print(f"Контакт с ID {contact_id} не найден.")
                return
            
            print(f"\nКонтакт для удаления:")
            print(contact)
            
            confirm = input("\nВы уверены? (да/нет): ").strip().lower()
            
            if confirm in ['да', 'yes', 'y', 'д']:
                self.contacts.remove(contact)
                self.modified = True
                print(f"Контакт с ID {contact_id} успешно удален.")
            else:
                print("Удаление отменено.")
                
        except KeyboardInterrupt:
            print("\n\nОперация отменена.")
        except Exception as e:
            print(f"Ошибка при удалении контакта: {e}")
    
    def _find_by_id(self, contact_id: int) -> Optional[Contact]:
        """Находит контакт по ID"""
        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        return None
    
    @staticmethod
    def _validate_phone(phone: str) -> bool:
        """Проверяет формат телефона"""
        allowed_chars = set('0123456789+-() ')
        return all(c in allowed_chars for c in phone)
    
    def has_unsaved_changes(self) -> bool:
        """Проверяет наличие несохраненных изменений"""
        return self.modified


def show_menu():
    """Отображает главное меню"""
    print("\n" + "="*60)
    print("ТЕЛЕФОННЫЙ СПРАВОЧНИК")
    print("="*60)
    print("1. Открыть файл")
    print("2. Сохранить файл")
    print("3. Показать все контакты")
    print("4. Создать контакт")
    print("5. Найти контакт")
    print("6. Изменить контакт")
    print("7. Удалить контакт")
    print("8. Выход")
    print("="*60)


def main():
    """Главная функция приложения"""
    phonebook = PhoneBook()
    
    print("Добро пожаловать в телефонный справочник!")
    
    # Пытаемся автоматически загрузить файл по умолчанию
    if os.path.exists(phonebook.filename):
        print(f"\nНайден файл {phonebook.filename}. Загружаю...")
        phonebook.load_from_file()
    else:
        print(f"\nФайл {phonebook.filename} не найден. Начните работу с пустым справочником или загрузите файл через меню.")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nВыберите действие (1-8): ").strip()
            
            if choice == "1":
                filename = input("Введите имя файла для загрузки: ").strip()
                if filename:
                    phonebook.filename = filename
                phonebook.load_from_file()
            
            elif choice == "2":
                phonebook.save_to_file()
            
            elif choice == "3":
                phonebook.show_all_contacts()
            
            elif choice == "4":
                phonebook.create_contact()
            
            elif choice == "5":
                phonebook.find_contact()
            
            elif choice == "6":
                phonebook.edit_contact()
            
            elif choice == "7":
                phonebook.delete_contact()
            
            elif choice == "8":
                if phonebook.has_unsaved_changes():
                    try:
                        save = input("\nУ вас есть несохраненные изменения. Сохранить? (да/нет): ").strip().lower()
                        if save in ['да', 'yes', 'y', 'д']:
                            phonebook.save_to_file()
                    except (EOFError, KeyboardInterrupt):
                        print("\nИзменения не сохранены.")
                print("\nДо свидания!")
                break
            
            else:
                print("Неверный выбор. Пожалуйста, выберите действие от 1 до 8.")
        
        except KeyboardInterrupt:
            print("\n\nПрерывание программы...")
            if phonebook.has_unsaved_changes():
                try:
                    save = input("У вас есть несохраненные изменения. Сохранить? (да/нет): ").strip().lower()
                    if save in ['да', 'yes', 'y', 'д']:
                        phonebook.save_to_file()
                except (EOFError, KeyboardInterrupt):
                    print("\nИзменения не сохранены.")
            print("До свидания!")
            break
        except EOFError:
            print("\n\nОшибка: Невозможно получить ввод от пользователя.")
            print("Программа требует интерактивного режима работы.")
            if phonebook.has_unsaved_changes():
                print("Внимание: У вас есть несохраненные изменения!")
            print("До свидания!")
            break
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            try:
                input("Нажмите Enter для продолжения...")
            except (EOFError, KeyboardInterrupt):
                print("\nЗавершение работы...")
                break


if __name__ == "__main__":
    main()


