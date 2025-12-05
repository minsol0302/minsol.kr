"""
Titanic 데이터셋 모델 클래스
Passenger 정보를 담는 모델
"""


class TitanicPassenger:
    """Titanic 승객 정보를 담는 모델 클래스"""

    def __init__(self):
        self._passenger_id = None
        self._survived = None
        self._pclass = None
        self._name = None
        self._sex = None
        self._age = None
        self._sib_sp = None
        self._parch = None
        self._ticket = None
        self._fare = None
        self._cabin = None
        self._embarked = None

    # PassengerId
    @property
    def passenger_id(self):
        """PassengerId getter"""
        return self._passenger_id

    @passenger_id.setter
    def passenger_id(self, value):
        """PassengerId setter"""
        self._passenger_id = value

    # Survived
    @property
    def survived(self):
        """Survived getter (0: 사망, 1: 생존)"""
        return self._survived

    @survived.setter
    def survived(self, value):
        """Survived setter"""
        self._survived = value

    # Pclass
    @property
    def pclass(self):
        """Pclass getter (1: 1등급, 2: 2등급, 3: 3등급)"""
        return self._pclass

    @pclass.setter
    def pclass(self, value):
        """Pclass setter"""
        self._pclass = value

    # Name
    @property
    def name(self):
        """Name getter"""
        return self._name

    @name.setter
    def name(self, value):
        """Name setter"""
        self._name = value

    # Sex
    @property
    def sex(self):
        """Sex getter (male, female)"""
        return self._sex

    @sex.setter
    def sex(self, value):
        """Sex setter"""
        self._sex = value

    # Age
    @property
    def age(self):
        """Age getter"""
        return self._age

    @age.setter
    def age(self, value):
        """Age setter"""
        self._age = value

    # SibSp
    @property
    def sib_sp(self):
        """SibSp getter (형제/배우자 수)"""
        return self._sib_sp

    @sib_sp.setter
    def sib_sp(self, value):
        """SibSp setter"""
        self._sib_sp = value

    # Parch
    @property
    def parch(self):
        """Parch getter (부모/자녀 수)"""
        return self._parch

    @parch.setter
    def parch(self, value):
        """Parch setter"""
        self._parch = value

    # Ticket
    @property
    def ticket(self):
        """Ticket getter"""
        return self._ticket

    @ticket.setter
    def ticket(self, value):
        """Ticket setter"""
        self._ticket = value

    # Fare
    @property
    def fare(self):
        """Fare getter (요금)"""
        return self._fare

    @fare.setter
    def fare(self, value):
        """Fare setter"""
        self._fare = value

    # Cabin
    @property
    def cabin(self):
        """Cabin getter"""
        return self._cabin

    @cabin.setter
    def cabin(self, value):
        """Cabin setter"""
        self._cabin = value

    # Embarked
    @property
    def embarked(self):
        """Embarked getter (S: Southampton, C: Cherbourg, Q: Queenstown)"""
        return self._embarked

    @embarked.setter
    def embarked(self, value):
        """Embarked setter"""
        self._embarked = value

    def __repr__(self):
        """문자열 표현"""
        return (f"TitanicPassenger(passenger_id={self._passenger_id}, "
                f"survived={self._survived}, pclass={self._pclass}, "
                f"name='{self._name}', sex='{self._sex}', age={self._age})")

    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'passenger_id': self._passenger_id,
            'survived': self._survived,
            'pclass': self._pclass,
            'name': self._name,
            'sex': self._sex,
            'age': self._age,
            'sib_sp': self._sib_sp,
            'parch': self._parch,
            'ticket': self._ticket,
            'fare': self._fare,
            'cabin': self._cabin,
            'embarked': self._embarked
        }

