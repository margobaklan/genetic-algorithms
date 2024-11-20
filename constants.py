import csv

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
PERIODS_PER_DAY = 5
WEEKS = 14  # Number of weeks in a semester

# Time periods mapping (Period number to actual times)
PERIOD_TIMES = {
    1: ('8:40', '10:15'),
    2: ('10:35', '12:10'),
    3: ('12:20', '13:55'),
    4: ('14:05', '15:40'),
    5: ('15:45', '17:20')
}

NUM_GROUPS = 2
NUM_SUBGROUPS = 2
NUM_ROOMS = 6

GROUP_PREFIX = "MI"
SUBJECT_NAMES = [
    'Алгоритми', 'Нейронні мережі', 'Інтелектуальні системи',
    'Теорія прийняття рішень', 'Інформаційні технології',
    'Комп\'ютерна лінгвістика', 'Статистичне моделювання'
]
LECTURER_NAMES = [
    'Бобиль', 'Закала', 'Вергунова', 'Тарануха',
    'Пашко', 'Зінько', 'Ткаченко', 
    'Терещенко', 'Мащенко'
]

LECTURER_SUBJECTS = {
    'Бобиль': [{'subject_name': 'Нейронні мережі', 'class_type': 'Lecture'},
               {'subject_name': 'Нейронні мережі', 'class_type': 'Lab'}],
    'Закала': [{'subject_name': 'Нейронні мережі', 'class_type': 'Lab'}],
    'Вергунова': [{'subject_name': 'Алгоритми', 'class_type': 'Lecture'},
                  {'subject_name': 'Алгоритми', 'class_type': 'Lab'}],
    'Тарануха': [{'subject_name': 'Комп\'ютерна лінгвістика', 'class_type': 'Lecture'},
                 {'subject_name': 'Комп\'ютерна лінгвістика', 'class_type': 'Lecture'},
                 {'subject_name': 'Інтелектуальні системи', 'class_type': 'Lab'}],
    'Мисечко': [{'subject_name': 'Інтелектуальні системи', 'class_type': 'Lab'}],
    'Федорус': [{'subject_name': 'Інтелектуальні системи', 'class_type': 'Lab'}],
    'Пашко': [{'subject_name': 'Статистичне моделювання', 'class_type': 'Lecture'}],                                 
    'Мащенко': [{'subject_name': 'Теорія прийняття рішень', 'class_type': 'Lecture'}],
    'Зінько': [{'subject_name': 'Теорія прийняття рішень', 'class_type': 'Lecture'}],
    'Ткаченко': [{'subject_name': 'Інформаційні технології', 'class_type': 'Lecture'}],
    'Терещенко': [{'subject_name': 'Інформаційні технології', 'class_type': 'Lab'}],
    'Свистунов': [{'subject_name': 'Інформаційні технології', 'class_type': 'Lab'}],
}

