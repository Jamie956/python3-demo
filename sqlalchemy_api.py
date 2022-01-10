from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# https://www.jianshu.com/p/0ad18fdd7eed

def getEngin():
    return create_engine('mysql+pymysql://root:root@localhost/db2019', echo=True)


def create_table_by_sql(engine):
    sql_create_table = '''create table student(
        id int not null primary key,
        name varchar(50),
        age int,
        address varchar(100));
    '''

    conn = engine.connect()
    conn.execute(sql_create_table)


def create_table(engine):
    metadata = MetaData(engine)

    Table('student', metadata,
          Column('id', Integer, primary_key=True),
          Column('name', String(50), ),
          Column('age', Integer),
          Column('address', String(10)),
          )

    metadata.create_all(engine)


def add_data():
    engine = getEngin()
    DBsession = sessionmaker(bind=engine)
    session = DBsession()

    Base = declarative_base()

    class Student(Base):
        __tablename__ = 'student'
        id = Column(Integer, primary_key=True)
        name = Column(String(100))
        age = Column(Integer)
        address = Column(String(100))

    student1 = Student(id=1001, name='ling', age=25, address="beijing")
    student2 = Student(id=1002, name='molin', age=18, address="jiangxi")
    student3 = Student(id=1003, name='karl', age=16, address="suzhou")

    session.add_all([student1, student2, student3])
    session.commit()
    session.close()


def query():
    Base = declarative_base()

    class Student(Base):
        __tablename__ = 'student'
        id = Column(Integer, primary_key=True)
        name = Column(String(50))
        age = Column(Integer)
        address = Column(String(100))

    engine = getEngin()
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    my_stdent = session.query(Student).filter_by(name="ling").first()
    print('===============')
    print(my_stdent.id, my_stdent.name, my_stdent.age, my_stdent.address)


if __name__ == '__main__':
    # create_table_by_sql(getEngin())
    # create_table(getEngin())
    # add_data()
    query()
