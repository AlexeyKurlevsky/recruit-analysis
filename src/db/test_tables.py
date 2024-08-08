import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backup_tables import Coworkers, toggle_coworker_activity, Base

TEST_DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(TEST_DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class TestCoworkerActivityToggle(unittest.TestCase):

    def setUp(self):
        """Настройка тестовой базы данных перед каждым тестом."""
        self.session = Session()
        self.coworker1 = Coworkers(name="John Doe", type="recruiter")
        self.coworker2 = Coworkers(name="Jane Doe", type="manager")
        self.session.add(self.coworker1)
        self.session.add(self.coworker2)
        self.session.commit()

    def tearDown(self):
        """Удаление данных после каждого теста."""
        self.session.query(Coworkers).delete()
        self.session.commit()
        self.session.close()

    def test_toggle_coworker_activity_to_inactive(self):
        """Тест переключения статуса активности сотрудника на неактивный."""
        toggle_coworker_activity(self.coworker1.id)
        updated_coworker = self.session.query(Coworkers).get(self.coworker1.id)
        self.assertFalse(updated_coworker.is_active)

    def test_toggle_coworker_activity_to_active(self):
        """Тест переключения статуса активности сотрудника на активный."""
        toggle_coworker_activity(self.coworker2.id)
        toggle_coworker_activity(self.coworker2.id)
        updated_coworker = self.session.query(Coworkers).get(self.coworker2.id)
        self.assertTrue(updated_coworker.is_active)

    def test_toggle_coworker_activity_non_existent(self):
        """Тест для случая, когда сотрудник с указанным ID не существует."""
        with self.assertRaises(ValueError) as context:
            toggle_coworker_activity(999)  # Заменили на несуществующий ID
        self.assertEqual(str(context.exception), "No coworker found with ID 999")

    def test_toggle_coworker_activity_empty_id(self):
        """Тест для случая, когда ID сотрудника пустой (None)."""
        with self.assertRaises(TypeError):
            toggle_coworker_activity(None)


if __name__ == '__main__':
    unittest.main()



'''
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backup_tables import Coworkers, toggle_coworker_activity, Base

TEST_DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(TEST_DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class TestCoworkerActivityToggle(unittest.TestCase):

    def setUp(self):
        """Настройка тестовой базы данных перед каждым тестом."""
        self.session = Session()
        self.coworker1 = Coworkers(name="John Doe", type="recruiter")
        self.coworker2 = Coworkers(name="Jane Doe", type="manager")
        self.session.add(self.coworker1)
        self.session.add(self.coworker2)
        self.session.commit()

    def tearDown(self):
        """Удаление данных после каждого теста."""
        self.session.query(Coworkers).delete()
        self.session.commit()
        self.session.close()

    def test_toggle_coworker_activity_to_inactive(self):
        """Тест переключения статуса активности сотрудника на неактивный."""
        toggle_coworker_activity(self.coworker1.name)
        updated_coworker = self.session.query(Coworkers).filter_by(name=self.coworker1.name).one()
        self.assertFalse(updated_coworker.is_active)

    def test_toggle_coworker_activity_to_active(self):
        """Тест переключения статуса активности сотрудника на активный."""
        toggle_coworker_activity(self.coworker2.name)
        toggle_coworker_activity(self.coworker2.name)
        updated_coworker = self.session.query(Coworkers).filter_by(name=self.coworker2.name).one()
        self.assertTrue(updated_coworker.is_active)

    def test_toggle_coworker_activity_non_existent(self):
        """Тест для случая, когда сотрудник с указанным именем не существует."""
        with self.assertRaises(ValueError) as context:
            toggle_coworker_activity("Non Existent")
        self.assertEqual(str(context.exception), "No coworker found with name Non Existent")

    def test_toggle_coworker_activity_empty_name(self):
        """Тест для случая, когда имя сотрудника пустое."""
        with self.assertRaises(ValueError) as context:
            toggle_coworker_activity("")
        self.assertEqual(str(context.exception), "No coworker found with name ")


if __name__ == '__main__':
    unittest.main()
'''